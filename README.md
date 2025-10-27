<div align="center">

# 🏛️ HGU Digital Core

### Sistema de Gestão Hospitalar Militar
**100% Offline • Seguro • Auditável • Open Architecture**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-75%25-yellow.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Funcionalidades](#-funcionalidades) •
[Instalação](#-instalação-rápida) •
[Documentação](#-documentação) •
[Segurança](#-segurança) •
[Changelog](CHANGELOG.md)

</div>

---

## 📖 O Que É?

O **HGU Digital Core** é um sistema completo de gestão hospitalar desenvolvido especialmente para **Hospitais de Guarnição (HGU)** das Forças Armadas Brasileiras. Projetado para funcionar **100% offline**, sem qualquer dependência de internet, garantindo autonomia operacional em qualquer situação.

### 🎯 Por Que Usar?

- 🔒 **Segurança em Primeiro Lugar**: Bcrypt, CSRF Protection, Rate Limiting e auditoria completa
- 🌐 **Totalmente Offline**: Não precisa de internet para funcionar
- 💻 **Fácil de Instalar**: 3 comandos e está rodando
- 🏥 **Específico para Militares**: Campos e fluxos adaptados para hospitais militares
- 📝 **Código Limpo**: Python moderno, bem documentado e fácil de manter
- 🧪 **Testado**: 36 testes automatizados garantem qualidade
- 🔧 **Personalizável**: Código aberto para adaptações

---

## ✨ Funcionalidades

<table>
<tr>
<td width="50%">

### 👥 Gestão de Pessoas
- **Pacientes Militares**: Cadastro com PREC/CP
- **Profissionais de Saúde**: Médicos, enfermeiros, técnicos
- **Níveis de Acesso**: Admin, auditor, operador
- **Autenticação Segura**: Login com hash Bcrypt

</td>
<td width="50%">

### 📋 Documentos Médicos
- **Guias de Encaminhamento**
- **Atestados Médicos**
- **Relatórios Hospitalares**
- **Geração de PDF**: Templates customizáveis
- **PDF Builder**: Construtor visual de formulários

</td>
</tr>
<tr>
<td width="50%">

### 📊 Gestão e Controle
- **Dashboard Executivo**: Estatísticas em tempo real
- **Auditoria Completa**: Rastreio de todas as ações
- **Relatórios Gerenciais**: Análises e métricas
- **Setores Hospitalares**: Organização por setor

</td>
<td width="50%">

### 🛡️ Segurança e Backup
- **Rate Limiting**: Proteção contra ataques
- **CSRF Protection**: Segurança em formulários
- **Backup Automático**: Cópias com hash SHA256
- **Logs Rotativos**: Histórico de ações
- **Validação de Dados**: Schemas Marshmallow

</td>
</tr>
</table>

---

## ⚡ Instalação Rápida

### Pré-requisitos

```bash
# Apenas Python 3.8+ é necessário
python --version  # Deve ser 3.8 ou superior
```

### Opção 1: Instalação Básica (3 comandos)

```bash
# 1. Clone o repositório
git clone https://github.com/fernandes01032000/hgu-digital-core.git
cd hgu-digital-core

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o servidor
python app.py
```

### Opção 2: Com Makefile (recomendado)

```bash
# Clone o projeto
git clone https://github.com/fernandes01032000/hgu-digital-core.git
cd hgu-digital-core

# Instale e execute
make install
make run
```

### 🎉 Pronto! Acesse o Sistema

Abra seu navegador em: **http://localhost:8080**

---

## 🚀 Primeiro Acesso

### 1️⃣ Configuração Inicial

Na primeira vez que acessar, você será direcionado para a tela de setup:

```
📝 Preencha os dados:
   • Nome do Hospital (ex: Hospital de Guarnição de Manaus)
   • OMS (ex: 1º HGU)
   • Região Militar (ex: 12ª RM)
   • Diretor Técnico
   • Responsável TI
```

### 2️⃣ Criar Administrador

```
👤 Dados do Admin:
   • Login: admin (ou qualquer nome)
   • Senha: Mínimo 8 caracteres
           → Deve ter: maiúscula, minúscula e número
           → Exemplo: Hospital@2025
   • Nome completo do administrador
```

### 3️⃣ Fazer Login

Use as credenciais que você acabou de criar e acesse o **Dashboard**!

---

## 🌐 Acesso em Rede Local

### Descubra seu IP

**Windows:**
```bash
ipconfig
# Procure "Endereço IPv4" → ex: 192.168.1.100
```

**Linux/Mac:**
```bash
ifconfig
# ou
ip addr show
```

### Acesse de Outros Computadores

No navegador de qualquer computador na mesma rede:
```
http://192.168.1.100:8080
```

**Porta ocupada?** O sistema detecta automaticamente outra porta disponível!

---

## 📁 Estrutura do Projeto

```
hgu-digital-core/
├── 📱 app.py                  # Aplicação principal Flask
├── 📂 src/                    # Código-fonte modular
│   ├── core/                 # Funcionalidades essenciais
│   │   ├── database.py       # Operações de banco de dados
│   │   ├── security.py       # Segurança e autenticação
│   │   ├── logger.py         # Sistema de logs
│   │   └── backup.py         # Sistema de backup
│   ├── services/             # Serviços de negócio
│   │   ├── pdf_generator.py  # Geração de PDFs
│   │   └── pdf_builder.py    # Construtor de formulários
│   ├── routes/               # Rotas da API
│   └── utils/                # Utilitários
├── 🎨 templates/              # Interfaces HTML
├── 📦 static/                 # CSS, JS, Imagens
├── 🧪 tests/                  # Testes automatizados
├── 📚 docs/                   # Documentação técnica
├── 🔧 scripts/                # Scripts utilitários
└── 📋 requirements.txt        # Dependências Python
```

📖 **Ver estrutura completa**: [ESTRUTURA_PROJETO.md](ESTRUTURA_PROJETO.md)

---

## 🔧 Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Executar testes
make test
pytest tests/ -v

# Criar backup manual
make backup

# Limpar arquivos temporários
make clean

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar linting
flake8 src/
black src/ --check
```

---

## 🛡️ Segurança

O HGU Digital Core implementa **múltiplas camadas de segurança**:

### Autenticação e Autorização
- ✅ Hash de senhas com **Bcrypt** (12 rounds)
- ✅ Controle de acesso baseado em **roles** (RBAC)
- ✅ Sessões seguras com cookies **HttpOnly** e **SameSite**
- ✅ Timeout automático de sessão

### Proteção de Aplicação
- ✅ **CSRF Protection** em todos os formulários
- ✅ **Rate Limiting**: 5 tentativas de login em 5 minutos
- ✅ **Validação de dados** com Marshmallow schemas
- ✅ **Sanitização** de inputs

### Auditoria e Logs
- ✅ **Logging completo** de todas as ações
- ✅ **Auditoria** de acessos e modificações
- ✅ **Rotação de logs** (10MB por arquivo)
- ✅ **Backup automático** com verificação SHA256

📖 **Detalhes completos**: [SECURITY.md](SECURITY.md)

---

## 🧪 Testes

O projeto possui **36 testes automatizados**:

```bash
# Executar todos os testes
pytest

# Com cobertura de código
pytest --cov=src

# Testes específicos
pytest tests/test_auth.py -v
```

### Cobertura por Módulo

| Módulo | Cobertura | Status |
|--------|-----------|--------|
| **Schemas** | 100% | ✅ |
| **Utils** | 100% | ✅ |
| **Database** | 83% | ✅ |
| **Auth** | 75% | ⚠️ |

📊 **Relatório completo**: [RELATORIO_TESTES.md](RELATORIO_TESTES.md)

---

## 📚 Documentação

### Documentos Principais

- 📖 [**README.md**](README.md) - Este arquivo (visão geral)
- 🔐 [**SECURITY.md**](SECURITY.md) - Guia de segurança completo
- 📋 [**CHANGELOG.md**](CHANGELOG.md) - Histórico de versões
- 🏗️ [**ESTRUTURA_PROJETO.md**](ESTRUTURA_PROJETO.md) - Arquitetura detalhada

### Documentação Técnica

- 📄 [Bootstrap Implementation](docs/BOOTSTRAP_IMPLEMENTATION.md)
- 📄 [PDF Builder API](docs/PDF_BUILDER_API.md)
- 📄 [Relatório de Atualização v1.0 → v2.0](docs/RELATORIO_ATUALIZACAO.md)
- 🔍 [Auditoria de Segurança](AUDITORIA_SEGURANCA.md)

---

## 🔄 Backup e Recuperação

### Criar Backup Manual

```bash
# Via comando Make
make backup

# Via Python
python -c "from src.core.backup import realizar_backup; realizar_backup()"
```

### Localização dos Backups

```
backups/
├── backup_2025-01-26_143022.db      # Arquivo do backup
└── backup_2025-01-26_143022.hash    # Hash SHA256 para verificação
```

### Restaurar Backup

```bash
python scripts/restore_backup.py backups/backup_2025-01-26_143022.db
```

---

## ❓ Troubleshooting

### Problema: Porta 8080 em uso

**Solução**: O sistema detecta automaticamente outra porta disponível (8081, 8082, etc.)

### Problema: Erro ao instalar dependências

```bash
# Atualize o pip primeiro
python -m pip install --upgrade pip

# Instale novamente
pip install -r requirements.txt
```

### Problema: Esqueci a senha do admin

```bash
# Execute o script de reset de senha
python scripts/migrate_passwords.py
```

### Problema: Banco de dados corrompido

```bash
# Restaure do backup mais recente
python scripts/restore_backup.py backups/backup_MAIS_RECENTE.db
```

### Problema: Python não encontrado

```bash
# Verifique se o Python está instalado
python --version
# ou
python3 --version

# Se não estiver, instale:
# Windows: https://www.python.org/downloads/
# Linux: sudo apt install python3 python3-pip
# Mac: brew install python3
```

---

## 🗺️ Roadmap

### ✅ Versão 2.0 (Atual)
- ✅ Estrutura modular com /src
- ✅ Testes automatizados (75%+)
- ✅ Segurança enterprise-grade
- ✅ PDF Builder interativo
- ✅ Backup automático

### 🔮 Versão 2.1 (Próxima)
- 🔄 Correção dos bugs de logging
- 📊 Dashboard aprimorado com gráficos
- 📱 Interface responsiva melhorada
- 🌙 Modo escuro
- 📧 Sistema de notificações

### 🚀 Versão 3.0 (Futuro)
- 🔐 Autenticação de 2 fatores (2FA)
- 📲 API REST completa
- 🔄 Sincronização entre unidades
- 📊 Business Intelligence integrado
- 🏥 Integração com equipamentos hospitalares

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja como você pode ajudar:

### Reportar Bugs

Abra uma [issue](https://github.com/fernandes01032000/hgu-digital-core/issues) descrevendo:
- O que aconteceu
- O que você esperava
- Passos para reproduzir
- Versão do Python e SO

### Sugerir Funcionalidades

Abra uma [issue](https://github.com/fernandes01032000/hgu-digital-core/issues) com:
- Descrição da funcionalidade
- Por que é útil
- Exemplos de uso

### Enviar Pull Requests

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- **Desenvolvedor Principal**: [Fernandes Piana Rodrigues](https://github.com/fernandes01032000)
- **Contribuições**: Claude AI Assistant
- **Organização**: Forças Armadas Brasileiras

---

## 🙏 Agradecimentos

- Equipe médica dos HGUs que forneceu feedback valioso
- Comunidade Python pela excelente documentação
- Flask, SQLite e todas as bibliotecas open-source utilizadas

---

## 📞 Suporte

- 📧 **Email**: [Criar issue no GitHub](https://github.com/fernandes01032000/hgu-digital-core/issues)
- 📚 **Documentação**: [Wiki do Projeto](https://github.com/fernandes01032000/hgu-digital-core/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/fernandes01032000/hgu-digital-core/discussions)

---

<div align="center">

### ⭐ Se este projeto foi útil, dê uma estrela no GitHub!

**Desenvolvido com ❤️ para os Hospitais de Guarnição das Forças Armadas Brasileiras**

[⬆ Voltar ao topo](#-hgu-digital-core)

</div>
