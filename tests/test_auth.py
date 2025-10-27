# -*- coding: utf-8 -*-
"""
Testes de Autenticação
Testa login, logout e controle de acesso
"""

import pytest
from src.core.database import criar_usuario_admin, criar_usuario


class TestLogin:
    """Testes da funcionalidade de login"""

    def test_login_page_loads(self, client):
        """Testa se a página de login carrega"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_success(self, client):
        """Testa login com credenciais corretas"""
        # Criar usuário
        criar_usuario_admin('test_admin', 'TestPass123!', 'Admin Teste')

        # Tentar login
        response = client.post('/login', json={
            'login': 'test_admin',
            'senha': 'TestPass123!'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['sucesso'] is True

    def test_login_wrong_password(self, client):
        """Testa login com senha incorreta"""
        # Criar usuário
        criar_usuario_admin('test_admin2', 'TestPass123!', 'Admin Teste 2')

        # Tentar login com senha errada
        response = client.post('/login', json={
            'login': 'test_admin2',
            'senha': 'SenhaErrada123!'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['sucesso'] is False

    def test_login_nonexistent_user(self, client):
        """Testa login com usuário inexistente"""
        response = client.post('/login', json={
            'login': 'usuario_nao_existe',
            'senha': 'QualquerSenha123!'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['sucesso'] is False

    def test_login_missing_fields(self, client):
        """Testa login com campos faltando"""
        response = client.post('/login', json={
            'login': 'test_user'
            # senha faltando
        })

        assert response.status_code == 400


class TestLogout:
    """Testes da funcionalidade de logout"""

    def test_logout(self, auth_client):
        """Testa logout de usuário autenticado"""
        response = auth_client.get('/logout')
        assert response.status_code == 302  # Redirect


class TestAccessControl:
    """Testes de controle de acesso"""

    def test_dashboard_requires_login(self, client):
        """Testa se dashboard requer autenticação"""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect para login

    def test_dashboard_with_login(self, auth_client):
        """Testa acesso ao dashboard com login"""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200

    def test_auditoria_requires_admin_or_auditor(self, client):
        """Testa se auditoria requer nível de acesso adequado"""
        # Criar usuário visualizador
        criar_usuario('Visualizador', 'visualizador', 'TestPass123!', 'visualizador')

        # Fazer login como visualizador
        client.post('/login', json={
            'login': 'visualizador',
            'senha': 'TestPass123!'
        })

        # Tentar acessar auditoria
        response = client.get('/auditoria')
        assert response.status_code == 403  # Forbidden
