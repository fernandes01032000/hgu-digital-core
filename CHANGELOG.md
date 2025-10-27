# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-01-26

### 🎉 Lançamento da Versão 2.0

#### ✨ Adicionado
- Sistema completo de autenticação e autorização com níveis de acesso
- Hash de senhas com Bcrypt (12 rounds)
- Proteção CSRF em todas as rotas POST
- Rate limiting para login (5 tentativas/5min) e API (200/dia)
- Sistema de backup automático com verificação de integridade (SHA256)
- Sistema de logging rotativos com múltiplos níveis
- Validação de dados com Marshmallow schemas
- Testes automatizados com Pytest (85%+ de cobertura)
- PDF Builder interativo com React/TypeScript
- Detecção automática de porta disponível
- Interface Bootstrap 5 responsiva
- Sistema de auditoria completo
- Gestão de pacientes e profissionais
- Geração de documentos PDF customizáveis
- Dashboard com estatísticas em tempo real
- Middleware de autenticação e autorização
- Context managers para conexões de banco de dados
- Health check endpoint (`/health`)
- Comandos Make para facilitar operações

#### 🔒 Segurança
- Secret key e salt movidos para variáveis de ambiente
- Cookies seguros (HttpOnly, Secure, SameSite)
- DEBUG=False em produção por padrão
- Sanitização de inputs
- Logs de segurança para tentativas de acesso
- Proteção contra SQL injection
- Timeout de sessão configurável
- Validação de nível de acesso em todas as rotas protegidas

#### 📝 Documentação
- README.md completo com guia de instalação e uso
- SECURITY.md com guia de segurança
- AUDITORIA_SEGURANCA.md com auditoria completa
- Guia de início rápido
- Documentação da API do PDF Builder
- Relatório de atualização v1.0 → v2.0
- Docstrings em todas as funções
- Exemplos de uso

#### 🧪 Testes
- 40+ testes automatizados
- Testes de autenticação e autorização
- Testes de banco de dados
- Testes de validação de schemas
- Testes de utilitários
- Configuração do Pytest
- Cobertura de código 85%+

#### 🏗️ Arquitetura
- Estrutura modular e organizada
- Separação de responsabilidades
- Configurações centralizadas em `config.py`
- Modelos de dados em arquivo separado
- Schemas de validação isolados
- Sistema de rotas modular
- Logging estruturado

#### 🛠️ Infraestrutura
- Makefile com comandos úteis
- Script de migração de senhas
- Script de migração para PDF Builder
- Backup automático configurável
- Limpeza de backups antigos
- .env.example para configuração
- .gitignore otimizado
- pytest.ini configurado

### 🐛 Corrigido
- Vulnerabilidades de segurança críticas (3)
- Vulnerabilidades de alta prioridade (4)
- Vulnerabilidades de média prioridade (3)
- Tratamento inadequado de erros
- Falta de validação de dados
- Queries SQL não otimizadas
- Conexões de banco não fechadas adequadamente
- Logs inadequados

### ⚠️ Breaking Changes
- **Senhas**: Todas as senhas devem ser redefinidas via `scripts/migrate_passwords.py`
- **Configuração**: Arquivo `.env` é obrigatório (gerado automaticamente)
- **Python**: Requer Python 3.8 ou superior
- **Dependências**: Novas dependências devem ser instaladas via `pip install -r requirements.txt`

### 📦 Dependências Adicionadas
- Flask-Bcrypt 1.0.1
- Flask-WTF 1.2.1
- Flask-Limiter 3.5.0
- Marshmallow 3.20.1
- python-dotenv 1.0.0
- Flask-CORS 4.0.0
- pytest 7.4.3
- pytest-flask 1.3.0
- pytest-cov 4.1.0
- python-dateutil 2.8.2

### 📊 Estatísticas
- **Arquivos Python**: 15+ (era 6)
- **Linhas de Código**: 8.000+ (era ~3.000)
- **Cobertura de Testes**: 85%+ (era 0%)
- **Vulnerabilidades**: 0 (eram 10)
- **Documentação**: 5 arquivos (era 1)

---

## [1.0.0] - 2024-10-25

### 🎉 Lançamento Inicial

#### ✨ Adicionado
- Aplicação Flask básica
- Banco de dados SQLite
- Sistema de login simples
- Gestão básica de pacientes
- Gestão básica de profissionais
- Geração de PDF com ReportLab
- Templates HTML com Jinja2
- CSS customizado
- Configurações básicas

#### 🐛 Problemas Conhecidos
- Hash de senha com SHA256 simples (vulnerável)
- Secret key hardcoded
- Sem proteção CSRF
- Sem rate limiting
- Sem validação de dados
- Sem testes automatizados
- Debug mode ativo
- Cookies inseguros
- Documentação limitada
- Falta de logs adequados

---

## Tipos de Mudanças

- `✨ Adicionado` - Para novas funcionalidades
- `🔄 Modificado` - Para mudanças em funcionalidades existentes
- `🗑️ Removido` - Para funcionalidades removidas
- `🐛 Corrigido` - Para correção de bugs
- `🔒 Segurança` - Para correções de vulnerabilidades
- `📝 Documentação` - Para mudanças na documentação
- `🧪 Testes` - Para adição ou mudança de testes
- `🏗️ Arquitetura` - Para mudanças estruturais
- `⚡ Performance` - Para melhorias de performance
- `♻️ Refatoração` - Para mudanças que não alteram funcionalidade

---

## Links

- [Repositório GitHub](https://github.com/fernandes01032000/hgu-digital-core)
- [Documentação Completa](README.md)
- [Guia de Segurança](SECURITY.md)
- [Auditoria de Segurança](AUDITORIA_SEGURANCA.md)
