# -*- coding: utf-8 -*-
"""
Módulo de Rotas
Organiza as rotas da aplicação em blueprints separados
"""

from flask import Blueprint

# Os blueprints serão importados aqui
__all__ = ['auth_bp', 'documentos_bp', 'pacientes_bp', 'profissionais_bp', 'pdf_builder_bp', 'auditoria_bp']
