# -*- coding: utf-8 -*-
"""
Configuração de Testes (Pytest Fixtures)
Define fixtures compartilhadas entre todos os testes
"""

import pytest
import os
import sys
import tempfile

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """
    Fixture que cria uma instância da aplicação Flask para testes
    """
    from app import app as flask_app
    from config import DATABASE

    # Configurar para modo de teste
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Desabilitar CSRF para testes

    # Usar banco de dados em memória para testes
    db_fd, db_path = tempfile.mkstemp()
    DATABASE['name'] = db_path

    # Criar tabelas
    from database import inicializar_db
    inicializar_db()

    yield flask_app

    # Limpeza
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """
    Fixture que cria um cliente de teste Flask
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture que cria um runner CLI de teste
    """
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """
    Fixture que retorna um cliente autenticado como administrador
    """
    # Criar usuário admin de teste
    from database import criar_usuario_admin

    criar_usuario_admin('admin_test', 'TestPass123!', 'Administrador Teste')

    # Fazer login
    client.post('/login', json={
        'login': 'admin_test',
        'senha': 'TestPass123!'
    })

    return client
