# -*- coding: utf-8 -*-
"""
Testes de Validação (Schemas)
Testa schemas Marshmallow
"""

import pytest
from marshmallow import ValidationError
from schemas import (
    LoginSchema, PacienteSchema, ProfissionalSchema,
    SetupSchema, DocumentoSchema
)


class TestLoginSchema:
    """Testes do schema de login"""

    def test_login_valido(self):
        """Testa validação de login válido"""
        schema = LoginSchema()
        data = schema.load({
            'login': 'usuario_teste',
            'senha': 'senha123'
        })

        assert data['login'] == 'usuario_teste'
        assert data['senha'] == 'senha123'

    def test_login_campo_faltando(self):
        """Testa validação com campo faltando"""
        schema = LoginSchema()

        with pytest.raises(ValidationError):
            schema.load({'login': 'usuario_teste'})  # senha faltando

    def test_login_muito_curto(self):
        """Testa validação com login muito curto"""
        schema = LoginSchema()

        with pytest.raises(ValidationError):
            schema.load({
                'login': 'ab',  # Menos de 3 caracteres
                'senha': 'senha123'
            })


class TestPacienteSchema:
    """Testes do schema de paciente"""

    def test_paciente_valido(self):
        """Testa validação de paciente válido"""
        schema = PacienteSchema()
        data = schema.load({
            'nome_completo': 'João da Silva',
            'prec_cp': '123456789',
            'posto': 'Soldado',
            'om': '1º Batalhão'
        })

        assert data['nome_completo'] == 'João da Silva'
        assert data['prec_cp'] == '123456789'

    def test_prec_cp_invalido(self):
        """Testa validação de PREC-CP inválido"""
        schema = PacienteSchema()

        with pytest.raises(ValidationError):
            schema.load({
                'nome_completo': 'João da Silva',
                'prec_cp': '123',  # Muito curto
                'posto': 'Soldado'
            })


class TestSetupSchema:
    """Testes do schema de setup"""

    def test_senha_fraca(self):
        """Testa validação de senha fraca"""
        schema = SetupSchema()

        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                'nome_hospital': 'Hospital Teste',
                'diretor_tecnico': 'Dr. Teste',
                'responsavel_ti': 'TI Teste',
                'admin_login': 'admin',
                'admin_senha': 'senha',  # Senha fraca (sem maiúscula, número)
                'admin_nome': 'Administrador'
            })

        assert 'admin_senha' in exc_info.value.messages

    def test_senha_forte(self):
        """Testa validação de senha forte"""
        schema = SetupSchema()

        data = schema.load({
            'nome_hospital': 'Hospital Teste',
            'diretor_tecnico': 'Dr. Teste',
            'responsavel_ti': 'TI Teste',
            'admin_login': 'admin',
            'admin_senha': 'SenhaForte123!',  # Senha forte
            'admin_nome': 'Administrador'
        })

        assert data['admin_senha'] == 'SenhaForte123!'


class TestDocumentoSchema:
    """Testes do schema de documento"""

    def test_documento_valido(self):
        """Testa validação de documento válido"""
        schema = DocumentoSchema()

        data = schema.load({
            'tipo_documento': 'Guia de Exame',
            'paciente_id': 1,
            'profissional_id': 1,
            'setor_origem_id': 1,
            'conteudo': {'exame': 'Hemograma'}
        })

        assert data['tipo_documento'] == 'Guia de Exame'

    def test_tipo_documento_invalido(self):
        """Testa validação de tipo de documento inválido"""
        schema = DocumentoSchema()

        with pytest.raises(ValidationError):
            schema.load({
                'tipo_documento': 'Tipo Inválido',  # Tipo não permitido
                'paciente_id': 1,
                'profissional_id': 1,
                'setor_origem_id': 1,
                'conteudo': {}
            })
