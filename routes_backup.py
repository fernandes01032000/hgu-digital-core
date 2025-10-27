# -*- coding: utf-8 -*-
"""
Rotas de Backup
Endpoints para gerenciamento de backups do sistema
"""

from flask import jsonify, request, send_file
from functools import wraps
import logging
from backup import (
    realizar_backup, listar_backups, restaurar_backup,
    verificar_integridade_backup, limpar_backups_antigos
)

logger = logging.getLogger(__name__)


def register_backup_routes(app, login_requerido, nivel_acesso_requerido, obter_ip_cliente, registrar_log, session):
    """
    Registra rotas de backup na aplicação Flask

    Args:
        app: Instância Flask
        login_requerido: Decorador de autenticação
        nivel_acesso_requerido: Decorador de controle de acesso
        obter_ip_cliente: Função para obter IP do cliente
        registrar_log: Função de logging
        session: Session do Flask
    """

    @app.route('/api/backup/criar', methods=['POST'])
    @login_requerido
    @nivel_acesso_requerido('administrador')
    def api_criar_backup():
        """
        Cria um novo backup manual do banco de dados
        Apenas administradores
        """
        try:
            info_backup = realizar_backup(
                usuario_id=session['usuario_id'],
                tipo='manual'
            )

            registrar_log(
                session['usuario_id'],
                session['usuario_nome'],
                obter_ip_cliente(),
                'Backup',
                f'Backup criado: {info_backup["nome_arquivo"]}'
            )

            logger.info(f"Backup manual criado por {session['usuario_nome']}")

            return jsonify({
                'sucesso': True,
                'mensagem': 'Backup criado com sucesso!',
                'backup': info_backup
            })

        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': f'Erro ao criar backup: {str(e)}'
            }), 500

    @app.route('/api/backup/listar', methods=['GET'])
    @login_requerido
    @nivel_acesso_requerido('administrador')
    def api_listar_backups():
        """
        Lista todos os backups disponíveis
        Apenas administradores
        """
        try:
            backups = listar_backups()

            return jsonify({
                'sucesso': True,
                'backups': backups
            })

        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Erro ao listar backups'
            }), 500

    @app.route('/api/backup/verificar/<int:backup_id>', methods=['GET'])
    @login_requerido
    @nivel_acesso_requerido('administrador')
    def api_verificar_backup(backup_id):
        """
        Verifica integridade de um backup específico
        Apenas administradores
        """
        try:
            resultado = verificar_integridade_backup(backup_id)

            return jsonify({
                'sucesso': True,
                'verificacao': resultado
            })

        except Exception as e:
            logger.error(f"Erro ao verificar backup: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Erro ao verificar backup'
            }), 500

    @app.route('/api/backup/limpar-antigos', methods=['POST'])
    @login_requerido
    @nivel_acesso_requerido('administrador')
    def api_limpar_backups_antigos():
        """
        Remove backups antigos conforme política de retenção
        Apenas administradores
        """
        try:
            removidos = limpar_backups_antigos()

            registrar_log(
                session['usuario_id'],
                session['usuario_nome'],
                obter_ip_cliente(),
                'Backup',
                f'{removidos} backup(s) antigo(s) removido(s)'
            )

            return jsonify({
                'sucesso': True,
                'mensagem': f'{removidos} backup(s) removido(s)',
                'quantidade': removidos
            })

        except Exception as e:
            logger.error(f"Erro ao limpar backups: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Erro ao limpar backups'
            }), 500

    @app.route('/backup')
    @login_requerido
    @nivel_acesso_requerido('administrador')
    def pagina_backup():
        """
        Página de gerenciamento de backups
        Apenas administradores
        """
        from flask import render_template
        return render_template('backup.html', usuario=session['usuario_nome'])

    logger.info("Rotas de backup registradas")
