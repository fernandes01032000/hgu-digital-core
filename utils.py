# -*- coding: utf-8 -*-
"""
Utilitários do Sistema HGU Digital Core
Funções auxiliares para operações comuns
"""

import socket
import secrets
import string
from contextlib import closing


def find_free_port(start_port=8080, max_attempts=100):
    """
    Encontra uma porta disponível no sistema

    Args:
        start_port: Porta inicial para começar a busca
        max_attempts: Número máximo de tentativas

    Returns:
        int: Número da porta disponível

    Raises:
        RuntimeError: Se não encontrar porta disponível
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(1)
                # Tenta fazer bind na porta
                sock.bind(('0.0.0.0', port))
                # Se conseguiu, a porta está livre
                return port
        except OSError:
            # Porta em uso, tentar próxima
            continue

    raise RuntimeError(f"Não foi possível encontrar porta disponível após {max_attempts} tentativas")


def generate_secret_key(length=64):
    """
    Gera uma chave secreta aleatória forte

    Args:
        length: Tamanho da chave em caracteres

    Returns:
        str: Chave secreta gerada
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_salt(length=32):
    """
    Gera um salt aleatório para hash de senhas

    Args:
        length: Tamanho do salt em caracteres

    Returns:
        str: Salt gerado
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_local_ip():
    """
    Obtém o endereço IP local da máquina

    Returns:
        str: Endereço IP local ou '127.0.0.1' se não conseguir detectar
    """
    try:
        # Cria um socket UDP (não precisa estar conectado)
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            # Não precisa realmente conectar, só para obter o IP local
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
            return ip
    except Exception:
        return '127.0.0.1'


def validate_prec_cp(prec_cp):
    """
    Valida o formato do PREC-CP (Número de Identificação Militar)

    Args:
        prec_cp: String com o PREC-CP

    Returns:
        bool: True se válido, False caso contrário
    """
    if not prec_cp or not isinstance(prec_cp, str):
        return False

    # Remove espaços e traços
    prec_clean = prec_cp.replace('-', '').replace(' ', '').replace('.', '')

    # PREC-CP deve ter entre 6 e 12 dígitos
    if not prec_clean.isdigit():
        return False

    if len(prec_clean) < 6 or len(prec_clean) > 12:
        return False

    return True


def sanitize_filename(filename):
    """
    Remove caracteres perigosos de nomes de arquivo

    Args:
        filename: Nome do arquivo

    Returns:
        str: Nome do arquivo sanitizado
    """
    # Caracteres permitidos: letras, números, underscore, hífen e ponto
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    sanitized = ''.join(c for c in filename if c in valid_chars)

    # Remove múltiplos pontos consecutivos (possível path traversal)
    while '..' in sanitized:
        sanitized = sanitized.replace('..', '.')

    return sanitized.strip()
