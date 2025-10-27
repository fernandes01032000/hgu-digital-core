# -*- coding: utf-8 -*-
"""
PDF Form Builder - Módulo Backend
Gerencia templates PDF e geração de formulários preenchidos
"""

import os
import json
import logging
from datetime import datetime
from io import BytesIO
import base64

from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black

from config import DIRECTORIES
from database import get_db_connection

logger = logging.getLogger(__name__)


# ============================================================================
# FUNÇÕES DE TEMPLATE
# ============================================================================

def criar_template(nome, descricao, pdf_file, usuario_id):
    """
    Cria um novo template PDF

    Args:
        nome: Nome do template
        descricao: Descrição do template
        pdf_file: FileStorage object do Flask
        usuario_id: ID do usuário criador

    Returns:
        dict com informações do template criado

    Raises:
        ValueError: Se o PDF for inválido
    """
    # Validar PDF
    try:
        pdf_bytes = pdf_file.read()
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        num_pages = len(pdf_reader.pages)

        # Obter dimensões da primeira página
        first_page = pdf_reader.pages[0]
        media_box = first_page.mediabox
        width = float(media_box.width)
        height = float(media_box.height)

        pdf_file.seek(0)  # Reset file pointer

    except Exception as e:
        logger.error(f"Erro ao validar PDF: {e}")
        raise ValueError(f"PDF inválido ou corrompido: {str(e)}")

    # Gerar nome único para arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"template_{timestamp}_{usuario_id}.pdf"
    filepath = os.path.join(DIRECTORIES['templates_pdfs'], filename)

    # Salvar arquivo
    os.makedirs(DIRECTORIES['templates_pdfs'], exist_ok=True)
    pdf_file.save(filepath)
    file_size = os.path.getsize(filepath)

    # Criar registro no banco
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO templates_pdf (nome, descricao, caminho_arquivo, mapeamento_campos, ativo)
            VALUES (?, ?, ?, ?, 1)
        """, (nome, descricao, filepath, json.dumps([])))
        conn.commit()
        template_id = cursor.lastrowid

    logger.info(f"Template criado: {template_id} - {nome} ({num_pages} páginas)")

    return {
        'id': template_id,
        'nome': nome,
        'descricao': descricao,
        'num_pages': num_pages,
        'width': width,
        'height': height,
        'file_size': file_size,
        'filename': filename
    }


def listar_templates(incluir_inativos=False):
    """
    Lista todos os templates

    Args:
        incluir_inativos: Se True, inclui templates desativados

    Returns:
        Lista de dicts com informações dos templates
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if incluir_inativos:
            cursor.execute("""
                SELECT
                    id, nome, descricao, caminho_arquivo,
                    ativo, data_criacao, mapeamento_campos
                FROM templates_pdf
                ORDER BY data_criacao DESC
            """)
        else:
            cursor.execute("""
                SELECT
                    id, nome, descricao, caminho_arquivo,
                    ativo, data_criacao, mapeamento_campos
                FROM templates_pdf
                WHERE ativo = 1
                ORDER BY data_criacao DESC
            """)

        rows = cursor.fetchall()

        templates = []
        for row in rows:
            # Contar campos
            campos = json.loads(row['mapeamento_campos'] or '[]')
            num_campos = len(campos)

            # Obter tamanho do arquivo
            file_size = 0
            if os.path.exists(row['caminho_arquivo']):
                file_size = os.path.getsize(row['caminho_arquivo'])

            templates.append({
                'id': row['id'],
                'nome': row['nome'],
                'descricao': row['descricao'],
                'caminho_arquivo': row['caminho_arquivo'],
                'ativo': bool(row['ativo']),
                'data_criacao': row['data_criacao'],
                'num_campos': num_campos,
                'file_size': file_size
            })

        return templates


