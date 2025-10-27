# Makefile para HGU Digital Core
# Comandos úteis para desenvolvimento e produção

.PHONY: help install run test clean backup migrate

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    - Instala dependências"
	@echo "  make run        - Inicia o servidor"
	@echo "  make test       - Executa testes"
	@echo "  make clean      - Limpa arquivos temporários"
	@echo "  make backup     - Cria backup do banco de dados"
	@echo "  make migrate    - Migra senhas para bcrypt"

install:
	@echo "Instalando dependências..."
	pip install -r requirements.txt
	@echo "✓ Dependências instaladas"

run:
	@echo "Iniciando servidor..."
	python app.py

test:
	@echo "Executando testes..."
	pytest

test-cov:
	@echo "Executando testes com cobertura..."
	pytest --cov=. --cov-report=html --cov-report=term

clean:
	@echo "Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✓ Limpeza concluída"

backup:
	@echo "Criando backup..."
	python -c "from backup import realizar_backup; realizar_backup(tipo='manual')"
	@echo "✓ Backup criado"

migrate:
	@echo "Migrando senhas para bcrypt..."
	python migrate_passwords.py

setup-dev:
	@echo "Configurando ambiente de desenvolvimento..."
	pip install -r requirements.txt
	@if [ ! -f .env ]; then \
		echo "Criando arquivo .env..."; \
		cp .env.example .env; \
		echo "⚠️  Configure o arquivo .env antes de iniciar"; \
	fi
	@echo "✓ Ambiente configurado"

lint:
	@echo "Verificando código..."
	@which flake8 > /dev/null || pip install flake8
	flake8 . --exclude=venv,env --max-line-length=120
	@echo "✓ Verificação concluída"
