# -*- coding: utf-8 -*-
"""
Migration Script - PDF Builder
Adiciona a tabela template_fields ao banco de dados existente
"""

import sqlite3
import sys
import os

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import DATABASE
from src.models import SQL_CREATE_TEMPLATE_FIELDS, SQL_CREATE_INDEX_TEMPLATE_FIELDS


def migrate():
    """Executa a migration para adicionar suporte ao PDF Builder"""

    print("=" * 70)
    print("🔄 MIGRATION: PDF Builder")
    print("=" * 70)
    print()

    try:
        # Conectar ao banco
        conn = sqlite3.connect(DATABASE['name'])
        cursor = conn.cursor()

        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='template_fields'
        """)

        if cursor.fetchone():
            print("⚠️  Tabela 'template_fields' já existe. Migration não necessária.")
            conn.close()
            return True

        # Criar tabela template_fields
        print("📝 Criando tabela 'template_fields'...")
        cursor.execute(SQL_CREATE_TEMPLATE_FIELDS)
        print("   ✓ Tabela criada com sucesso")

        # Criar índice
        print("📝 Criando índice 'idx_template_fields_template_id'...")
        cursor.execute(SQL_CREATE_INDEX_TEMPLATE_FIELDS)
        print("   ✓ Índice criado com sucesso")

        # Commit
        conn.commit()
        print()
        print("✅ Migration concluída com sucesso!")
        print()
        print("Tabelas atualizadas:")
        print("  - template_fields (nova)")
        print("  - idx_template_fields_template_id (novo índice)")
        print()

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"\n❌ Erro ao executar migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
