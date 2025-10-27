# -*- coding: utf-8 -*-
"""
Aplicação Principal - HGU Digital Core
Servidor Flask que gerencia todas as rotas e funcionalidades do sistema
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
import logging
from io import BytesIO
from datetime import datetime, timedelta
from functools import wraps

# Importar módulos do sistema
from src.config import (
    SERVER, SECURITY, SYSTEM_CONFIG, TIPOS_DOCUMENTOS,
    STATUS_AUDITORIA, NIVEIS_ACESSO, RATE_LIMITING, DATABASE
)
from src.core.database import (
    inicializar_db, verificar_setup_inicial, salvar_configuracao,
    obter_configuracao, criar_setores_padrao, criar_usuario_admin,
    registrar_log, listar_setores, cadastrar_paciente, cadastrar_profissional,
    criar_documento, listar_documentos, buscar_paciente_por_prec, listar_profissionais,
    init_bcrypt, verificar_senha, get_db_connection
)
from src.services.pdf_generator import gerar_pdf_documento
from src.schemas import (
    LoginSchema, SetupSchema, PacienteSchema, ProfissionalSchema,
    DocumentoSchema, validate_request
)
from src.core.logger import setup_logging, log_api_call
from src.utils.helpers import find_free_port, get_local_ip
from src.core.security import add_security_headers, validate_content_type, sanitize_filename, log_security_event

# Criar aplicação Flask
app = Flask(__name__)

# Configurar aplicação
app.secret_key = SECURITY['secret_key']
app.config['SESSION_COOKIE_SECURE'] = not SERVER['debug']  # HTTPS apenas em produção
app.config['SESSION_COOKIE_HTTPONLY'] = SECURITY['session_cookie_httponly']
app.config['SESSION_COOKIE_SAMESITE'] = SECURITY['session_cookie_samesite']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=SECURITY['permanent_session_lifetime'])
app.config['WTF_CSRF_ENABLED'] = True  # CSRF habilitado
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Verificação manual por rota
app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF token não expira

# Inicializar extensões
csrf = CSRFProtect(app)
bcrypt = init_bcrypt(app)

# Isentar rotas públicas de CSRF
csrf.exempt('/health')
csrf.exempt('/login')

# Configurar Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=RATE_LIMITING['storage_uri'],
    default_limits=RATE_LIMITING['default_limits']
)

# Configurar logging
setup_logging(app)
logger = logging.getLogger(__name__)

# Aplicar headers de segurança em todas as respostas
@app.after_request
def apply_security_headers(response):
    """Aplica headers de segurança HTTP"""
    return add_security_headers(response)

# Inicializar banco de dados na primeira execução
if not os.path.exists(DATABASE['name']):
    logger.info("Primeira execução detectada. Inicializando banco de dados...")
    print("🔧 Primeira execução detectada. Inicializando banco de dados...")
    try:
        inicializar_db()
    except Exception as e:
        logger.critical(f"Erro ao inicializar banco de dados: {e}")
        print(f"❌ Erro crítico ao inicializar banco de dados: {e}")
        raise


# ============================================================================
# DECORADORES E FUNÇÕES AUXILIARES
# ============================================================================

def obter_ip_cliente():
    """
    Obtém o endereço IP do cliente que fez a requisição
    Considera proxies e load balancers
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or '0.0.0.0'


def login_requerido(f):
    """
    Decorador que verifica se o usuário está logado
    Redireciona para login se não estiver
    Inclui validação de IP para prevenir session hijacking
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            log_security_event(
                'access_denied',
                f'Tentativa de acesso sem autenticação: {request.endpoint}',
                ip_address=obter_ip_cliente()
            )
            return redirect(url_for('login'))

        # Validar IP da sessão (prevenir session hijacking)
        # Comentado por padrão - pode causar problemas com proxies/NAT
        # if session.get('ip_address') and session.get('ip_address') != obter_ip_cliente():
        #     log_security_event(
        #         'session_hijacking_attempt',
        #         f'IP diferente detectado na sessão',
        #         user_id=session.get('usuario_id'),
        #         ip_address=obter_ip_cliente()
        #     )
        #     session.clear()
        #     return redirect(url_for('login'))

        # Renovar sessão se próximo da expiração
        session.permanent = True
        session.modified = True

        return f(*args, **kwargs)
    return decorated_function


def nivel_acesso_requerido(*niveis_permitidos):
    """
    Decorador que verifica se o usuário tem nível de acesso adequado

    Args:
        *niveis_permitidos: Lista de níveis de acesso permitidos

    Usage:
        @nivel_acesso_requerido('administrador', 'auditor')
        def minha_rota():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'nivel_acesso' not in session:
                log_security_event(
                    'access_denied',
                    'Sessão sem nível de acesso',
                    user_id=session.get('usuario_id'),
                    ip_address=obter_ip_cliente()
                )
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Acesso negado'
                }), 403

            if session['nivel_acesso'] not in niveis_permitidos:
                log_security_event(
                    'access_denied',
                    f'Acesso negado por nível insuficiente: {request.endpoint}',
                    user_id=session.get('usuario_id'),
                    ip_address=obter_ip_cliente(),
                    extra_data={'nivel_usuario': session['nivel_acesso']}
                )
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Você não tem permissão para acessar este recurso'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# ROTAS - AUTENTICAÇÃO
# ============================================================================

