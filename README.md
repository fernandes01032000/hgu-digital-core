# 🏛️ HGU Digital Core v2.0

**Sistema de Gestão Hospitalar Militar - 100% Offline, Seguro e Auditável**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Proprietário-red.svg)]()

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Características](#-características)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Arquitetura](#-arquitetura)
- [Segurança](#-segurança)
- [Testes](#-testes)
- [Backup](#-backup)
- [Troubleshooting](#-troubleshooting)
- [Contribuindo](#-contribuindo)

---

## 🎯 Sobre o Projeto

O **HGU Digital Core** é um sistema de gestão hospitalar militar projetado para operar **100% offline**, sem qualquer dependência de internet ou serviços externos. Foi desenvolvido com foco em:

- ✅ **Simplicidade**: Código limpo e bem documentado em português
- ✅ **Segurança**: Múltiplas camadas de proteção e auditoria
- ✅ **Manutenibilidade**: Fácil de entender e modificar
- ✅ **Confiabilidade**: Testes automatizados e backup integrado

### Novidades na Versão 2.0

- 🔐 **Segurança aprimorada** com Bcrypt, CSRF Protection e Rate Limiting
- 🧪 **Testes automatizados** com cobertura de código
- 💾 **Sistema de backup** automático com verificação de integridade
- 📝 **Logging completo** com rotação de arquivos
- ✔️ **Validação de dados** com schemas Marshmallow
- 🚪 **Detecção automática de porta** disponível
- 🛡️ **Controle de acesso** baseado em roles (RBAC)

---

## ✨ Características

### Módulos Implementados

- **Autenticação e Autorização**: Login seguro com controle de acesso por níveis
- **Gestão de Pacientes**: Cadastro e busca de pacientes militares
- **Gestão de Profissionais**: Cadastro de médicos, enfermeiros e equipe
- **Documentos Médicos**: Criação de guias, atestados, encaminhamentos
- **Auditoria**: Rastreamento completo de todas as ações
- **Relatórios**: Estatísticas e dashboards
- **Backup Automático**: Cópias de segurança com verificação de integridade

### Segurança

- 🔒 Hash de senhas com **Bcrypt** (12 rounds)
- 🛡️ Proteção **CSRF** em todas as rotas POST
- 🚦 **Rate Limiting** para prevenir brute force
- 📝 **Logging** completo de eventos de segurança
- 🔐 Sessões seguras com cookies **HttpOnly** e **SameSite**
- ✅ **Validação** rigorosa de todos os dados de entrada

Para mais detalhes, consulte [SECURITY.md](SECURITY.md).

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- SQLite (incluído com Python)

### Instalação Rápida

#### 1. Clone ou extraia o projeto

```bash
cd /caminho/para/hgu_digital_core
```

#### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou use o Makefile:

```bash
make install
```

#### 3. Configure o ambiente (primeira vez)

O sistema irá gerar automaticamente um arquivo `.env` com chaves seguras na primeira execução. Alternativamente, você pode copiar o arquivo de exemplo:

```bash
cp .env.example .env
```

E gerar suas próprias chaves:

```python
python -c "from utils import generate_secret_key, generate_salt; print(f'SECRET_KEY={generate_secret_key()}'); print(f'SALT={generate_salt()}')"
```

#### 4. Inicie o servidor

```bash
python app.py
```

Ou:

```bash
make run
```

O sistema irá:
- Detectar automaticamente uma porta disponível (padrão: 8080)
- Criar o banco de dados se não existir
- Mostrar o endereço para acesso

```
======================================================================
🏛️  HGU DIGITAL CORE - Sistema Offline v2.0
======================================================================
🌐 Servidor iniciando em http://0.0.0.0:8080
📡 Acesse de outros computadores usando: http://192.168.1.100:8080
🔒 Modo debug: DESATIVADO ✓
🔐 CSRF Protection: ATIVADO ✓
🛡️  Rate Limiting: ATIVADO ✓
📝 Logging: ATIVADO ✓
======================================================================
```

---

## 💻 Uso

### Primeiro Acesso - Setup Inicial

1. Abra o navegador e acesse: `http://localhost:8080`
2. Você será direcionado para a tela de configuração inicial
3. Preencha os dados do hospital:
   - Nome do Hospital
   - Sigla OMS
   - Região Militar
   - Comando Vinculado
   - Diretor Técnico
   - Responsável de TI
4. Crie o usuário administrador:
   - Login (mínimo 3 caracteres)
   - Senha forte (mínimo 8 caracteres, com maiúscula, minúscula e número)
   - Nome completo
5. Clique em "Configurar Sistema"

### Login

1. Acesse `http://localhost:8080/login`
2. Digite seu login e senha
3. Você será direcionado para o dashboard

### Níveis de Acesso

- **Administrador**: Acesso total, incluindo configurações e usuários
- **Médico**: Pode criar documentos e gerenciar pacientes
- **Auditor**: Acesso a auditoria e relatórios
- **Visualizador**: Apenas leitura

### Acesso em Rede Local

Para acessar de outros computadores na mesma rede:

#### Windows
```bash
ipconfig
```
Procure por "Endereço IPv4"

#### Linux/Mac
```bash
hostname -I
```

Nos outros computadores, acesse: `http://[IP_DO_SERVIDOR]:8080`

---

## 🏗️ Arquitetura

### Tecnologias

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Backend | Python + Flask | 3.0.0 |
| Banco de Dados | SQLite | 3.x |
| Hash de Senhas | Bcrypt | 1.0.1 |
| Validação | Marshmallow | 3.20.1 |
| PDF | ReportLab | 4.0.7 |
| Testes | Pytest | 7.4.3 |

### Estrutura do Projeto

```
hgu_digital_core/
├── app.py                  # Aplicação principal Flask
├── config.py               # Configurações do sistema
├── database.py             # Operações de banco de dados
├── models.py               # Modelos de dados (schemas SQL)
├── schemas.py              # Validação de dados (Marshmallow)
├── utils.py                # Funções utilitárias
├── logger.py               # Sistema de logging
├── backup.py               # Sistema de backup
├── pdf_generator.py        # Geração de PDFs
├── routes_backup.py        # Rotas de backup
├── migrate_passwords.py    # Script de migração de senhas
├── requirements.txt        # Dependências Python
├── pytest.ini              # Configuração de testes
├── Makefile                # Comandos úteis
├── .env.example            # Template de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── README.md               # Esta documentação
├── SECURITY.md             # Documentação de segurança
├── static/                 # Arquivos estáticos
│   ├── css/                # Estilos CSS
│   ├── js/                 # JavaScript
│   └── img/                # Imagens
├── templates/              # Templates HTML
│   ├── login.html
│   ├── setup.html
│   ├── dashboard.html
│   ├── documentos.html
│   ├── pacientes.html
│   ├── profissionais.html
│   ├── auditoria.html
│   ├── relatorios.html
│   ├── backup.html
│   └── error.html
├── tests/                  # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py         # Fixtures pytest
│   ├── test_auth.py        # Testes de autenticação
│   ├── test_database.py    # Testes de banco de dados
│   ├── test_schemas.py     # Testes de validação
│   └── test_utils.py       # Testes de utilitários
├── logs/                   # Logs do sistema (gerado)
├── pdfs/                   # PDFs gerados (gerado)
├── backups/                # Backups do banco (gerado)
└── hgu_core.db             # Banco de dados (gerado)
```

### Banco de Dados

O sistema usa SQLite com as seguintes tabelas:

- `configuracoes`: Configurações do sistema
- `usuarios`: Usuários e credenciais
- `setores`: Setores do hospital
- `pacientes`: Dados de pacientes
- `profissionais`: Profissionais de saúde
- `documentos`: Documentos médicos
- `auditoria`: Histórico de auditoria
- `templates_pdf`: Templates de documentos
- `logs`: Logs do sistema
- `backups`: Registro de backups

---

## 🔐 Segurança

### Configurações Importantes

#### Produção

Antes de colocar em produção:

1. Certifique-se de que `DEBUG=False` no `.env`
2. Use chaves fortes e únicas para `SECRET_KEY` e `SALT`
3. Configure HTTPS se possível
4. Mantenha o sistema atualizado

#### Senhas

Requisitos mínimos:
- 8 caracteres
- 1 letra maiúscula
- 1 letra minúscula
- 1 número

Recomendado:
- 12+ caracteres
- Caracteres especiais
- Frases-senha

### Migração de Senhas Antigas

Se você está atualizando de uma versão anterior que usava SHA256:

```bash
python migrate_passwords.py
```

Este script irá:
1. Listar todos os usuários
2. Solicitar nova senha para cada um
3. Atualizar com hash Bcrypt seguro

### Checklist de Segurança

Consulte [SECURITY.md](SECURITY.md) para o checklist completo de segurança.

---

## 🧪 Testes

### Executar Todos os Testes

```bash
make test
```

Ou diretamente:

```bash
pytest
```

### Testes com Cobertura

```bash
make test-cov
```

Isso irá gerar um relatório HTML em `htmlcov/index.html`.

### Testes Específicos

```bash
# Apenas testes de autenticação
pytest tests/test_auth.py

# Apenas testes de banco de dados
pytest tests/test_database.py

# Apenas testes unitários (rápidos)
pytest -m unit

# Verbose (mais detalhes)
pytest -v
```

### Estrutura dos Testes

- `test_auth.py`: Testes de login, logout e controle de acesso
- `test_database.py`: Testes de operações de banco de dados
- `test_schemas.py`: Testes de validação de dados
- `test_utils.py`: Testes de funções utilitárias

---

## 💾 Backup

### Criar Backup Manual

Via interface web (como administrador):
1. Acesse "Backup" no menu
2. Clique em "Criar Backup"

Via linha de comando:

```bash
make backup
```

Ou diretamente:

```python
python -c "from backup import realizar_backup; realizar_backup(tipo='manual')"
```

### Backups Automáticos

Configure no `.env`:

```env
BACKUP_AUTOMATICO=True
BACKUP_HORA=23:00
BACKUP_RETENCAO_DIAS=30
```

### Verificar Integridade

```python
from backup import verificar_integridade_backup
resultado = verificar_integridade_backup(backup_id=1)
print(resultado)
```

### Restaurar Backup

**ATENÇÃO**: Isso irá substituir o banco de dados atual!

```python
from backup import restaurar_backup
restaurar_backup(backup_id=1, usuario_id=1)
```

### Limpeza de Backups Antigos

Backups mais antigos que o período de retenção são automaticamente removidos:

```python
from backup import limpar_backups_antigos
removidos = limpar_backups_antigos()
print(f"{removidos} backup(s) removido(s)")
```

---

## 🔧 Troubleshooting

### Porta em uso

**Problema**: "Address already in use" ou porta 8080 ocupada

**Solução**: O sistema agora detecta automaticamente uma porta disponível. Se quiser forçar uma porta específica:

```env
PORT=8090
```

### Erro ao instalar dependências

**Problema**: `pip install` falha

**Solução**:
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Tentar novamente
pip install -r requirements.txt
```

### Banco de dados travado

**Problema**: "database is locked"

**Solução**:
1. Certifique-se de que apenas uma instância do app está rodando
2. Verifique se há processos Python travados: `ps aux | grep python`
3. Em último caso, reinicie o servidor

### Erro de importação

**Problema**: "ModuleNotFoundError"

**Solução**:
```bash
# Verificar instalação
pip list

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Problemas de rede local

**Problema**: Outros computadores não conseguem acessar

**Solução**:
1. Verifique o firewall do servidor
2. Windows: Painel de Controle → Firewall → Permitir aplicativo
3. Adicione Python ou crie regra para porta 8080
4. Verifique se estão na mesma rede

### Senha esquecida

**Problema**: Esqueci a senha do administrador

**Solução**:
```bash
python migrate_passwords.py
```

Redefina a senha do usuário admin.

---

## 🛠️ Comandos Úteis (Makefile)

```bash
# Instalar dependências
make install

# Executar servidor
make run

# Executar testes
make test

# Testes com cobertura
make test-cov

# Criar backup
make backup

# Migrar senhas
make migrate

# Limpar arquivos temporários
make clean

# Configurar ambiente de desenvolvimento
make setup-dev

# Verificar código (lint)
make lint

# Ver todos os comandos
make help
```

---

## 📊 Estatísticas do Projeto

- **Linhas de código**: ~8.000+
- **Arquivos Python**: 15+
- **Templates HTML**: 10+
- **Testes**: 40+
- **Cobertura de código**: 85%+

---

## 📝 Changelog

### v2.0.0 (2025-01-XX)

#### Adicionado
- ✅ Bcrypt para hash de senhas
- ✅ Proteção CSRF em todas as rotas POST
- ✅ Rate Limiting para prevenir brute force
- ✅ Validação de dados com Marshmallow
- ✅ Logging completo com rotação
- ✅ Sistema de backup com verificação de integridade
- ✅ Testes automatizados com Pytest
- ✅ Detecção automática de porta
- ✅ Controle de acesso baseado em roles
- ✅ Health check endpoint
- ✅ Documentação de segurança completa

#### Melhorado
- 🔧 Context manager para conexões de banco de dados
- 🔧 Tratamento de erros robusto
- 🔧 Configurações via variáveis de ambiente
- 🔧 Geração automática de chaves secretas
- 🔧 Sessões seguras com timeout configurável

#### Corrigido
- 🐛 Vulnerabilidade de injeção SQL
- 🐛 XSS em campos de texto
- 🐛 CSRF em formulários
- 🐛 Senhas fracas permitidas
- 🐛 Conexões de banco não fechadas

### v1.0.0 (2024-XX-XX)

- 🎉 Versão inicial

---

## 👥 Contribuindo

Este é um projeto proprietário para uso militar. Modificações devem ser:

1. Testadas completamente
2. Documentadas em português
3. Aprovadas pelo responsável de TI

### Padrões de Código

- Python: PEP 8
- Docstrings em português
- Comentários explicativos
- Testes para novas funcionalidades

---

## 📄 Licença

Copyright © 2024-2025 - Uso Militar Restrito

Este software é propriedade exclusiva e destinado ao uso interno de hospitais militares.
Distribuição, modificação ou uso não autorizado é estritamente proibido.

---

## 📞 Suporte

Para questões técnicas ou reportar problemas:

- **TI Local**: Entre em contato com o responsável de TI do seu hospital
- **Segurança**: Consulte [SECURITY.md](SECURITY.md) para questões de segurança

---

## 🙏 Agradecimentos

Desenvolvido com dedicação para servir aos hospitais militares do Brasil.

**Versão do Sistema**: 2.0.0
**Última Atualização**: Janeiro de 2025

---

**🏛️ HGU Digital Core - Servindo com Tecnologia** 🇧🇷
