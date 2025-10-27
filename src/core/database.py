# -*- coding: utf-8 -*-
"""
Funções do Banco de Dados
Contém todas as funções para interagir com o SQLite
"""

import sqlite3
import json
import logging
import hashlib
from datetime import datetime
from contextlib import contextmanager
from flask_bcrypt import Bcrypt
from src.config import DATABASE, SETORES_PADRAO, SECURITY
from src.models import ALL_TABLES

# Configurar logging
logger = logging.getLogger(__name__)

# Instância do Bcrypt (será inicializada pela aplicação Flask)
bcrypt = None


def init_bcrypt(app):
    """
    Inicializa o Bcrypt com a aplicação Flask

    Args:
        app: Instância da aplicação Flask
    """
    global bcrypt
    bcrypt = Bcrypt(app)
    return bcrypt


@contextmanager
def get_db_connection():
    """
    Context manager para conexão com banco de dados
    Garante que a conexão seja sempre fechada, mesmo em caso de erro

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)

    Yields:
        sqlite3.Connection: Conexão com o banco de dados
    """
    conn = None
    try:
        conn = sqlite3.connect(
            DATABASE['name'],
            timeout=DATABASE.get('timeout', 30.0),
            check_same_thread=DATABASE.get('check_same_thread', False)
        )
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def conectar_db():
    """
    Cria uma conexão com o banco de dados SQLite
    DEPRECATED: Use get_db_connection() context manager

    Retorna: objeto de conexão
    """
    logger.warning("conectar_db() está deprecated. Use get_db_connection() context manager")
    conn = sqlite3.connect(
        DATABASE['name'],
        timeout=DATABASE.get('timeout', 30.0),
        check_same_thread=DATABASE.get('check_same_thread', False)
    )
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    """
    Cria todas as tabelas do banco de dados se não existirem
    Deve ser executado na primeira vez que o sistema é iniciado
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Criar todas as tabelas
    for sql_create in ALL_TABLES:
        cursor.execute(sql_create)
    
    conn.commit()
    conn.close()
    print("✓ Banco de dados inicializado com sucesso!")


def verificar_setup_inicial():
    """
    Verifica se o setup inicial do sistema foi concluído
    Retorna: True se configurado, False caso contrário
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'configurado'")
    resultado = cursor.fetchone()
    
    conn.close()
    
    if resultado and resultado['valor'] == '1':
        return True
    return False


def salvar_configuracao(chave, valor, descricao=''):
    """
    Salva ou atualiza uma configuração no banco de dados
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO configuracoes (chave, valor, descricao, data_atualizacao)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(chave) DO UPDATE SET 
            valor = excluded.valor,
            data_atualizacao = CURRENT_TIMESTAMP
    """, (chave, str(valor), descricao))
    
    conn.commit()
    conn.close()


def obter_configuracao(chave, padrao=None):
    """
    Obtém o valor de uma configuração
    Retorna o valor padrão se não encontrar
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
    resultado = cursor.fetchone()
    
    conn.close()
    
    if resultado:
        return resultado['valor']
    return padrao


def criar_setores_padrao():
    """
    Cria os setores padrão do hospital
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    for setor in SETORES_PADRAO:
        cursor.execute("""
            INSERT OR IGNORE INTO setores (nome, sigla, ativo)
            VALUES (?, ?, 1)
        """, (setor, setor))
    
    conn.commit()
    conn.close()
    print("✓ Setores padrão criados!")


def criar_usuario_admin(login, senha, nome):
    """
    Cria o usuário administrador inicial

    Args:
        login: Login do administrador
        senha: Senha em texto plano (será hasheada)
        nome: Nome completo do administrador
    """
    if not bcrypt:
        raise RuntimeError("Bcrypt não foi inicializado. Chame init_bcrypt(app) primeiro")

    # Gerar hash seguro da senha com bcrypt
    senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nome, login, senha_hash, nivel_acesso, ativo)
            VALUES (?, ?, ?, 'administrador', 1)
        """, (nome, login, senha_hash))

        conn.commit()

    logger.info(f"Usuário administrador '{login}' criado com sucesso")
    print(f"✓ Usuário administrador '{login}' criado!")


def verificar_senha(senha_plana, senha_hash):
    """
    Verifica se a senha corresponde ao hash armazenado

    Args:
        senha_plana: Senha em texto plano
        senha_hash: Hash bcrypt armazenado

    Returns:
        bool: True se a senha está correta, False caso contrário
    """
    if not bcrypt:
        raise RuntimeError("Bcrypt não foi inicializado")

    try:
        return bcrypt.check_password_hash(senha_hash, senha_plana)
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False


def criar_usuario(nome, login, senha, nivel_acesso='visualizador'):
    """
    Cria um novo usuário no sistema

    Args:
        nome: Nome completo do usuário
        login: Login único do usuário
        senha: Senha em texto plano (será hasheada)
        nivel_acesso: Nível de acesso do usuário

    Returns:
        int: ID do usuário criado

    Raises:
        ValueError: Se o login já existir
    """
    if not bcrypt:
        raise RuntimeError("Bcrypt não foi inicializado")

    # Gerar hash seguro da senha
    senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verificar se login já existe
        cursor.execute("SELECT id FROM usuarios WHERE login = ?", (login,))
        if cursor.fetchone():
            raise ValueError(f"Login '{login}' já está em uso")

        cursor.execute("""
            INSERT INTO usuarios (nome, login, senha_hash, nivel_acesso, ativo)
            VALUES (?, ?, ?, ?, 1)
        """, (nome, login, senha_hash, nivel_acesso))

        usuario_id = cursor.lastrowid
        conn.commit()

    logger.info(f"Usuário '{login}' criado com sucesso")
    return usuario_id


def registrar_log(usuario_id, usuario_nome, ip_local, modulo, operacao, detalhes=''):
    """
    Registra uma ação no log do sistema
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO logs (usuario_id, usuario_nome, ip_local, modulo, operacao, detalhes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (usuario_id, usuario_nome, ip_local, modulo, operacao, detalhes))
    
    conn.commit()
    conn.close()


