# -*- coding: utf-8 -*-
"""
Schemas de Validação de Dados
Usa Marshmallow para validar dados de entrada da API
"""

from marshmallow import Schema, fields, validates, ValidationError, validate
from src.utils.helpers import validate_prec_cp


class LoginSchema(Schema):
    """Schema para validação de login"""
    login = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    senha = fields.Str(required=True, validate=validate.Length(min=6, max=100))


class SetupSchema(Schema):
    """Schema para configuração inicial do sistema"""
    nome_hospital = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    sigla_oms = fields.Str(required=False, validate=validate.Length(max=50))
    regiao_militar = fields.Str(required=False, validate=validate.Length(max=100))
    comando_vinculado = fields.Str(required=False, validate=validate.Length(max=200))
    diretor_tecnico = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    responsavel_ti = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    prefixo_documentos = fields.Str(required=False, validate=validate.Length(min=2, max=10))
    admin_login = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    admin_senha = fields.Str(required=True, validate=validate.Length(min=8, max=100))
    admin_nome = fields.Str(required=True, validate=validate.Length(min=3, max=200))

    @validates('admin_senha')
    def validate_admin_senha(self, value):
        """Validação adicional para senha forte"""
        if len(value) < 8:
            raise ValidationError("Senha deve ter no mínimo 8 caracteres")

        # Verificar complexidade básica
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)

        if not (has_upper and has_lower and has_digit):
            raise ValidationError(
                "Senha deve conter pelo menos uma letra maiúscula, "
                "uma letra minúscula e um número"
            )


class PacienteSchema(Schema):
    """Schema para cadastro de paciente"""
    nome_completo = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    prec_cp = fields.Str(required=True, validate=validate.Length(min=6, max=20))
    posto = fields.Str(required=False, validate=validate.Length(max=50))
    om = fields.Str(required=False, validate=validate.Length(max=100))
    data_nascimento = fields.Date(required=False, format='%Y-%m-%d')
    observacoes = fields.Str(required=False, validate=validate.Length(max=1000))

    @validates('prec_cp')
    def validate_prec_cp_format(self, value):
        """Validação do formato PREC-CP"""
        if not validate_prec_cp(value):
            raise ValidationError(
                "PREC-CP inválido. Deve conter entre 6 e 12 dígitos"
            )


class ProfissionalSchema(Schema):
    """Schema para cadastro de profissional"""
    nome = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    funcao = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    crm_coren = fields.Str(required=False, validate=validate.Length(max=50))
    posto_graduacao = fields.Str(required=False, validate=validate.Length(max=50))
    setor_id = fields.Int(required=False, allow_none=True)


class DocumentoSchema(Schema):
    """Schema para criação de documento"""
    tipo_documento = fields.Str(
        required=True,
        validate=validate.OneOf([
            'Guia de Exame',
            'Encaminhamento Médico',
            'Guia de Internação',
            'Declaração',
            'Atestado Administrativo'
        ])
    )
    paciente_id = fields.Int(required=True)
    profissional_id = fields.Int(required=True)
    setor_origem_id = fields.Int(required=True)
    setor_destino_id = fields.Int(required=False, allow_none=True)
    conteudo = fields.Dict(required=True)


class UsuarioSchema(Schema):
    """Schema para criação de usuário"""
    nome = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    login = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    senha = fields.Str(required=True, validate=validate.Length(min=8, max=100))
    nivel_acesso = fields.Str(
        required=True,
        validate=validate.OneOf(['administrador', 'medico', 'auditor', 'visualizador'])
    )

    @validates('senha')
    def validate_senha(self, value):
        """Validação de senha forte"""
        if len(value) < 8:
            raise ValidationError("Senha deve ter no mínimo 8 caracteres")

        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)

        if not (has_upper and has_lower and has_digit):
            raise ValidationError(
                "Senha deve conter pelo menos uma letra maiúscula, "
                "uma letra minúscula e um número"
            )


class AuditoriaSchema(Schema):
    """Schema para auditoria de documento"""
    documento_id = fields.Int(required=True)
    status_novo = fields.Str(
        required=True,
        validate=validate.OneOf(['Emitido', 'Aprovado', 'Indeferido', 'Revisado'])
    )
    motivo_glosa = fields.Str(required=False, validate=validate.Length(max=1000))
    comentarios = fields.Str(required=False, validate=validate.Length(max=2000))


# ============================================================================
# SCHEMAS PDF BUILDER
# ============================================================================

class PDFTemplateUploadSchema(Schema):
    """Schema para upload de template PDF"""
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    description = fields.Str(required=False, validate=validate.Length(max=1000))


class TemplateFieldSchema(Schema):
    """Schema para campo de template"""
    field_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'text', 'textarea', 'checkbox', 'radio',
            'dropdown', 'date', 'signature', 'image'
        ])
    )
    x = fields.Int(required=True, validate=validate.Range(min=0))
    y = fields.Int(required=True, validate=validate.Range(min=0))
    width = fields.Int(required=True, validate=validate.Range(min=10, max=2000))
    height = fields.Int(required=True, validate=validate.Range(min=10, max=2000))
    font_size = fields.Int(required=False, validate=validate.Range(min=8, max=72))
    required = fields.Bool(required=False)
    placeholder = fields.Str(required=False, validate=validate.Length(max=500))
    default_value = fields.Str(required=False, validate=validate.Length(max=1000))
    options = fields.List(fields.Str(), required=False)
    validation = fields.Dict(required=False)


class SaveTemplateFieldsSchema(Schema):
    """Schema para salvar campos de template"""
    fields = fields.List(fields.Nested(TemplateFieldSchema), required=True)


class GeneratePDFSchema(Schema):
    """Schema para geração de PDF preenchido"""
    template_id = fields.Int(required=True)
    form_data = fields.Dict(required=True)


def validate_request(schema_class):
    """
    Decorador para validar requisições usando schemas Marshmallow

    Usage:
        @app.route('/api/pacientes/cadastrar', methods=['POST'])
        @validate_request(PacienteSchema)
        def cadastrar_paciente(validated_data):
            # validated_data contém os dados já validados
            pass

    Args:
        schema_class: Classe do schema Marshmallow a ser usada

    Returns:
        Decorador de função
    """
    from functools import wraps
    from flask import request, jsonify

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()

            try:
                # Obter dados JSON da requisição
                dados = request.get_json()
                if not dados:
                    return jsonify({
                        'sucesso': False,
                        'mensagem': 'Nenhum dado JSON fornecido'
                    }), 400

                # Validar dados
                validated_data = schema.load(dados)

                # Chamar função original com dados validados
                return f(validated_data, *args, **kwargs)

            except ValidationError as err:
                # Retornar erros de validação
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Erro de validação',
                    'erros': err.messages
                }), 400
            except Exception as e:
                return jsonify({
                    'sucesso': False,
                    'mensagem': f'Erro ao processar requisição: {str(e)}'
                }), 500

        return decorated_function
    return decorator
