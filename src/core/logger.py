# -*- coding: utf-8 -*-
"""
Sistema de Logging
Configura logging em arquivo e console
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from src.config import LOGS, DIRECTORIES


def setup_logging(app=None):
    """
    Configura o sistema de logging

    Args:
        app: Instância da aplicação Flask (opcional)

    Returns:
        logging.Logger: Logger configurado
    """
    # Criar diretório de logs se não existir
    os.makedirs(DIRECTORIES['logs'], exist_ok=True)

    # Configurar formato de log
    log_format = logging.Formatter(LOGS['formato'])

    # Criar handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        LOGS['arquivo'],
        maxBytes=LOGS['max_bytes'],
        backupCount=LOGS['backup_count'],
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(getattr(logging, LOGS['nivel']))

    # Criar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)

    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Se app Flask foi fornecido, configurar seu logger também
    if app:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(getattr(logging, LOGS['nivel']))

    logging.info("Sistema de logging inicializado")
    return root_logger


def log_security_event(event_type, message, user_id=None, ip_address=None, extra_data=None):
    """
    Registra evento de segurança

    Args:
        event_type: Tipo do evento (login, logout, failed_login, access_denied, etc.)
        message: Mensagem descritiva
        user_id: ID do usuário (se aplicável)
        ip_address: Endereço IP
        extra_data: Dados adicionais (dicionário)
    """
    logger = logging.getLogger('security')

    log_data = {
        'event': event_type,
        'message': message,
        'user_id': user_id,
        'ip': ip_address,
    }

    if extra_data:
        log_data.update(extra_data)

    logger.warning(f"SECURITY: {log_data}")


def log_api_call(endpoint, method, user_id=None, ip_address=None, status_code=None, duration=None):
    """
    Registra chamada de API

    Args:
        endpoint: Endpoint da API
        method: Método HTTP
        user_id: ID do usuário
        ip_address: Endereço IP
        status_code: Código de status HTTP
        duration: Duração da requisição em ms
    """
    logger = logging.getLogger('api')

    log_data = {
        'endpoint': endpoint,
        'method': method,
        'user_id': user_id,
        'ip': ip_address,
        'status': status_code,
        'duration_ms': duration
    }

    logger.info(f"API: {log_data}")


def log_database_error(operation, error, query=None):
    """
    Registra erro de banco de dados

    Args:
        operation: Operação que falhou
        error: Exceção ou mensagem de erro
        query: Query SQL (opcional, para debug)
    """
    logger = logging.getLogger('database')

    log_data = {
        'operation': operation,
        'error': str(error),
    }

    if query:
        log_data['query'] = query

    logger.error(f"DATABASE ERROR: {log_data}")
