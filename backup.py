# -*- coding: utf-8 -*-
"""
Sistema de Backup Automático
Realiza backups do banco de dados e arquivos importantes
"""

import os
import shutil
import hashlib
import sqlite3
import logging
from datetime import datetime, timedelta
from config import DATABASE, DIRECTORIES, BACKUP
from database import get_db_connection

logger = logging.getLogger(__name__)


def calcular_hash_arquivo(caminho_arquivo):
    """
    Calcula hash SHA256 de um arquivo

    Args:
        caminho_arquivo: Caminho do arquivo

    Returns:
        str: Hash hex do arquivo
    """
    sha256 = hashlib.sha256()

    with open(caminho_arquivo, 'rb') as f:
        for bloco in iter(lambda: f.read(65536), b''):
            sha256.update(bloco)

    return sha256.hexdigest()


def realizar_backup(usuario_id=None, tipo='manual'):
    """
    Realiza backup do banco de dados

    Args:
        usuario_id: ID do usuário que solicitou o backup (None para automático)
        tipo: Tipo do backup ('manual' ou 'automatico')

    Returns:
        dict: Informações sobre o backup realizado
    """
    try:
        # Gerar nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_backup = f"backup_{timestamp}.db"
        caminho_backup = os.path.join(DIRECTORIES['backups'], nome_backup)

        # Garantir que diretório existe
        os.makedirs(DIRECTORIES['backups'], exist_ok=True)

        logger.info(f"Iniciando backup: {nome_backup}")

        # Fazer cópia do banco de dados usando SQLite backup API
        origem = sqlite3.connect(DATABASE['name'])
        destino = sqlite3.connect(caminho_backup)

        with destino:
            origem.backup(destino)

        origem.close()
        destino.close()

        # Calcular hash do backup
        hash_backup = calcular_hash_arquivo(caminho_backup)

        # Obter tamanho do arquivo
        tamanho_bytes = os.path.getsize(caminho_backup)

        # Registrar backup no banco de dados
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backups (
                    nome_arquivo, caminho_completo, tamanho_bytes,
                    hash_backup, tipo, usuario_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nome_backup, caminho_backup, tamanho_bytes,
                hash_backup, tipo, usuario_id
            ))
            backup_id = cursor.lastrowid
            conn.commit()

        info_backup = {
            'id': backup_id,
            'nome_arquivo': nome_backup,
            'caminho': caminho_backup,
            'tamanho_bytes': tamanho_bytes,
            'tamanho_mb': round(tamanho_bytes / (1024 * 1024), 2),
            'hash': hash_backup,
            'data': datetime.now().isoformat()
        }

        logger.info(f"Backup concluído: {nome_backup} ({info_backup['tamanho_mb']} MB)")

        return info_backup

    except Exception as e:
        logger.error(f"Erro ao realizar backup: {e}")
        raise


def limpar_backups_antigos():
    """
    Remove backups mais antigos que o período de retenção configurado
    """
    try:
        dias_retencao = BACKUP['retencao_dias']
        data_limite = datetime.now() - timedelta(days=dias_retencao)

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Buscar backups antigos
            cursor.execute("""
                SELECT id, nome_arquivo, caminho_completo
                FROM backups
                WHERE data_criacao < ?
            """, (data_limite,))

            backups_antigos = cursor.fetchall()

            if not backups_antigos:
                logger.info("Nenhum backup antigo para remover")
                return 0

            removidos = 0
            for backup in backups_antigos:
                try:
                    # Remover arquivo físico
                    if os.path.exists(backup['caminho_completo']):
                        os.remove(backup['caminho_completo'])

                    # Remover registro do banco
                    cursor.execute("DELETE FROM backups WHERE id = ?", (backup['id'],))
                    removidos += 1

                    logger.info(f"Backup antigo removido: {backup['nome_arquivo']}")

                except Exception as e:
                    logger.error(f"Erro ao remover backup {backup['nome_arquivo']}: {e}")

            conn.commit()

            logger.info(f"{removidos} backup(s) antigo(s) removido(s)")
            return removidos

    except Exception as e:
        logger.error(f"Erro ao limpar backups antigos: {e}")
        return 0