@app.route('/')
def index():
    """
    Página inicial do sistema
    Redireciona para setup se não configurado, ou para login/dashboard
    """
    try:
        if not verificar_setup_inicial():
            return redirect(url_for('setup'))

        if 'usuario_id' in session:
            return redirect(url_for('dashboard'))

        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Erro na página inicial: {e}")
        return render_template('error.html', mensagem="Erro ao carregar página inicial"), 500


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit(f"{RATE_LIMITING['login_attempts']} per {RATE_LIMITING['login_window']} seconds")
def login():
    """
    Página de login do sistema
    Rate limited para prevenir brute force
    """
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
                # Limpar sessão antiga e gerar nova (previne session fixation)
                old_session_id = session.get('_id')
                session.clear()

                # Criar nova sessão
                session.permanent = True
                session['usuario_id'] = usuario['id']
                session['usuario_nome'] = usuario['nome']
                session['nivel_acesso'] = usuario['nivel_acesso']
                session['login_timestamp'] = datetime.now().isoformat()
                session['ip_address'] = obter_ip_cliente()  # Validar IP nas próximas requisições

                # Log da mudança de sessão
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
                    f'Login bem-sucedido: {login_usuario}',
                    user_id=usuario['id'],
                    ip_address=obter_ip_cliente()
                )

                logger.info(f"Login bem-sucedido: {login_usuario} (ID: {usuario['id']})")

                return jsonify({
                    'sucesso': True,
                    'mensagem': 'Login realizado com sucesso!',
                    'redirect': url_for('dashboard')
                })
            else:
                # Login falhou
                log_security_event(
                    'login_failed',
                    f'Tentativa de login falhou: {login_usuario}',
                    ip_address=obter_ip_cliente()
                )

                logger.warning(f"Tentativa de login falhou: {login_usuario}")

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


@app.route('/logout')
def logout():
    """
    Realiza logout do usuário
    """
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
            f'Logout: {session["usuario_nome"]}',
            user_id=session['usuario_id'],
            ip_address=obter_ip_cliente()
        )

        logger.info(f"Logout: {session['usuario_nome']} (ID: {session['usuario_id']})")

    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# ROTAS - SETUP INICIAL
# ============================================================================

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """
    Configuração inicial do sistema
    Executado apenas na primeira vez
    """
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
                'redirect': url_for('login')
            })

        except Exception as e:
            logger.error(f"Erro no setup: {e}")
            return jsonify({
                'sucesso': False,
                'mensagem': f'Erro ao configurar sistema: {str(e)}'
            }), 500

    # GET - Mostrar página de setup
    return render_template('setup.html')


# ============================================================================
# ROTAS - DASHBOARD
# ============================================================================

@app.route('/dashboard')
@login_requerido
def dashboard():
    """
    Painel principal do sistema
    """
    try:
        # Obter estatísticas básicas
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Total de documentos
            cursor.execute("SELECT COUNT(*) as total FROM documentos")
            total_docs = cursor.fetchone()['total']

            # Total de pacientes
            cursor.execute("SELECT COUNT(*) as total FROM pacientes WHERE ativo = 1")
            total_pacientes = cursor.fetchone()['total']

            # Total de profissionais
            cursor.execute("SELECT COUNT(*) as total FROM profissionais WHERE ativo = 1")
            total_profissionais = cursor.fetchone()['total']

            # Documentos por status
            cursor.execute("""
                SELECT status, COUNT(*) as total
                FROM documentos
                GROUP BY status
            """)
            docs_por_status = cursor.fetchall()

        estatisticas = {
            'total_documentos': total_docs,
            'total_pacientes': total_pacientes,
            'total_profissionais': total_profissionais,
            'documentos_por_status': [dict(row) for row in docs_por_status]
        }

        return render_template('dashboard.html',
                             usuario=session['usuario_nome'],
                             nivel_acesso=session['nivel_acesso'],
                             estatisticas=estatisticas)

    except Exception as e:
        logger.error(f"Erro ao carregar dashboard: {e}")
        return render_template('error.html', mensagem="Erro ao carregar dashboard"), 500