def obter_template(template_id):
    """
    Obtém informações completas de um template

    Args:
        template_id: ID do template

    Returns:
        dict com informações do template ou None se não encontrado
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                id, nome, descricao, caminho_arquivo,
                mapeamento_campos, ativo, data_criacao
            FROM templates_pdf
            WHERE id = ?
        """, (template_id,))

        row = cursor.fetchone()

        if not row:
            return None

        # Carregar campos
        campos = json.loads(row['mapeamento_campos'] or '[]')

        # Obter informações do PDF
        file_size = 0
        num_pages = 0
        width = 0
        height = 0

        if os.path.exists(row['caminho_arquivo']):
            file_size = os.path.getsize(row['caminho_arquivo'])

            try:
                with open(row['caminho_arquivo'], 'rb') as f:
                    pdf_reader = PdfReader(f)
                    num_pages = len(pdf_reader.pages)

                    first_page = pdf_reader.pages[0]
                    media_box = first_page.mediabox
                    width = float(media_box.width)
                    height = float(media_box.height)
            except Exception as e:
                logger.error(f"Erro ao ler PDF: {e}")

        return {
            'id': row['id'],
            'nome': row['nome'],
            'descricao': row['descricao'],
            'caminho_arquivo': row['caminho_arquivo'],
            'campos': campos,
            'ativo': bool(row['ativo']),
            'data_criacao': row['data_criacao'],
            'file_size': file_size,
            'num_pages': num_pages,
            'width': width,
            'height': height
        }


def obter_pdf_template(template_id):
    """
    Obtém o arquivo PDF de um template

    Args:
        template_id: ID do template

    Returns:
        bytes do PDF ou None se não encontrado
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT caminho_arquivo
            FROM templates_pdf
            WHERE id = ?
        """, (template_id,))

        row = cursor.fetchone()

        if not row or not os.path.exists(row['caminho_arquivo']):
            return None

        with open(row['caminho_arquivo'], 'rb') as f:
            return f.read()


def atualizar_template(template_id, nome=None, descricao=None, ativo=None):
    """
    Atualiza informações de um template

    Args:
        template_id: ID do template
        nome: Novo nome (opcional)
        descricao: Nova descrição (opcional)
        ativo: Novo status ativo (opcional)

    Returns:
        bool indicando sucesso
    """
    # Whitelist de campos permitidos para prevenir SQL injection
    allowed_updates = {
        'nome': nome,
        'descricao': descricao,
        'ativo': 1 if ativo else 0 if ativo is not None else None
    }

    # Construir query segura apenas com campos permitidos
    updates = []
    params = []

    for field, value in allowed_updates.items():
        if value is not None:
            updates.append(f"{field} = ?")
            params.append(value)

    if not updates:
        return True

    params.append(template_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Query segura - campos são hardcoded, apenas valores são parametrizados
        query = f"UPDATE templates_pdf SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

        return cursor.rowcount > 0


def deletar_template(template_id):
    """
    Deleta um template (soft delete - marca como inativo)

    Args:
        template_id: ID do template

    Returns:
        bool indicando sucesso
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE templates_pdf
            SET ativo = 0
            WHERE id = ?
        """, (template_id,))
        conn.commit()

        success = cursor.rowcount > 0

        if success:
            logger.info(f"Template deletado (soft): {template_id}")

        return success


def duplicar_template(template_id, usuario_id):
    """
    Duplica um template existente

    Args:
        template_id: ID do template original
        usuario_id: ID do usuário que está duplicando

    Returns:
        dict com informações do novo template ou None se falhar
    """
    # Obter template original
    original = obter_template(template_id)
    if not original:
        return None

    # Copiar arquivo PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"template_{timestamp}_{usuario_id}_copy.pdf"
    new_filepath = os.path.join(DIRECTORIES['templates_pdfs'], new_filename)

    try:
        with open(original['caminho_arquivo'], 'rb') as src:
            with open(new_filepath, 'wb') as dst:
                dst.write(src.read())
    except Exception as e:
        logger.error(f"Erro ao copiar PDF: {e}")
        return None

    # Criar novo template no banco
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO templates_pdf (nome, descricao, caminho_arquivo, mapeamento_campos, ativo)
            VALUES (?, ?, ?, ?, 1)
        """, (
            f"{original['nome']} (Cópia)",
            original['descricao'],
            new_filepath,
            json.dumps(original['campos'])
        ))
        conn.commit()
        new_template_id = cursor.lastrowid

    logger.info(f"Template duplicado: {template_id} -> {new_template_id}")

    return obter_template(new_template_id)


# ============================================================================
# FUNÇÕES DE CAMPOS
# ============================================================================

def salvar_campos_template(template_id, campos):
    """
    Salva os campos de um template

    Args:
        template_id: ID do template
        campos: Lista de dicts com informações dos campos

    Returns:
        bool indicando sucesso
    """
    # Validar que o template existe
    if not obter_template(template_id):
        return False

    # Converter campos para JSON
    campos_json = json.dumps(campos, ensure_ascii=False)

    # Atualizar no banco
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE templates_pdf
            SET mapeamento_campos = ?
            WHERE id = ?
        """, (campos_json, template_id))
        conn.commit()

        success = cursor.rowcount > 0

        if success:
            logger.info(f"Campos salvos para template {template_id}: {len(campos)} campos")

        return success


