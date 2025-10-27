# -*- coding: utf-8 -*-
"""
Módulo de Segurança
Implementa headers de segurança e outras proteções
"""

from functools import wraps
from flask import request, abort
import logging

logger = logging.getLogger(__name__)


def add_security_headers(response):
    """
    Adiciona headers de segurança HTTP às respostas

    Args:
        response: Objeto de resposta Flask

    Returns:
        response com headers de segurança adicionados
    """
    # Previne que o browser faça MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Previne clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Ativa proteção XSS do browser
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Content Security Policy (CSP)
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: blob:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self';"
    )
    response.headers['Content-Security-Policy'] = csp_policy

    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Permissions Policy (Feature Policy)
    response.headers['Permissions-Policy'] = (
        'geolocation=(), '
        'microphone=(), '
        'camera=(), '
        'payment=()'
    )

    return response


def validate_content_type(allowed_types):
    """
    Decorador para validar Content-Type de uploads

    Args:
        allowed_types: Lista de MIME types permitidos

    Usage:
        @validate_content_type(['application/pdf'])
        def upload_pdf():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                abort(400, 'Nenhum arquivo enviado')

            file = request.files['file']

            # Ler magic bytes para validar tipo real do arquivo
            file_header = file.read(16)
            file.seek(0)

            # Validar PDF
            if 'application/pdf' in allowed_types:
                if not file_header.startswith(b'%PDF'):
                    logger.warning(f"Tentativa de upload de arquivo não-PDF: {file.filename}")
                    abort(400, 'Arquivo não é um PDF válido')

            # Validar imagens
            if any(t.startswith('image/') for t in allowed_types):
                image_signatures = {
                    b'\x89PNG\r\n\x1a\n': 'image/png',
                    b'\xff\xd8\xff': 'image/jpeg',
                    b'GIF87a': 'image/gif',
                    b'GIF89a': 'image/gif',
                }

                valid_image = False
                for signature, mime_type in image_signatures.items():
                    if file_header.startswith(signature) and mime_type in allowed_types:
                        valid_image = True
                        break

                if not valid_image and any(t.startswith('image/') for t in allowed_types):
                    logger.warning(f"Tentativa de upload de arquivo inválido: {file.filename}")
                    abort(400, 'Arquivo de imagem inválido')

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def sanitize_filename(filename):
    """
    Sanitiza nome de arquivo para prevenir path traversal

    Args:
        filename: Nome original do arquivo

    Returns:
        str: Nome sanitizado
    """
    import string
    import os

    # Remover path (pegar apenas o nome do arquivo)
    filename = os.path.basename(filename)

    # Caracteres permitidos
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    sanitized = ''.join(c for c in filename if c in valid_chars)

    # Remover múltiplos pontos (prevenir path traversal)
    while '..' in sanitized:
        sanitized = sanitized.replace('..', '.')

    # Limitar tamanho
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext

    return sanitized.strip()


def check_password_strength(password):
    """
    Verifica força da senha

    Args:
        password: Senha em texto plano

    Returns:
        tuple: (bool válida, str mensagem)
    """
    if len(password) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"

    if len(password) > 128:
        return False, "Senha muito longa (máximo 128 caracteres)"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

    if not has_upper:
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not has_lower:
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not has_digit:
        return False, "Senha deve conter pelo menos um número"

    if not has_special:
        return False, "Senha deve conter pelo menos um caractere especial"

    # Verificar senhas comuns
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin123', 'letmein', 'welcome', 'monkey', '1234567890'
    ]

    if password.lower() in common_passwords:
        return False, "Senha muito comum, escolha outra"

    return True, "Senha válida"


def log_security_event(event_type, message, user_id=None, ip_address=None, extra_data=None):
    """
    Registra evento de segurança

    Args:
        event_type: Tipo do evento (login_success, login_failed, etc)
        message: Mensagem descritiva
        user_id: ID do usuário (opcional)
        ip_address: IP do cliente (opcional)
        extra_data: Dados adicionais (opcional)
    """
    log_data = {
        'event_type': event_type,
        'event_message': message,
        'user_id': user_id,
        'ip_address': ip_address,
        'extra_data': extra_data
    }

    # Log com nível baseado no tipo de evento
    if event_type in ['login_failed', 'access_denied', 'csrf_failed']:
        logger.warning(f"[SECURITY] {message}", extra=log_data)
    elif event_type in ['sql_injection_attempt', 'path_traversal_attempt']:
        logger.error(f"[SECURITY ALERT] {message}", extra=log_data)
    else:
        logger.info(f"[SECURITY] {message}", extra=log_data)