# ============================================================================
# ROTAS - DOCUMENTOS
# ============================================================================

@app.route('/documentos')
@login_requerido
def documentos():
    """
    Página de gestão de documentos
    """
    return render_template('documentos.html',
                         tipos_documentos=TIPOS_DOCUMENTOS,
                         usuario=session['usuario_nome'])


@app.route('/api/documentos/listar', methods=['GET'])
@login_requerido
@limiter.limit("100 per minute")
def api_listar_documentos():
    """
    API para listar documentos
    """
    try:
        limite = request.args.get('limite', 100, type=int)
        limite = min(limite, 1000)  # Máximo de 1000 documentos por vez

        docs = listar_documentos(limite)

        return jsonify({'sucesso': True, 'documentos': docs})

    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao listar documentos'
        }), 500


@app.route('/api/documentos/criar', methods=['POST'])
@login_requerido
@limiter.limit("20 per minute")
@validate_request(DocumentoSchema)
def api_criar_documento(validated_data):
    """
    API para criar novo documento
    """
    try:
        codigo = criar_documento(
            tipo_documento=validated_data['tipo_documento'],
            paciente_id=validated_data['paciente_id'],
            profissional_id=validated_data['profissional_id'],
            setor_origem_id=validated_data['setor_origem_id'],
            setor_destino_id=validated_data.get('setor_destino_id'),
            conteudo_json=validated_data['conteudo'],
            usuario_criador_id=session['usuario_id']
        )

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'Documentos', f'Documento criado: {codigo}'
        )

        logger.info(f"Documento criado: {codigo} por {session['usuario_nome']}")

        return jsonify({
            'sucesso': True,
            'mensagem': 'Documento criado com sucesso!',
            'codigo': codigo
        })

    except Exception as e:
        logger.error(f"Erro ao criar documento: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao criar documento: {str(e)}'
        }), 500


# ============================================================================
# ROTAS - PACIENTES
# ============================================================================

@app.route('/pacientes')
@login_requerido
def pacientes():
    """
    Página de gestão de pacientes
    """
    return render_template('pacientes.html', usuario=session['usuario_nome'])


@app.route('/api/pacientes/cadastrar', methods=['POST'])
@login_requerido
@limiter.limit("30 per minute")
@validate_request(PacienteSchema)
def api_cadastrar_paciente(validated_data):
    """
    API para cadastrar novo paciente
    """
    try:
        paciente_id = cadastrar_paciente(
            nome_completo=validated_data['nome_completo'],
            prec_cp=validated_data['prec_cp'],
            posto=validated_data.get('posto', ''),
            om=validated_data.get('om', ''),
            data_nascimento=validated_data.get('data_nascimento', ''),
            observacoes=validated_data.get('observacoes', '')
        )

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'Pacientes', f'Paciente cadastrado: {validated_data["nome_completo"]}'
        )

        logger.info(f"Paciente cadastrado: {validated_data['nome_completo']} (ID: {paciente_id})")

        return jsonify({
            'sucesso': True,
            'mensagem': 'Paciente cadastrado com sucesso!',
            'paciente_id': paciente_id
        })

    except Exception as e:
        logger.error(f"Erro ao cadastrar paciente: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao cadastrar paciente: {str(e)}'
        }), 500


@app.route('/api/pacientes/buscar/<prec_cp>', methods=['GET'])
@login_requerido
def api_buscar_paciente(prec_cp):
    """
    API para buscar paciente por PREC-CP
    """
    try:
        paciente = buscar_paciente_por_prec(prec_cp)

        if paciente:
            return jsonify({'sucesso': True, 'paciente': paciente})
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado'
            }), 404

    except Exception as e:
        logger.error(f"Erro ao buscar paciente: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao buscar paciente'
        }), 500


# ============================================================================
# ROTAS - PROFISSIONAIS
# ============================================================================