def obter_campos_template(template_id):
    """
    Obtém os campos de um template

    Args:
        template_id: ID do template

    Returns:
        Lista de dicts com informações dos campos
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mapeamento_campos
            FROM templates_pdf
            WHERE id = ?
        """, (template_id,))

        row = cursor.fetchone()

        if not row:
            return []

        return json.loads(row['mapeamento_campos'] or '[]')


# ============================================================================
# GERAÇÃO DE PDF PREENCHIDO
# ============================================================================

def gerar_pdf_preenchido(template_id, form_data):
    """
    Gera um PDF preenchido com os dados do formulário

    Args:
        template_id: ID do template
        form_data: Dict com valores dos campos {field_id: value}

    Returns:
        bytes do PDF gerado ou None se falhar

    Raises:
        ValueError: Se template não encontrado ou dados inválidos
    """
    # Obter template
    template = obter_template(template_id)
    if not template:
        raise ValueError(f"Template {template_id} não encontrado")

    # Carregar PDF original
    pdf_path = template['caminho_arquivo']
    if not os.path.exists(pdf_path):
        raise ValueError(f"Arquivo PDF não encontrado: {pdf_path}")

    try:
        # Ler PDF original
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            pdf_writer = PdfWriter()

            # Obter primeira página
            page = pdf_reader.pages[0]
            media_box = page.mediabox
            page_width = float(media_box.width)
            page_height = float(media_box.height)

            # Criar overlay com ReportLab
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))

            # Desenhar cada campo
            campos = template['campos']

            for campo in campos:
                field_id = campo.get('field_id')
                value = form_data.get(field_id)

                # Pular campos vazios
                if value is None or value == '':
                    continue

                # Obter propriedades do campo
                field_type = campo.get('type')
                x = campo.get('x', 0)
                y = campo.get('y', 0)
                width = campo.get('width', 100)
                height = campo.get('height', 20)
                font_size = campo.get('font_size', 12)

                # Converter coordenadas (PDF Y-axis é invertido)
                pdf_y = page_height - y - height

                # Configurar fonte
                can.setFont("Helvetica", font_size)
                can.setFillColor(black)

                # Renderizar baseado no tipo
                if field_type == 'text' or field_type == 'textarea':
                    _desenhar_texto(can, str(value), x, pdf_y, width, height, font_size)

                elif field_type == 'checkbox':
                    _desenhar_checkbox(can, bool(value), x, pdf_y, height, font_size)

                elif field_type == 'radio':
                    _desenhar_texto(can, str(value), x, pdf_y, width, height, font_size)

                elif field_type == 'dropdown':
                    _desenhar_texto(can, str(value), x, pdf_y, width, height, font_size)

                elif field_type == 'date':
                    _desenhar_data(can, value, x, pdf_y, width, height, font_size)

                elif field_type == 'signature':
                    _desenhar_assinatura(can, value, x, pdf_y, width, height)

                elif field_type == 'image':
                    _desenhar_imagem(can, value, x, pdf_y, width, height)

            # Finalizar canvas
            can.save()
            packet.seek(0)

            # Merge overlay com PDF original
            overlay_pdf = PdfReader(packet)
            page.merge_page(overlay_pdf.pages[0])
            pdf_writer.add_page(page)

            # Adicionar páginas restantes (se houver)
            for i in range(1, len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[i])

            # Retornar bytes
            output = BytesIO()
            pdf_writer.write(output)
            output.seek(0)

            logger.info(f"PDF gerado com sucesso para template {template_id}")

            return output.read()

    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        raise ValueError(f"Erro ao gerar PDF: {str(e)}")


