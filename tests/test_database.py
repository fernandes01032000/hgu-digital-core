# -*- coding: utf-8 -*-
"""
Testes do Banco de Dados
Testa operações de banco de dados
"""

import pytest
from database import (
    get_db_connection, criar_usuario_admin, criar_usuario,
    verificar_senha, cadastrar_paciente, cadastrar_profissional,
    criar_setores_padrao, listar_setores
)


class TestUsuarios:
    """Testes de gerenciamento de usuários"""

    def test_criar_usuario_admin(self, app):
        """Testa criação de usuário administrador"""
        with app.app_context():
            usuario_id = criar_usuario_admin('admin', 'AdminPass123!', 'Administrador')
            assert usuario_id is not None

            # Verificar se usuário foi criado
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE login = ?", ('admin',))
                usuario = cursor.fetchone()

                assert usuario is not None
                assert usuario['nome'] == 'Administrador'
                assert usuario['nivel_acesso'] == 'administrador'

    def test_verificar_senha_correta(self, app):
        """Testa verificação de senha correta"""
        with app.app_context():
            criar_usuario_admin('admin2', 'CorrectPass123!', 'Admin 2')

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT senha_hash FROM usuarios WHERE login = ?", ('admin2',))
                usuario = cursor.fetchone()

                assert verificar_senha('CorrectPass123!', usuario['senha_hash']) is True

    def test_verificar_senha_incorreta(self, app):
        """Testa verificação de senha incorreta"""
        with app.app_context():
            criar_usuario_admin('admin3', 'CorrectPass123!', 'Admin 3')

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT senha_hash FROM usuarios WHERE login = ?", ('admin3',))
                usuario = cursor.fetchone()

                assert verificar_senha('WrongPass123!', usuario['senha_hash']) is False


class TestPacientes:
    """Testes de gerenciamento de pacientes"""

    def test_cadastrar_paciente(self, app):
        """Testa cadastro de paciente"""
        with app.app_context():
            paciente_id = cadastrar_paciente(
                nome_completo='João da Silva',
                prec_cp='123456789',
                posto='Soldado',
                om='1º Batalhão'
            )

            assert paciente_id is not None

            # Verificar se foi cadastrado
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
                paciente = cursor.fetchone()

                assert paciente is not None
                assert paciente['nome_completo'] == 'João da Silva'
                assert paciente['prec_cp'] == '123456789'


class TestProfissionais:
    """Testes de gerenciamento de profissionais"""

    def test_cadastrar_profissional(self, app):
        """Testa cadastro de profissional"""
        with app.app_context():
            prof_id = cadastrar_profissional(
                nome='Dr. Carlos Santos',
                funcao='Médico',
                crm_coren='CRM-BA 12345',
                posto_graduacao='Capitão'
            )

            assert prof_id is not None

            # Verificar se foi cadastrado
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM profissionais WHERE id = ?", (prof_id,))
                prof = cursor.fetchone()

                assert prof is not None
                assert prof['nome'] == 'Dr. Carlos Santos'
                assert prof['funcao'] == 'Médico'


class TestSetores:
    """Testes de gerenciamento de setores"""

    def test_criar_setores_padrao(self, app):
        """Testa criação de setores padrão"""
        with app.app_context():
            criar_setores_padrao()

            setores = listar_setores()
            assert len(setores) > 0

            # Verificar se setores esperados existem
            nomes_setores = [s['nome'] for s in setores]
            assert 'UPAT' in nomes_setores
            assert 'ABAS' in nomes_setores