@app.route('/profissionais')
@login_requerido
def profissionais():
    """
    Página de gestão de profissionais
    """
    try:
        setores = listar_setores()
        return render_template('profissionais.html',
                             usuario=session['usuario_nome'],
                             setores=setores)
    except Exception as e:
        logger.error(f"Erro ao carregar página de profissionais: {e}")
        return render_template('error.html', mensagem="Erro ao carregar página"), 500


@app.route('/api/profissionais/cadastrar', methods=['POST'])
@login_requerido
@limiter.limit("30 per minute")
@validate_request(ProfissionalSchema)
def api_cadastrar_profissional(validated_data):
    """
    API para cadastrar novo profissional
    """
    try:
        prof_id = cadastrar_profissional(
            nome=validated_data['nome'],
            funcao=validated_data['funcao'],
            crm_coren=validated_data.get('crm_coren', ''),
            posto_graduacao=validated_data.get('posto_graduacao', ''),
            setor_id=validated_data.get('setor_id')
        )

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'Profissionais', f'Profissional cadastrado: {validated_data["nome"]}'
        )

        logger.info(f"Profissional cadastrado: {validated_data['nome']} (ID: {prof_id})")

        return jsonify({
            'sucesso': True,
            'mensagem': 'Profissional cadastrado com sucesso!',
            'profissional_id': prof_id
        })

    except Exception as e:
        logger.error(f"Erro ao cadastrar profissional: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao cadastrar profissional: {str(e)}'
        }), 500


@app.route('/api/profissionais/listar', methods=['GET'])
@login_requerido
def api_listar_profissionais():
    """
    API para listar profissionais
    """
    try:
        profs = listar_profissionais()
        return jsonify({'sucesso': True, 'profissionais': profs})
    except Exception as e:
        logger.error(f"Erro ao listar profissionais: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao listar profissionais'
        }), 500


# ============================================================================
# ROTAS - SETORES
# ============================================================================

@app.route('/api/setores/listar', methods=['GET'])
@login_requerido
def api_listar_setores():
    """
    API para listar setores
    """
    try:
        setores = listar_setores()
        return jsonify({'sucesso': True, 'setores': setores})
    except Exception as e:
        logger.error(f"Erro ao listar setores: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao listar setores'
        }), 500


# ============================================================================
# ROTAS - RELATÓRIOS
# ============================================================================

@app.route('/relatorios')
@login_requerido
def relatorios():
    """
    Página de relatórios do sistema
    """
    return render_template('relatorios.html', usuario=session['usuario_nome'])


# ============================================================================
# ROTAS - AUDITORIA
# ============================================================================

@app.route('/auditoria')
@login_requerido
@nivel_acesso_requerido('auditor', 'administrador')
def auditoria():
    """
    Página de auditoria (apenas para auditores e administradores)
    """
    return render_template('auditoria.html',
                         usuario=session['usuario_nome'],
                         status_disponiveis=STATUS_AUDITORIA)


# ============================================================================
# ROTAS - PDF FORM BUILDER
# ============================================================================

from src.services import pdf_builder
from src.schemas import PDFTemplateUploadSchema, SaveTemplateFieldsSchema, GeneratePDFSchema

@app.route('/pdf-builder')
@login_requerido
def pdf_builder_page():
    """Página do PDF Form Builder (React SPA)"""
    return render_template('pdf_builder.html', usuario=session['usuario_nome'])


@app.route('/api/pdf-templates', methods=['GET'])
@login_requerido
def api_listar_templates():
    """Lista todos os templates PDF"""
    try:
        templates = pdf_builder.listar_templates()
        return jsonify({'sucesso': True, 'templates': templates})
    except Exception as e:
        logger.error(f"Erro ao listar templates: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao listar templates'
        }), 500


