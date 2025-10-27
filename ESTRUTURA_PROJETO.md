# 📁 Estrutura do Projeto HGU Digital Core

Estrutura organizada e profissional após refatoração completa.

```
hgu-digital-core/
│
├── 📄 Arquivos de Configuração Raiz
│   ├── .env                      # Variáveis de ambiente (não versionado)
│   ├── .env.example              # Template de configuração
│   ├── .gitignore               # Arquivos ignorados pelo Git
│   ├── Makefile                 # Comandos úteis (make help)
│   ├── pytest.ini               # Configuração de testes
│   ├── requirements.txt         # Dependências de produção
│   └── requirements-dev.txt     # Dependências de desenvolvimento
│
├── 📚 Documentação Principal
│   ├── README.md                # Documentação completa do projeto
│   ├── CHANGELOG.md             # Histórico de versões
│   ├── SECURITY.md              # Guia de segurança
│   └── AUDITORIA_SEGURANCA.md   # Relatório de auditoria
│
├── 📂 docs/                     # Documentação Técnica
│   ├── BOOTSTRAP_IMPLEMENTATION.md
│   ├── PDF_BUILDER_API.md
│   ├── RELATORIO_ATUALIZACAO.md
│   └── research/                # Documentos de pesquisa
│       ├── Pesquisa sistema hospitalar.pdf
│       └── Relatório_Técnico_Proposta...pdf
│
├── 🔧 scripts/                  # Scripts Utilitários
│   ├── migrate_passwords.py     # Migração de senhas
│   └── migrate_pdf_builder.py   # Migração PDF Builder
│
├── 🐍 src/                      # Código-Fonte Python
│   ├── __init__.py
│   ├── config.py                # Configurações do sistema
│   ├── models.py                # Modelos de dados (schemas DB)
│   ├── schemas.py               # Validação de dados (Marshmallow)
│   │
│   ├── core/                    # Módulos Principais
│   │   ├── __init__.py
│   │   ├── database.py          # Operações de banco de dados
│   │   ├── security.py          # Segurança e headers
│   │   ├── logger.py            # Sistema de logging
│   │   └── backup.py            # Sistema de backup
│   │
│   ├── routes/                  # Rotas da API
│   │   ├── __init__.py
│   │   └── auth.py              # Rotas de autenticação
│   │
│   ├── services/                # Lógica de Negócio
│   │   ├── __init__.py
│   │   ├── pdf_generator.py     # Geração de PDFs
│   │   └── pdf_builder.py       # Builder de formulários PDF
│   │
│   └── utils/                   # Utilitários
│       ├── __init__.py
│       └── helpers.py           # Funções auxiliares
│
├── 🎨 static/                   # Arquivos Estáticos
│   ├── css/
│   │   ├── bootstrap-custom.css
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── pdf-builder/             # Frontend React
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── src/
│           ├── lib/
│           └── types/
│
├── 🖼️ templates/                # Templates Jinja2
│   ├── base.html               # Template base
│   ├── _navbar.html            # Componente navbar
│   ├── login.html
│   ├── setup.html
│   ├── dashboard.html
│   ├── pacientes.html
│   ├── profissionais.html
│   ├── documentos.html
│   ├── pdf_builder.html
│   ├── auditoria.html
│   ├── relatorios.html
│   └── error.html
│
├── 🧪 tests/                    # Testes Automatizados
│   ├── __init__.py
│   ├── conftest.py             # Fixtures do Pytest
│   ├── test_auth.py            # Testes de autenticação
│   ├── test_database.py        # Testes de banco de dados
│   ├── test_schemas.py         # Testes de validação
│   └── test_utils.py           # Testes de utilitários
│
├── 🗂️ Diretórios de Dados (não versionados)
│   ├── backups/                # Backups do banco de dados
│   ├── logs/                   # Logs do sistema
│   ├── pdfs/                   # PDFs gerados
│   └── templates_pdfs/         # Templates de PDF uploadados
│
└── 🚀 app.py                    # Aplicação Principal Flask
```

## 📊 Estatísticas

- **Total de Arquivos Python**: ~25 arquivos
- **Linhas de Código**: ~5.300 linhas
- **Módulos Principais**: 4 (core, routes, services, utils)
- **Testes**: 40+ testes automatizados
- **Documentação**: 8 arquivos markdown

## 🎯 Benefícios da Nova Estrutura

### ✅ Organização
- Código separado por responsabilidades
- Estrutura modular e escalável
- Fácil navegação e manutenção

### ✅ Profissionalismo
- Segue padrões da indústria
- Estrutura similar a projetos Python profissionais
- Preparado para crescimento

### ✅ Manutenibilidade
- Imports claros e organizados
- Fácil adicionar novos módulos
- Testabilidade melhorada

### ✅ Separação de Conceitos
- **src/core**: Funcionalidades essenciais do sistema
- **src/services**: Lógica de negócio específica
- **src/routes**: Endpoints da API
- **src/utils**: Funções auxiliares reutilizáveis

## 🔧 Como Usar

### Executar o Servidor
```bash
python app.py
```

### Executar Testes
```bash
pytest
# ou
make test
```

### Instalar Dependências
```bash
# Produção
pip install -r requirements.txt

# Desenvolvimento
pip install -r requirements-dev.txt
```

### Executar Scripts
```bash
python scripts/migrate_passwords.py
python scripts/migrate_pdf_builder.py
```

## 📚 Documentação

- **Início Rápido**: Ver seção Quick Start no [README.md](README.md)
- **Segurança**: [SECURITY.md](SECURITY.md)
- **Auditoria**: [AUDITORIA_SEGURANCA.md](AUDITORIA_SEGURANCA.md)
- **API**: [docs/PDF_BUILDER_API.md](docs/PDF_BUILDER_API.md)
- **Histórico**: [CHANGELOG.md](CHANGELOG.md)

---

**Estrutura criada em**: 2025-01-26  
**Versão**: 2.0.0  
**Status**: ✅ Produção Ready
