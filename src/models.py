# -*- coding: utf-8 -*-
"""
Modelos do Banco de Dados
Define a estrutura de todas as tabelas do sistema
"""

# SQL para criar todas as tabelas do banco de dados

# Tabela de Configurações do Sistema
SQL_CREATE_CONFIG = """
CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT,
    descricao TEXT,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tabela de Usuários
SQL_CREATE_USUARIOS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    nivel_acesso TEXT NOT NULL,
    ativo INTEGER DEFAULT 1,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP
);
"""

# Tabela de Setores
SQL_CREATE_SETORES = """
CREATE TABLE IF NOT EXISTS setores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    sigla TEXT,
    descricao TEXT,
    ativo INTEGER DEFAULT 1,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tabela de Pacientes
SQL_CREATE_PACIENTES = """
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo TEXT NOT NULL,
    prec_cp TEXT UNIQUE NOT NULL,
    posto TEXT,
    om TEXT,
    data_nascimento DATE,
    observacoes TEXT,
    ativo INTEGER DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tabela de Profissionais
SQL_CREATE_PROFISSIONAIS = """
CREATE TABLE IF NOT EXISTS profissionais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    funcao TEXT NOT NULL,
    crm_coren TEXT,
    posto_graduacao TEXT,
    setor_id INTEGER,
    ativo INTEGER DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (setor_id) REFERENCES setores(id)
);
"""

# Tabela de Documentos
SQL_CREATE_DOCUMENTOS = """
CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_unico TEXT UNIQUE NOT NULL,
    tipo_documento TEXT NOT NULL,
    paciente_id INTEGER,
    profissional_id INTEGER,
    setor_origem_id INTEGER,
    setor_destino_id INTEGER,
    conteudo_json TEXT,
    caminho_pdf TEXT,
    hash_documento TEXT,
    status TEXT DEFAULT 'Emitido',
    data_emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_criador_id INTEGER,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY (profissional_id) REFERENCES profissionais(id),
    FOREIGN KEY (setor_origem_id) REFERENCES setores(id),
    FOREIGN KEY (setor_destino_id) REFERENCES setores(id),
    FOREIGN KEY (usuario_criador_id) REFERENCES usuarios(id)
);
"""

# Tabela de Auditoria
SQL_CREATE_AUDITORIA = """
CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento_id INTEGER,
    status_anterior TEXT,
    status_novo TEXT,
    motivo_glosa TEXT,
    comentarios TEXT,
    auditor_id INTEGER,
    data_auditoria TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (documento_id) REFERENCES documentos(id),
    FOREIGN KEY (auditor_id) REFERENCES usuarios(id)
);
"""

# Tabela de Templates PDF
SQL_CREATE_TEMPLATES = """
CREATE TABLE IF NOT EXISTS templates_pdf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    caminho_arquivo TEXT NOT NULL,
    mapeamento_campos TEXT,
    ativo INTEGER DEFAULT 1,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tabela de Logs do Sistema
SQL_CREATE_LOGS = """
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    usuario_nome TEXT,
    ip_local TEXT,
    modulo TEXT,
    operacao TEXT,
    detalhes TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
"""

# Tabela de Backups
SQL_CREATE_BACKUPS = """
CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_arquivo TEXT NOT NULL,
    caminho_completo TEXT NOT NULL,
    tamanho_bytes INTEGER,
    hash_backup TEXT,
    tipo TEXT DEFAULT 'manual',
    usuario_id INTEGER,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
"""

# Tabela de Campos de Templates (PDF Form Builder)
SQL_CREATE_TEMPLATE_FIELDS = """
CREATE TABLE IF NOT EXISTS template_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    field_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    font_size INTEGER DEFAULT 12,
    required INTEGER DEFAULT 0,
    placeholder TEXT,
    default_value TEXT,
    options TEXT,
    validation TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates_pdf(id) ON DELETE CASCADE
);
"""

# Índice para otimizar consultas por template_id
SQL_CREATE_INDEX_TEMPLATE_FIELDS = """
CREATE INDEX IF NOT EXISTS idx_template_fields_template_id
ON template_fields(template_id);
"""

# Índices adicionais para otimização de performance
SQL_CREATE_INDEX_DOCUMENTOS_CODIGO = """
CREATE INDEX IF NOT EXISTS idx_documentos_codigo
ON documentos(codigo_unico);
"""

SQL_CREATE_INDEX_DOCUMENTOS_PACIENTE = """
CREATE INDEX IF NOT EXISTS idx_documentos_paciente
ON documentos(paciente_id);
"""

SQL_CREATE_INDEX_DOCUMENTOS_DATA = """
CREATE INDEX IF NOT EXISTS idx_documentos_data
ON documentos(data_emissao DESC);
"""

SQL_CREATE_INDEX_PACIENTES_PREC = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_pacientes_prec
ON pacientes(prec_cp);
"""

SQL_CREATE_INDEX_USUARIOS_LOGIN = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_login
ON usuarios(login);
"""

SQL_CREATE_INDEX_LOGS_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_logs_usuario
ON logs(usuario_id, data_hora DESC);
"""

SQL_CREATE_INDEX_AUDITORIA_DOCUMENTO = """
CREATE INDEX IF NOT EXISTS idx_auditoria_documento
ON auditoria(documento_id, data_auditoria DESC);
"""

SQL_CREATE_INDEX_BACKUPS_DATA = """
CREATE INDEX IF NOT EXISTS idx_backups_data
ON backups(data_criacao DESC);
"""

# Lista de todos os comandos SQL para criar tabelas e índices
ALL_TABLES = [
    SQL_CREATE_CONFIG,
    SQL_CREATE_USUARIOS,
    SQL_CREATE_SETORES,
    SQL_CREATE_PACIENTES,
    SQL_CREATE_PROFISSIONAIS,
    SQL_CREATE_DOCUMENTOS,
    SQL_CREATE_AUDITORIA,
    SQL_CREATE_TEMPLATES,
    SQL_CREATE_TEMPLATE_FIELDS,
    SQL_CREATE_LOGS,
    SQL_CREATE_BACKUPS,
    SQL_CREATE_INDEX_TEMPLATE_FIELDS,
    SQL_CREATE_INDEX_DOCUMENTOS_CODIGO,
    SQL_CREATE_INDEX_DOCUMENTOS_PACIENTE,
    SQL_CREATE_INDEX_DOCUMENTOS_DATA,
    SQL_CREATE_INDEX_PACIENTES_PREC,
    SQL_CREATE_INDEX_USUARIOS_LOGIN,
    SQL_CREATE_INDEX_LOGS_USUARIO,
    SQL_CREATE_INDEX_AUDITORIA_DOCUMENTO,
    SQL_CREATE_INDEX_BACKUPS_DATA
]