def listar_backups():
    """
    Lista todos os backups disponíveis

    Returns:
        list: Lista de dicionários com informações dos backups
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    b.id,
                    b.nome_arquivo,
                    b.tamanho_bytes,
                    b.hash_backup,
                    b.tipo,
                    b.data_criacao,
                    u.nome as usuario_nome
                FROM backups b
                LEFT JOIN usuarios u ON b.usuario_id = u.id
                ORDER BY b.data_criacao DESC
            """)

            backups = cursor.fetchall()

            return [{
                'id': b['id'],
                'nome_arquivo': b['nome_arquivo'],
                'tamanho_mb': round(b['tamanho_bytes'] / (1024 * 1024), 2),
                'hash': b['hash_backup'][:16] + '...',  # Mostrar apenas primeiros 16 caracteres
                'tipo': b['tipo'],
                'data_criacao': b['data_criacao'],
                'usuario': b['usuario_nome'] or 'Sistema'
            } for b in backups]

    except Exception as e:
        logger.error(f"Erro ao listar backups: {e}")
        return []


def restaurar_backup(backup_id, usuario_id=None):
    """
    Restaura um backup específico

    ATENÇÃO: Esta operação substitui o banco de dados atual!

    Args:
        backup_id: ID do backup a restaurar
        usuario_id: ID do usuário que solicitou a restauração

    Returns:
        bool: True se restaurado com sucesso
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Buscar informações do backup
            cursor.execute("""
                SELECT nome_arquivo, caminho_completo, hash_backup
                FROM backups
                WHERE id = ?
            """, (backup_id,))

            backup = cursor.fetchone()

            if not backup:
                raise ValueError(f"Backup {backup_id} não encontrado")

            if not os.path.exists(backup['caminho_completo']):
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup['caminho_completo']}")

        # Verificar integridade do backup
        hash_atual = calcular_hash_arquivo(backup['caminho_completo'])
        if hash_atual != backup['hash_backup']:
            raise ValueError("Arquivo de backup corrompido! Hash não confere.")

        logger.warning(f"Restaurando backup: {backup['nome_arquivo']}")

        # Fazer backup do estado atual antes de restaurar
        info_backup_seguranca = realizar_backup(usuario_id, tipo='pre-restauracao')
        logger.info(f"Backup de segurança criado: {info_backup_seguranca['nome_arquivo']}")

        # Fechar todas as conexões antes de substituir o banco
        # (Nota: em produção, seria necessário parar o servidor)

        # Substituir banco de dados atual
        shutil.copy2(backup['caminho_completo'], DATABASE['name'])

        logger.info(f"Backup {backup['nome_arquivo']} restaurado com sucesso")

        return True

    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {e}")
        raise


def verificar_integridade_backup(backup_id):
    """
    Verifica a integridade de um arquivo de backup

    Args:
        backup_id: ID do backup a verificar

    Returns:
        dict: Resultado da verificação
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT nome_arquivo, caminho_completo, hash_backup
                FROM backups
                WHERE id = ?
            """, (backup_id,))

            backup = cursor.fetchone()

            if not backup:
                return {
                    'valido': False,
                    'mensagem': 'Backup não encontrado'
                }

            if not os.path.exists(backup['caminho_completo']):
                return {
                    'valido': False,
                    'mensagem': 'Arquivo de backup não encontrado no disco'
                }

            # Calcular hash atual
            hash_atual = calcular_hash_arquivo(backup['caminho_completo'])

            if hash_atual == backup['hash_backup']:
                return {
                    'valido': True,
                    'mensagem': 'Backup íntegro',
                    'hash': hash_atual
                }
            else:
                return {
                    'valido': False,
                    'mensagem': 'Arquivo corrompido - hash não confere',
                    'hash_esperado': backup['hash_backup'],
                    'hash_atual': hash_atual
                }

    except Exception as e:
        logger.error(f"Erro ao verificar integridade do backup: {e}")
        return {
            'valido': False,
            'mensagem': f'Erro: {str(e)}'
        }
