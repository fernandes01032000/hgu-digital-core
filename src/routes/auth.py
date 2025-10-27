# -*- coding: utf-8 -*-
"""
Blueprint de Autenticação
Gerencia rotas de login, logout e setup inicial
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime

from src.core.database import (
    verificar_setup_inicial, salvar_configuracao, criar_setores_padrao,
    criar_usuario_admin, verificar_senha, registrar_log, get_db_connection
)
from src.schemas import LoginSchema, SetupSchema
from src.core.security import log_security_event

logger = logging.getLogger(__name__)

# Criar blueprint
auth_bp = Blueprint('auth', __name__)


def obter_ip_cliente():
    """Obtém o endereço IP do cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or '0.0.0.0'


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do sistema"""
    if request.method == 'POST':
        try:
            # Validar dados de entrada
            schema = LoginSchema()
            dados = schema.load(request.get_json())

            login_usuario = dados['login']
            senha = dados['senha']

            # Buscar usuário
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, nome, senha_hash, nivel_acesso, ativo
                    FROM usuarios
                    WHERE login = ? AND ativo = 1
                """, (login_usuario,))
                usuario = cursor.fetchone()

            # Verificar se usuário existe e senha está correta
            if usuario and verificar_senha(senha, usuario['senha_hash']):
                # Limpar sessão antiga e gerar nova
                old_session_id = session.get('_id')
                session.clear()

                # Criar nova sessão
                session.permanent = True
                session['usuario_id'] = usuario['id']
                session['usuario_nome'] = usuario['nome']
                session['nivel_acesso'] = usuario['nivel_acesso']
                session['login_timestamp'] = datetime.now().isoformat()
                session['ip_address'] = obter_ip_cliente()

                if old_session_id:
                    logger.info(f"Sessão regenerada para usuário ID: {usuario['id']}")

                # Atualizar último acesso
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE usuarios
                        SET ultimo_acesso = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (usuario['id'],))
                    conn.commit()

                # Registrar log
                registrar_log(
                    usuario['id'], usuario['nome'], obter_ip_cliente(),
                    'Autenticação', 'Login realizado com sucesso'
                )

                log_security_event(
                    'login_success',
                    f'Login bem-sucedido para usuário ID: {usuario["id"]}',
                    user_id=usuario['id'],
                    ip_address=obter_ip_cliente()
                )

                logger.info(f"Login bem-sucedido: usuário ID {usuario['id']}")

                return jsonify({
                    'sucesso': True,
                    'mensagem': 'Login realizado com sucesso!',
                    'redirect': url_for('index')
                })
            else:
                # Login falhou
                log_security_event(
                    'login_failed',
                    f'Tentativa de login falhou',
                    ip_address=obter_ip_cliente()
                )

                logger.warning(f"Tentativa de login falhou de IP: {obter_ip_cliente()}")

                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Login ou senha incorretos'
                }), 401

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Erro ao processar login'
            }), 500

    # GET - Mostrar página de login
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Realiza logout do usuário"""
    if 'usuario_id' in session:
        registrar_log(
            session['usuario_id'],
            session['usuario_nome'],
            obter_ip_cliente(),
            'Autenticação',
            'Logout realizado'
        )

        log_security_event(
            'logout',
            f'Logout de usuário ID: {session["usuario_id"]}',
            user_id=session['usuario_id'],
            ip_address=obter_ip_cliente()
        )

        logger.info(f"Logout: usuário ID {session['usuario_id']}")

    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """Configuração inicial do sistema"""
    if verificar_setup_inicial():
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Validar dados de entrada
            schema = SetupSchema()
            dados = schema.load(request.get_json())

            # Salvar configurações
            salvar_configuracao('nome_hospital', dados.get('nome_hospital'))
            salvar_configuracao('sigla_oms', dados.get('sigla_oms', ''))
            salvar_configuracao('regiao_militar', dados.get('regiao_militar', ''))
            salvar_configuracao('comando_vinculado', dados.get('comando_vinculado', ''))
            salvar_configuracao('diretor_tecnico', dados.get('diretor_tecnico'))
            salvar_configuracao('responsavel_ti', dados.get('responsavel_ti'))
            salvar_configuracao('prefixo_documentos', dados.get('prefixo_documentos', 'HGU'))

            # Criar setores padrão
            criar_setores_padrao()

            # Criar usuário administrador
            criar_usuario_admin(
                dados.get('admin_login'),
                dados.get('admin_senha'),
                dados.get('admin_nome')
            )

            # Marcar sistema como configurado
            salvar_configuracao('configurado', '1')

            logger.info("Setup inicial concluído com sucesso")

            return jsonify({
                'sucesso': True,
                'mensagem': 'Sistema configurado com sucesso!',
                'redirect': url_for('auth.login')
            })

        except Exception as e:
            logger.error(f"Erro no setup: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': f'Erro ao configurar sistema: {str(e)}'
            }), 500

    # GET - Mostrar página de setup
    return render_template('setup.html')
