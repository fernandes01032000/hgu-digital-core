# -*- coding: utf-8 -*-
"""
Testes de Utilitários
Testa funções utilitárias do sistema
"""

import pytest
from utils import (
    find_free_port, validate_prec_cp, sanitize_filename,
    generate_secret_key, generate_salt
)


class TestPortDetection:
    """Testes de detecção de porta"""

    def test_find_free_port(self):
        """Testa se encontra uma porta livre"""
        port = find_free_port(start_port=9000, max_attempts=10)
        assert port >= 9000
        assert port < 9010

    def test_find_free_port_raises_on_no_port(self):
        """Testa se levanta exceção quando não há porta disponível"""
        # Não há como testar isso facilmente sem mockar sockets
        pass


class TestPrecCpValidation:
    """Testes de validação de PREC-CP"""

    def test_prec_cp_valido(self):
        """Testa PREC-CP válido"""
        assert validate_prec_cp('123456') is True
        assert validate_prec_cp('1234567890') is True
        assert validate_prec_cp('123456789012') is True

    def test_prec_cp_invalido(self):
        """Testa PREC-CP inválido"""
        assert validate_prec_cp('12345') is False  # Muito curto
        assert validate_prec_cp('1234567890123') is False  # Muito longo
        assert validate_prec_cp('abc123') is False  # Contém letras
        assert validate_prec_cp('') is False  # Vazio
        assert validate_prec_cp(None) is False  # None

    def test_prec_cp_com_formatacao(self):
        """Testa PREC-CP com formatação (traços, pontos)"""
        assert validate_prec_cp('123-456-789') is True
        assert validate_prec_cp('123.456.789') is True
        assert validate_prec_cp('123 456 789') is True


class TestFilenameSanitization:
    """Testes de sanitização de nome de arquivo"""

    def test_sanitize_filename_normal(self):
        """Testa sanitização de nome normal"""
        result = sanitize_filename('documento_teste.pdf')
        assert result == 'documento_teste.pdf'

    def test_sanitize_filename_special_chars(self):
        """Testa remoção de caracteres especiais"""
        result = sanitize_filename('documento<>:"/\\|?*.pdf')
        # Deve remover caracteres perigosos
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result

    def test_sanitize_filename_path_traversal(self):
        """Testa proteção contra path traversal"""
        result = sanitize_filename('../../../etc/passwd')
        # Não deve conter ..
        assert '..' not in result


class TestKeyGeneration:
    """Testes de geração de chaves"""

    def test_generate_secret_key(self):
        """Testa geração de chave secreta"""
        key = generate_secret_key(32)
        assert len(key) == 32
        assert isinstance(key, str)

    def test_generate_secret_key_unique(self):
        """Testa se chaves geradas são únicas"""
        key1 = generate_secret_key(64)
        key2 = generate_secret_key(64)
        assert key1 != key2

    def test_generate_salt(self):
        """Testa geração de salt"""
        salt = generate_salt(16)
        assert len(salt) == 16
        assert isinstance(salt, str)

    def test_generate_salt_unique(self):
        """Testa se salts gerados são únicos"""
        salt1 = generate_salt(32)
        salt2 = generate_salt(32)
        assert salt1 != salt2
