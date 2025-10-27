# -*- coding: utf-8 -*-
"""
Gerador de PDFs
Cria documentos PDF padronizados com cabeçalho e rodapé
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os
from src.config import DIRECTORIES, CORES


def gerar_pdf_documento(codigo_documento, tipo_documento, dados_documento, caminho_saida=None):
    """
    Gera um PDF padronizado para o documento
    
    Parâmetros:
    - codigo_documento: código único do documento (ex: HGUMBA-EXAM-2025-0001)
    - tipo_documento: tipo do documento (ex: Guia de Exame)
    - dados_documento: dicionário com os dados do documento
    - caminho_saida: caminho onde salvar o PDF (opcional)
    
    Retorna: caminho do arquivo PDF gerado
    """
    
    # Definir caminho de saída
    if not caminho_saida:
        nome_arquivo = f"{codigo_documento}.pdf"
        caminho_saida = os.path.join(DIRECTORIES['pdfs'], nome_arquivo)
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    # Criar canvas do PDF
    c = canvas.Canvas(caminho_saida, pagesize=A4)
    largura, altura = A4
    
    # ========================================================================
    # CABEÇALHO
    # ========================================================================
    
    # Linha superior verde-oliva
    c.setFillColor(colors.HexColor(CORES['primaria']))
    c.rect(0, altura - 2*cm, largura, 2*cm, fill=True, stroke=False)
    
    # Texto do cabeçalho (branco)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    
    # Nome do hospital (obtido das configurações)
    from src.core.database import obter_configuracao
    nome_hospital = obter_configuracao('nome_hospital', 'Hospital Militar')
    sigla_oms = obter_configuracao('sigla_oms', '')
    
    c.drawCentredString(largura/2, altura - 1.2*cm, nome_hospital)
    
    if sigla_oms:
        c.setFont("Helvetica", 10)
        c.drawCentredString(largura/2, altura - 1.6*cm, f"OMS: {sigla_oms}")
    
    # ========================================================================
    # CORPO DO DOCUMENTO
    # ========================================================================
    
    # Voltar para cor preta
    c.setFillColor(colors.black)
    
    # Título do documento
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura/2, altura - 3.5*cm, tipo_documento.upper())
    
    # Código do documento
    c.setFont("Helvetica", 10)
    c.drawCentredString(largura/2, altura - 4*cm, f"Código: {codigo_documento}")
    
    # Linha horizontal
    c.line(2*cm, altura - 4.5*cm, largura - 2*cm, altura - 4.5*cm)
    
    # Dados do documento
    y_posicao = altura - 5.5*cm
    c.setFont("Helvetica", 11)
    
    # Renderizar dados conforme o tipo de documento
    if tipo_documento == 'Guia de Exame':
        y_posicao = _renderizar_guia_exame(c, dados_documento, y_posicao, largura)
    elif tipo_documento == 'Encaminhamento Médico':
        y_posicao = _renderizar_encaminhamento(c, dados_documento, y_posicao, largura)
    elif tipo_documento == 'Guia de Internação':
        y_posicao = _renderizar_guia_internacao(c, dados_documento, y_posicao, largura)
    elif tipo_documento == 'Declaração':
        y_posicao = _renderizar_declaracao(c, dados_documento, y_posicao, largura)
    elif tipo_documento == 'Atestado Administrativo':
        y_posicao = _renderizar_atestado(c, dados_documento, y_posicao, largura)
    
    # ========================================================================
    # RODAPÉ
    # ========================================================================
    
    # Data e hora de emissão
    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, 2*cm, f"Emitido em: {data_emissao}")
    
    # Hash do documento (simplificado)
    import hashlib
    hash_doc = hashlib.sha256(codigo_documento.encode()).hexdigest()[:16]
    c.drawString(2*cm, 1.5*cm, f"Hash: {hash_doc}")
    
    # Linha inferior
    c.setStrokeColor(colors.HexColor(CORES['primaria']))
    c.line(2*cm, 1*cm, largura - 2*cm, 1*cm)
    
    # Texto rodapé
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(largura/2, 0.6*cm, "Documento gerado pelo Sistema HGU Digital Core")
    
    # Finalizar e salvar PDF
    c.save()
    
    print(f"✓ PDF gerado: {caminho_saida}")
    return caminho_saida


def _renderizar_guia_exame(c, dados, y_pos, largura):
    """Renderiza dados específicos da Guia de Exame"""
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Dados do Paciente:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, f"Nome: {dados.get('paciente_nome', '')}")
    y_pos -= 0.5*cm
    c.drawString(2.5*cm, y_pos, f"PREC-CP: {dados.get('paciente_prec', '')}")
    y_pos -= 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Exame Solicitado:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, dados.get('exame_solicitado', ''))
    y_pos -= 0.8*cm
    
    if dados.get('observacoes'):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y_pos, "Observações:")
        y_pos -= 0.6*cm
        
        c.setFont("Helvetica", 10)
        c.drawString(2.5*cm, y_pos, dados.get('observacoes', ''))
        y_pos -= 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Profissional Solicitante:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, f"{dados.get('profissional_nome', '')} - {dados.get('profissional_crm', '')}")
    y_pos -= 0.5*cm
    
    return y_pos


def _renderizar_encaminhamento(c, dados, y_pos, largura):
    """Renderiza dados específicos do Encaminhamento Médico"""
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Paciente:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, f"{dados.get('paciente_nome', '')} - PREC: {dados.get('paciente_prec', '')}")
    y_pos -= 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Encaminhado para:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, dados.get('setor_destino', ''))
    y_pos -= 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Motivo:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    # Quebrar texto longo em múltiplas linhas
    motivo = dados.get('motivo', '')
    if len(motivo) > 80:
        palavras = motivo.split()
        linha_atual = ""
        for palavra in palavras:
            if len(linha_atual + palavra) < 80:
                linha_atual += palavra + " "
            else:
                c.drawString(2.5*cm, y_pos, linha_atual)
                y_pos -= 0.5*cm
                linha_atual = palavra + " "
        if linha_atual:
            c.drawString(2.5*cm, y_pos, linha_atual)
            y_pos -= 0.5*cm
    else:
        c.drawString(2.5*cm, y_pos, motivo)
        y_pos -= 0.5*cm
    
    return y_pos


def _renderizar_guia_internacao(c, dados, y_pos, largura):
    """Renderiza dados específicos da Guia de Internação"""
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Dados do Paciente:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, f"Nome: {dados.get('paciente_nome', '')}")
    y_pos -= 0.5*cm
    c.drawString(2.5*cm, y_pos, f"PREC-CP: {dados.get('paciente_prec', '')}")
    y_pos -= 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Diagnóstico:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, dados.get('diagnostico', ''))
    y_pos -= 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y_pos, "Previsão de Internação:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y_pos, f"{dados.get('dias_previstos', '')} dias")
    y_pos -= 0.5*cm
    
    return y_pos


def _renderizar_declaracao(c, dados, y_pos, largura):
    """Renderiza dados específicos da Declaração"""
    
    c.setFont("Helvetica", 11)
    
    # Texto da declaração
    texto = dados.get('texto_declaracao', '')
    
    # Quebrar em linhas
    palavras = texto.split()
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual + palavra) < 90:
            linha_atual += palavra + " "
        else:
            c.drawString(2*cm, y_pos, linha_atual)
            y_pos -= 0.6*cm
            linha_atual = palavra + " "
    
    if linha_atual:
        c.drawString(2*cm, y_pos, linha_atual)
        y_pos -= 0.6*cm
    
    y_pos -= 1*cm
    
    # Assinatura
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y_pos, "Declarado por:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y_pos, dados.get('profissional_nome', ''))
    y_pos -= 0.4*cm
    c.drawString(2*cm, y_pos, dados.get('profissional_funcao', ''))
    
    return y_pos


def _renderizar_atestado(c, dados, y_pos, largura):
    """Renderiza dados específicos do Atestado Administrativo"""
    
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y_pos, f"Atesto que {dados.get('paciente_nome', '')}, PREC-CP {dados.get('paciente_prec', '')},")
    y_pos -= 0.6*cm
    
    motivo = dados.get('motivo_atestado', '')
    c.drawString(2*cm, y_pos, motivo)
    y_pos -= 0.8*cm
    
    c.drawString(2*cm, y_pos, f"Período: {dados.get('data_inicio', '')} a {dados.get('data_fim', '')}")
    y_pos -= 1.5*cm
    
    # Assinatura
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y_pos, "Atestado por:")
    y_pos -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y_pos, f"{dados.get('profissional_nome', '')} - {dados.get('profissional_crm', '')}")
    
    return y_pos