@app.route('/api/pdf-templates/upload', methods=['POST'])
@login_requerido
@limiter.limit("10 per hour")
@validate_content_type(['application/pdf'])
def api_upload_template():
    """Upload de PDF para criar template"""
    try:
        # Validar arquivo
        if 'file' not in request.files:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum arquivo enviado'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'sucesso': False,
                'mensagem': 'Arquivo vazio'
            }), 400

        # Sanitizar nome do arquivo
        safe_filename = sanitize_filename(file.filename)
        if not safe_filename or not safe_filename.lower().endswith('.pdf'):
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nome de arquivo inválido'
            }), 400

        # Validar tamanho (max 10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'sucesso': False,
                'mensagem': 'Arquivo muito grande (máximo 10MB)'
            }), 400

        # Validar dados do formulário
        schema = PDFTemplateUploadSchema()
        try:
            form_data = schema.load(request.form.to_dict())
        except Exception as e:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Dados inválidos',
                'erros': str(e)
            }), 400

        # Criar template
        template = pdf_builder.criar_template(
            nome=form_data['name'],
            descricao=form_data.get('description', ''),
            pdf_file=file,
            usuario_id=session['usuario_id']
        )

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'PDF Builder', f'Template criado: {template["nome"]}'
        )

        logger.info(f"Template PDF criado: {template['id']} por {session['usuario_nome']}")

        return jsonify({
            'sucesso': True,
            'mensagem': 'Template criado com sucesso!',
            'template': template
        })

    except ValueError as e:
        return jsonify({
            'sucesso': False,
            'mensagem': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erro ao criar template: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao criar template: {str(e)}'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>', methods=['GET'])
@login_requerido
def api_obter_template(template_id):
    """Obtém informações de um template"""
    try:
        template = pdf_builder.obter_template(template_id)

        if not template:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Template não encontrado'
            }), 404

        return jsonify({'sucesso': True, 'template': template})

    except Exception as e:
        logger.error(f"Erro ao obter template: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao obter template'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>/pdf', methods=['GET'])
@login_requerido
def api_obter_pdf_template(template_id):
    """Retorna o arquivo PDF de um template"""
    try:
        pdf_bytes = pdf_builder.obter_pdf_template(template_id)

        if not pdf_bytes:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Template ou PDF não encontrado'
            }), 404

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'template_{template_id}.pdf'
        )

    except Exception as e:
        logger.error(f"Erro ao obter PDF: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao obter PDF'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>', methods=['PUT'])
@login_requerido
def api_atualizar_template(template_id):
    """Atualiza informações de um template"""
    try:
        dados = request.get_json()

        sucesso = pdf_builder.atualizar_template(
            template_id,
            nome=dados.get('name'),
            descricao=dados.get('description'),
            ativo=dados.get('ativo')
        )

        if not sucesso:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Template não encontrado'
            }), 404

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'PDF Builder', f'Template atualizado: {template_id}'
        )

        return jsonify({
            'sucesso': True,
            'mensagem': 'Template atualizado com sucesso!'
        })

    except Exception as e:
        logger.error(f"Erro ao atualizar template: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao atualizar template'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>', methods=['DELETE'])
@login_requerido
def api_deletar_template(template_id):
    """Deleta um template (soft delete)"""
    try:
        sucesso = pdf_builder.deletar_template(template_id)

        if not sucesso:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Template não encontrado'
            }), 404

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'PDF Builder', f'Template deletado: {template_id}'
        )

        return jsonify({
            'sucesso': True,
            'mensagem': 'Template deletado com sucesso!'
        })

    except Exception as e:
        logger.error(f"Erro ao deletar template: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao deletar template'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>/duplicate', methods=['POST'])
@login_requerido
def api_duplicar_template(template_id):
    """Duplica um template"""
    try:
        novo_template = pdf_builder.duplicar_template(template_id, session['usuario_id'])

        if not novo_template:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Template não encontrado ou erro ao duplicar'
            }), 404

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'PDF Builder', f'Template duplicado: {template_id} -> {novo_template["id"]}'
        )

        return jsonify({
            'sucesso': True,
            'mensagem': 'Template duplicado com sucesso!',
            'template': novo_template
        })

    except Exception as e:
        logger.error(f"Erro ao duplicar template: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao duplicar template'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>/fields', methods=['PUT'])
@login_requerido
def api_salvar_campos(template_id):
    """Salva os campos de um template"""
    try:
        schema = SaveTemplateFieldsSchema()
        dados = schema.load(request.get_json())

        sucesso = pdf_builder.salvar_campos_template(template_id, dados['fields'])

        if not sucesso:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Template não encontrado'
            }), 404

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'PDF Builder', f'Campos salvos para template: {template_id}'
        )

        return jsonify({
            'sucesso': True,
            'mensagem': 'Campos salvos com sucesso!'
        })

    except Exception as e:
        logger.error(f"Erro ao salvar campos: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar campos: {str(e)}'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>/fields', methods=['GET'])
@login_requerido
def api_obter_campos(template_id):
    """Obtém os campos de um template"""
    try:
        campos = pdf_builder.obter_campos_template(template_id)

        return jsonify({
            'sucesso': True,
            'campos': campos
        })

    except Exception as e:
        logger.error(f"Erro ao obter campos: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao obter campos'
        }), 500


