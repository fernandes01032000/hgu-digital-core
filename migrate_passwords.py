# -*- coding: utf-8 -*-
"""
Script de Migração de Senhas
Converte senhas existentes de SHA256 para Bcrypt

USO: python migrate_passwords.py
IMPORTANTE: Execute este script apenas UMA VEZ após atualizar o sistema
"""

import sqlite3
import sys
import os
from getpass import getpass

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE
from database import get_db_connection, init_bcrypt
from flask import Flask

print("=" * 70)
print("MIGRAÇÃO DE SENHAS - SHA256 → Bcrypt")
print("=" * 70)
print()
print("Este script irá resetar a senha de todos os usuários")
print("Você precisará fornecer uma nova senha para cada usuário")
print()
print("ATENÇÃO: Esta operação não pode ser desfeita!")
print()

resposta = input("Deseja continuar? (s/N): ").strip().lower()
if resposta != 's':
    print("Operação cancelada.")
    sys.exit(0)

print()

# Criar aplicação Flask temporária para inicializar bcrypt
app = Flask(__name__)
app.secret_key = 'temporary-key-for-migration'
bcrypt = init_bcrypt(app)

try:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Buscar todos os usuários ativos
        cursor.execute("""
            SELECT id, nome, login, nivel_acesso
            FROM usuarios
            WHERE ativo = 1
            ORDER BY id
        """)

        usuarios = cursor.fetchall()

        if not usuarios:
            print("Nenhum usuário encontrado no banco de dados.")
            sys.exit(0)

        print(f"Encontrados {len(usuarios)} usuário(s) para migração:")
        print()

        senhas_atualizadas = []

        for usuario in usuarios:
            print(f"Usuário: {usuario['nome']}")
            print(f"Login: {usuario['login']}")
            print(f"Nível: {usuario['nivel_acesso']}")

            while True:
                senha1 = getpass("Nova senha (mínimo 8 caracteres): ")

                if len(senha1) < 8:
                    print("❌ Senha deve ter no mínimo 8 caracteres!")
                    continue

                senha2 = getpass("Confirme a senha: ")

                if senha1 != senha2:
                    print("❌ Senhas não conferem!")
                    continue

                # Validar complexidade
                has_upper = any(c.isupper() for c in senha1)
                has_lower = any(c.islower() for c in senha1)
                has_digit = any(c.isdigit() for c in senha1)

                if not (has_upper and has_lower and has_digit):
                    print("❌ Senha deve conter pelo menos:")
                    print("   - Uma letra maiúscula")
                    print("   - Uma letra minúscula")
                    print("   - Um número")
                    continue

                break

            # Gerar hash bcrypt
            senha_hash = bcrypt.generate_password_hash(senha1).decode('utf-8')

            senhas_atualizadas.append((senha_hash, usuario['id']))
            print(f"✓ Senha definida para {usuario['login']}")
            print()

        # Atualizar todas as senhas
        print("Atualizando banco de dados...")
        for senha_hash, usuario_id in senhas_atualizadas:
            cursor.execute("""
                UPDATE usuarios
                SET senha_hash = ?
                WHERE id = ?
            """, (senha_hash, usuario_id))

        conn.commit()

        print()
        print("=" * 70)
        print(f"✓ Migração concluída! {len(senhas_atualizadas)} senha(s) atualizada(s)")
        print("=" * 70)
        print()
        print("Agora você pode fazer login com as novas senhas.")

except Exception as e:
    print(f"\n❌ Erro durante a migração: {e}")
    sys.exit(1)