def listar_setores():
    """
    Lista todos os setores ativos
    Retorna: lista de dicionários com dados dos setores
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM setores WHERE ativo = 1 ORDER BY nome")
    setores = cursor.fetchall()
    
    conn.close()
    
    return [dict(setor) for setor in setores]


def cadastrar_paciente(nome_completo, prec_cp, posto='', om='', data_nascimento='', observacoes=''):
    """
    Cadastra um novo paciente no sistema
    Retorna: ID do paciente criado
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO pacientes (nome_completo, prec_cp, posto, om, data_nascimento, observacoes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome_completo, prec_cp, posto, om, data_nascimento, observacoes))
    
    paciente_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return paciente_id


def cadastrar_profissional(nome, funcao, crm_coren='', posto_graduacao='', setor_id=None):
    """
    Cadastra um novo profissional no sistema
    Retorna: ID do profissional criado
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO profissionais (nome, funcao, crm_coren, posto_graduacao, setor_id)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, funcao, crm_coren, posto_graduacao, setor_id))
    
    profissional_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return profissional_id


def gerar_codigo_documento(tipo_documento, prefixo):
    """
    Gera um código único para o documento
    Formato: PREFIXO-TIPO-ANO-NUMERO
    Exemplo: HGUMBA-EXAM-2025-0001
    """
    ano_atual = datetime.now().year
    
    # Mapear tipo de documento para sigla
    siglas = {
        'Guia de Exame': 'EXAM',
        'Encaminhamento Médico': 'ENCAM',
        'Guia de Internação': 'INTER',
        'Declaração': 'DECL',
        'Atestado Administrativo': 'ATEST'
    }
    
    sigla = siglas.get(tipo_documento, 'DOC')
    
    # Buscar último número do ano
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT codigo_unico FROM documentos 
        WHERE codigo_unico LIKE ? 
        ORDER BY id DESC LIMIT 1
    """, (f"{prefixo}-{sigla}-{ano_atual}-%",))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        # Extrair número do último código
        ultimo_codigo = resultado['codigo_unico']
        ultimo_numero = int(ultimo_codigo.split('-')[-1])
        novo_numero = ultimo_numero + 1
    else:
        novo_numero = 1
    
    # Formatar código com zeros à esquerda
    codigo = f"{prefixo}-{sigla}-{ano_atual}-{novo_numero:04d}"
    return codigo


def criar_documento(tipo_documento, paciente_id, profissional_id, setor_origem_id, 
                   setor_destino_id, conteudo_json, usuario_criador_id):
    """
    Cria um novo documento no sistema
    Retorna: código único do documento
    """
    prefixo = obter_configuracao('prefixo_documentos', 'HGU')
    codigo_unico = gerar_codigo_documento(tipo_documento, prefixo)
    
    # Gerar hash do documento
    hash_documento = hashlib.sha256(
        (codigo_unico + json.dumps(conteudo_json)).encode()
    ).hexdigest()
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO documentos (
            codigo_unico, tipo_documento, paciente_id, profissional_id,
            setor_origem_id, setor_destino_id, conteudo_json, hash_documento,
            status, usuario_criador_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Emitido', ?)
    """, (codigo_unico, tipo_documento, paciente_id, profissional_id,
          setor_origem_id, setor_destino_id, json.dumps(conteudo_json),
          hash_documento, usuario_criador_id))
    
    conn.commit()
    conn.close()
    
    return codigo_unico


def listar_documentos(limite=100):
    """
    Lista os documentos mais recentes
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.*, p.nome_completo as paciente_nome, 
               prof.nome as profissional_nome,
               so.nome as setor_origem_nome
        FROM documentos d
        LEFT JOIN pacientes p ON d.paciente_id = p.id
        LEFT JOIN profissionais prof ON d.profissional_id = prof.id
        LEFT JOIN setores so ON d.setor_origem_id = so.id
        ORDER BY d.data_emissao DESC
        LIMIT ?
    """, (limite,))
    
    documentos = cursor.fetchall()
    conn.close()
    
    return [dict(doc) for doc in documentos]


def buscar_paciente_por_prec(prec_cp):
    """
    Busca um paciente pelo PREC-CP
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pacientes WHERE prec_cp = ? AND ativo = 1", (prec_cp,))
    paciente = cursor.fetchone()
    
    conn.close()
    
    if paciente:
        return dict(paciente)
    return None


def listar_profissionais():
    """
    Lista todos os profissionais ativos
    """
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, s.nome as setor_nome
        FROM profissionais p
        LEFT JOIN setores s ON p.setor_id = s.id
        WHERE p.ativo = 1
        ORDER BY p.nome
    """)
    
    profissionais = cursor.fetchall()
    conn.close()
    
    return [dict(prof) for prof in profissionais]