# ============================================================================
# FUNÇÕES AUXILIARES DE DESENHO
# ============================================================================

def _desenhar_texto(can, texto, x, y, width, height, font_size):
    """Desenha texto no PDF"""
    # Ajustar posição Y para centralizar verticalmente
    y_adjusted = y + (height / 2) - (font_size / 3)
    can.drawString(x + 2, y_adjusted, texto)


def _desenhar_checkbox(can, checked, x, y, height, font_size):
    """Desenha checkbox no PDF"""
    y_adjusted = y + (height / 2) - (font_size / 3)
    if checked:
        can.drawString(x, y_adjusted, '☑')
    else:
        can.drawString(x, y_adjusted, '☐')


def _desenhar_data(can, data_str, x, y, width, height, font_size):
    """Desenha data formatada no PDF"""
    try:
        # Formatar data se necessário
        if isinstance(data_str, str):
            # Assume ISO format ou já formatado
            texto = data_str
        else:
            texto = str(data_str)

        _desenhar_texto(can, texto, x, y, width, height, font_size)
    except Exception as e:
        logger.warning(f"Erro ao formatar data: {e}")
        _desenhar_texto(can, str(data_str), x, y, width, height, font_size)


def _desenhar_assinatura(can, data_url, x, y, width, height):
    """Desenha assinatura (imagem base64) no PDF"""
    try:
        # Extrair imagem do data URL
        if data_url.startswith('data:image'):
            # Format: data:image/png;base64,iVBORw0KGgo...
            header, encoded = data_url.split(',', 1)
            image_data = base64.b64decode(encoded)

            # Criar arquivo temporário
            temp_path = os.path.join(DIRECTORIES['pdfs'], f'temp_sig_{datetime.now().timestamp()}.png')

            with open(temp_path, 'wb') as f:
                f.write(image_data)

            # Desenhar imagem
            can.drawImage(temp_path, x, y, width=width, height=height, preserveAspectRatio=True)

            # Remover arquivo temporário
            try:
                os.remove(temp_path)
            except:
                pass

    except Exception as e:
        logger.error(f"Erro ao desenhar assinatura: {e}")
        # Fallback: desenhar texto
        can.setFont("Helvetica-Oblique", 10)
        can.drawString(x, y + height/2, "[Assinatura]")


def _desenhar_imagem(can, data_url, x, y, width, height):
    """Desenha imagem (base64) no PDF"""
    try:
        # Similar à assinatura
        if data_url.startswith('data:image'):
            header, encoded = data_url.split(',', 1)
            image_data = base64.b64decode(encoded)

            temp_path = os.path.join(DIRECTORIES['pdfs'], f'temp_img_{datetime.now().timestamp()}.png')

            with open(temp_path, 'wb') as f:
                f.write(image_data)

            can.drawImage(temp_path, x, y, width=width, height=height, preserveAspectRatio=True)

            try:
                os.remove(temp_path)
            except:
                pass

    except Exception as e:
        logger.error(f"Erro ao desenhar imagem: {e}")
        can.setFont("Helvetica-Oblique", 10)
        can.drawString(x, y + height/2, "[Imagem]")


# ============================================================================
# FUNÇÕES DE UPLOAD DE IMAGEM
# ============================================================================

def processar_upload_imagem(image_file):
    """
    Processa upload de imagem e retorna data URL

    Args:
        image_file: FileStorage object do Flask

    Returns:
        str data URL (base64)

    Raises:
        ValueError: Se imagem for inválida
    """
    try:
        # Validar imagem
        img = Image.open(image_file)

        # Redimensionar se muito grande (max 800x800)
        max_size = 800
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Converter para PNG
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        # Converter para base64
        encoded = base64.b64encode(output.read()).decode('utf-8')
        data_url = f"data:image/png;base64,{encoded}"

        return data_url

    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        raise ValueError(f"Imagem inválida: {str(e)}")
