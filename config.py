# -*- coding: utf-8 -*-
"""
Arquivo de Configuração do Sistema HGU Digital Core
Contém todas as configurações básicas do sistema
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações do Banco de Dados
DATABASE = {
    'name': os.path.join(BASE_DIR, os.getenv('DATABASE_NAME', 'hgu_core.db')),
    'timeout': 30.0,  # Timeout para operações do banco
    'check_same_thread': False  # Permite uso de threads
}

# Configurações do Servidor Flask
SERVER = {
    'host': os.getenv('HOST', '0.0.0.0'),
    'port': int(os.getenv('PORT', 8080)),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true'
}

# Diretórios do Sistema
DIRECTORIES = {
    'pdfs': os.path.join(BASE_DIR, 'pdfs'),
    'backups': os.path.join(BASE_DIR, 'backups'),
    'templates_pdfs': os.path.join(BASE_DIR, 'templates_pdfs'),
    'static': os.path.join(BASE_DIR, 'static'),
    'templates': os.path.join(BASE_DIR, 'templates'),
    'logs': os.path.join(BASE_DIR, 'logs')
}

# Configurações de Segurança
SECURITY = {
    'secret_key': os.getenv('SECRET_KEY'),
    'salt': os.getenv('SALT'),
    # Configurações de sessão
    'session_cookie_secure': not SERVER['debug'],  # HTTPS only em produção
    'session_cookie_httponly': True,  # Previne acesso via JavaScript
    'session_cookie_samesite': 'Lax',  # Proteção CSRF
    'permanent_session_lifetime': int(os.getenv('SESSION_TIMEOUT', 3600)),  # 1 hora padrão
    # Bcrypt
    'bcrypt_log_rounds': 12,  # Custo do hash (quanto maior, mais seguro e lento)
}

# Configurações do Sistema (valores padrão)
SYSTEM_CONFIG = {
    'nome_hospital': '',
    'sigla_oms': '',
    'regiao_militar': '',
    'comando_vinculado': '',
    'diretor_tecnico': '',
    'responsavel_ti': '',
    'prefixo_documentos': 'HGU',
    'timezone': 'America/Sao_Paulo',
    'configurado': False  # Indica se o setup inicial foi concluído
}

# Setores Padrão do Hospital
SETORES_PADRAO = [
    'UPAT',
    'ABAS',
    'UI',
    'Centro Cirúrgico',
    'LAB-DI',
    'ODONTO',
    'FISIO',
    'MAT-OBS',
    'FARM'
]

# Tipos de Documentos Disponíveis
TIPOS_DOCUMENTOS = [
    'Guia de Exame',
    'Encaminhamento Médico',
    'Guia de Internação',
    'Declaração',
    'Atestado Administrativo'
]

# Status de Documentos para Auditoria
STATUS_AUDITORIA = [
    'Emitido',
    'Aprovado',
    'Indeferido',
    'Revisado'
]

# Níveis de Acesso (RBAC)
NIVEIS_ACESSO = {
    'administrador': 'Administrador',
    'medico': 'Médico',
    'auditor': 'Auditor',
    'visualizador': 'Visualizador'
}

# Configurações de Rate Limiting
RATE_LIMITING = {
    'login_attempts': int(os.getenv('RATE_LIMIT_LOGIN', 5)),  # Tentativas de login
    'login_window': int(os.getenv('RATE_LIMIT_WINDOW', 300)),  # Janela em segundos (5 min)
    'default_limits': ['200 per day', '50 per hour'],  # Limites gerais da API
    'storage_uri': 'memory://',  # Usar memória para rate limiting
}

# Configurações de Backup
BACKUP = {
    'automatico': True,  # Ativa backup automático
    'hora': '23:00',     # Hora do backup automático
    'retencao_dias': 30  # Dias para manter backups antigos
}

# Configurações de Logs
LOGS = {
    'retencao_meses': 12,  # Meses para manter logs
    'arquivo': os.path.join(DIRECTORIES['logs'], 'sistema.log'),
    'nivel': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_bytes': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5  # Manter 5 arquivos de log rotacionados
}

# Cores do Sistema (identidade visual)
CORES = {
    'primaria': '#556B2F',    # Verde-oliva
    'secundaria': '#FFFFFF',  # Branco
    'terciaria': '#E5E5E5',   # Cinza claro
    'texto': '#333333'        # Cinza escuro
}

# Validação de Configurações Críticas
def validar_configuracao():
    """
    Valida se as configurações críticas estão definidas
    Gera automaticamente se não existir arquivo .env
    """
    import sys
    from utils import generate_secret_key, generate_salt

    env_file = os.path.join(BASE_DIR, '.env')

    # Se não existir .env, criar com valores gerados
    if not os.path.exists(env_file):
        print("⚠️  Arquivo .env não encontrado. Gerando configurações...")

        secret_key = generate_secret_key()
        salt = generate_salt()

        with open(env_file, 'w') as f:
            f.write(f"# Configurações de Segurança - GERADO AUTOMATICAMENTE\n")
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write(f"SALT={salt}\n\n")
            f.write(f"# Configurações do Servidor\n")
            f.write(f"DEBUG=False\n")
            f.write(f"HOST=0.0.0.0\n")
            f.write(f"PORT=8080\n\n")
            f.write(f"# Outras configurações\n")
            f.write(f"DATABASE_NAME=hgu_core.db\n")
            f.write(f"SESSION_TIMEOUT=3600\n")
            f.write(f"TIMEZONE=America/Sao_Paulo\n")

        print("✓ Arquivo .env criado com sucesso!")
        print("⚠️  IMPORTANTE: Reinicie o servidor para carregar as novas configurações.")

        # Recarregar variáveis de ambiente
        load_dotenv(override=True)

    # Validar se SECRET_KEY e SALT estão definidos
    if not SECURITY['secret_key'] or not SECURITY['salt']:
        print("\n❌ ERRO CRÍTICO DE CONFIGURAÇÃO!")
        print("As variáveis SECRET_KEY e SALT não estão definidas no arquivo .env")
        print("\nPor favor:")
        print("1. Copie o arquivo .env.example para .env")
        print("2. Gere valores aleatórios para SECRET_KEY e SALT")
        print("3. Ou delete o arquivo .env para gerar automaticamente")
        sys.exit(1)

    # Criar diretórios necessários
    for dir_path in DIRECTORIES.values():
        os.makedirs(dir_path, exist_ok=True)

# Executar validação ao importar
validar_configuracao()