@app.route('/api/pdf-templates/<int:template_id>/generate', methods=['POST'])
@login_requerido
def api_gerar_pdf(template_id):
    """Gera PDF preenchido com dados do formulário"""
    try:
        dados = request.get_json()
        form_data = dados.get('formData', {})

        pdf_bytes = pdf_builder.gerar_pdf_preenchido(template_id, form_data)

        # Registrar log
        registrar_log(
            session['usuario_id'], session['usuario_nome'], obter_ip_cliente(),
            'PDF Builder', f'PDF gerado do template: {template_id}'
        )

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'documento_{template_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )

    except ValueError as e:
        return jsonify({
            'sucesso': False,
            'mensagem': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao gerar PDF: {str(e)}'
        }), 500


@app.route('/api/upload-image', methods=['POST'])
@login_requerido
@limiter.limit("20 per minute")
@validate_content_type(['image/png', 'image/jpeg', 'image/gif'])
def api_upload_imagem():
    """Upload de imagem para campos signature/image"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum arquivo enviado'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'sucesso': False,
                'mensagem': 'Arquivo vazio'
            }), 400

        # Sanitizar nome do arquivo
        safe_filename = sanitize_filename(file.filename)
        if not safe_filename:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nome de arquivo inválido'
            }), 400

        # Validar tamanho (max 5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({
                'sucesso': False,
                'mensagem': 'Imagem muito grande (máximo 5MB)'
            }), 400

        # Processar imagem
        data_url = pdf_builder.processar_upload_imagem(file)

        return jsonify({
            'sucesso': True,
            'dataUrl': data_url
        })

    except ValueError as e:
        return jsonify({
            'sucesso': False,
            'mensagem': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erro ao fazer upload de imagem: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao fazer upload de imagem'
        }), 500


# ============================================================================
# ROTAS - SAÚDE E INFORMAÇÕES
# ============================================================================

@app.route('/health')
def health():
    """
    Endpoint de health check para monitoramento
    """
    try:
        # Testar conexão com banco
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503


# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Página não encontrada"""
    logger.warning(f"Página não encontrada: {request.url}")
    return render_template('error.html', mensagem="Página não encontrada"), 404


@app.errorhandler(403)
def forbidden(e):
    """Acesso negado"""
    logger.warning(f"Acesso negado: {request.url}")
    return render_template('error.html', mensagem="Acesso negado"), 403


@app.errorhandler(500)
def internal_error(e):
    """Erro interno do servidor"""
    logger.error(f"Erro interno: {e}")
    return render_template('error.html', mensagem="Erro interno do servidor"), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit excedido"""
    logger.warning(f"Rate limit excedido: {obter_ip_cliente()}")
    return jsonify({
        'sucesso': False,
        'mensagem': 'Muitas tentativas. Por favor, aguarde alguns minutos.'
    }), 429


# ============================================================================
# INICIAR SERVIDOR
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🏛️  HGU DIGITAL CORE - Sistema Offline v2.0")
    print("=" * 70)

    # Detectar porta disponível
    try:
        porta = find_free_port(SERVER['port'])
        if porta != SERVER['port']:
            print(f"⚠️  Porta {SERVER['port']} em uso. Usando porta {porta}")
    except Exception as e:
        print(f"❌ Erro ao detectar porta: {e}")
        porta = SERVER['port']

    # Obter IP local
    ip_local = get_local_ip()

    print(f"🌐 Servidor iniciando em http://{SERVER['host']}:{porta}")
    print(f"📡 Acesse de outros computadores usando: http://{ip_local}:{porta}")
    print(f"🔒 Modo debug: {'ATIVADO ⚠️' if SERVER['debug'] else 'DESATIVADO ✓'}")
    print(f"🔐 CSRF Protection: ATIVADO ✓")
    print(f"🛡️  Rate Limiting: ATIVADO ✓")
    print(f"📝 Logging: ATIVADO ✓")
    print("=" * 70)
    print()

    if SERVER['debug']:
        print("⚠️  ATENÇÃO: Modo debug está ativado!")
        print("   Desative em produção configurando DEBUG=False no arquivo .env")
        print()

    try:
        app.run(
            host=SERVER['host'],
            port=porta,
            debug=SERVER['debug'],
            threaded=True
        )
    except Exception as e:
        logger.critical(f"Erro ao iniciar servidor: {e}")
        print(f"\n❌ Erro crítico ao iniciar servidor: {e}")
        raise
