# Segurança do HGU Digital Core

## Visão Geral

Este documento descreve as medidas de segurança implementadas no sistema HGU Digital Core e as melhores práticas para operação segura.

## Medidas de Segurança Implementadas

### 1. Autenticação e Autorização

#### Hash de Senhas
- **Bcrypt**: Todas as senhas são hasheadas usando Bcrypt com custo de 12 rounds
- **Salt único**: Cada senha tem seu próprio salt gerado automaticamente
- **Nunca armazena senhas em texto plano**

#### Sessões
- **Cookies seguros**:
  - `HttpOnly`: Previne acesso via JavaScript
  - `Secure`: Apenas HTTPS em produção
  - `SameSite=Lax`: Proteção contra CSRF
- **Timeout**: Sessões expiram após 1 hora (configurável)
- **Renovação automática**: Sessões são renovadas em cada requisição

#### Controle de Acesso Baseado em Roles (RBAC)
- **Administrador**: Acesso total ao sistema
- **Médico**: Acesso a documentos e pacientes
- **Auditor**: Acesso a auditoria e relatórios
- **Visualizador**: Acesso somente leitura

### 2. Proteção Contra Ataques

#### CSRF (Cross-Site Request Forgery)
- **Flask-WTF CSRF Protection** ativado em todas as rotas POST
- Tokens CSRF obrigatórios para formulários

#### Rate Limiting
- **Login**: Máximo 5 tentativas a cada 5 minutos por IP
- **API**: 200 requisições/dia, 50/hora por IP
- Implementado com Flask-Limiter

#### SQL Injection
- **Queries parametrizadas**: Todas as consultas SQL usam parâmetros
- **ORM**: Uso de row_factory do SQLite para acesso seguro
- **Validação de entrada**: Schemas Marshmallow validam todos os dados

#### XSS (Cross-Site Scripting)
- **Sanitização**: Jinja2 escapa automaticamente HTML
- **Content Security Policy**: Recomendado configurar CSP headers
- **Validação de entrada**: Rejeita caracteres perigosos

### 3. Logging e Auditoria

#### Logs de Segurança
- Todas as tentativas de login (sucesso e falha)
- Acessos negados por falta de permissão
- Mudanças em dados críticos
- Erros de sistema

#### Logs Rotativos
- Arquivos rotacionam a cada 10 MB
- Mantém 5 arquivos históricos
- Formato timestamped para análise

#### Auditoria de Documentos
- Todas as mudanças em documentos são registradas
- Histórico completo de status
- Rastreamento de usuário e timestamp

### 4. Proteção de Dados

#### Criptografia
- **Senhas**: Bcrypt com salt único
- **Sessões**: Secret key forte gerada automaticamente
- **Hash de documentos**: SHA256 para verificar integridade

#### Backup
- Backups automáticos diários
- Hash SHA256 de cada backup para verificar integridade
- Retenção configurável (padrão: 30 dias)
- Verificação de integridade antes de restaurar

### 5. Validação de Dados

#### Schemas Marshmallow
- Todos os endpoints validam entrada com schemas
- Rejeita dados malformados antes de processar
- Mensagens de erro claras

#### Validação Específica
- PREC-CP: Formato militar validado
- Senhas: Mínimo 8 caracteres, maiúscula, minúscula e número
- Nomes de arquivo: Sanitização para prevenir path traversal

## Configurações de Segurança

### Arquivo .env

**NUNCA** commite o arquivo `.env` no controle de versão!

```env
# Gere valores únicos e fortes
SECRET_KEY=use-python-secrets-para-gerar
SALT=use-python-secrets-para-gerar

# Produção
DEBUG=False
SESSION_TIMEOUT=3600

# Rate Limiting
RATE_LIMIT_LOGIN=5
RATE_LIMIT_WINDOW=300
```

### Geração de Chaves

Use Python para gerar chaves seguras:

```python
import secrets
import string

alphabet = string.ascii_letters + string.digits + string.punctuation
secret_key = ''.join(secrets.choice(alphabet) for _ in range(64))
print(f"SECRET_KEY={secret_key}")

alphabet = string.ascii_letters + string.digits
salt = ''.join(secrets.choice(alphabet) for _ in range(32))
print(f"SALT={salt}")
```

## Checklist de Segurança para Produção

### Antes de Implantar

- [ ] Arquivo `.env` configurado com chaves únicas
- [ ] `DEBUG=False` no .env
- [ ] Secret key forte (mínimo 64 caracteres)
- [ ] Salt forte (mínimo 32 caracteres)
- [ ] Senhas de todos os usuários foram migradas para Bcrypt
- [ ] Backup inicial criado

### Configuração do Servidor

- [ ] HTTPS configurado (certificado SSL/TLS)
- [ ] Firewall configurado (apenas portas necessárias abertas)
- [ ] Sistema operacional atualizado
- [ ] Antivírus ativo (Windows)
- [ ] Acesso físico ao servidor restrito

### Rede

- [ ] Servidor em rede isolada/VLAN separada
- [ ] IPs de acesso restritos (se possível)
- [ ] Logs de firewall ativados
- [ ] Monitoramento de tráfego (se disponível)

### Operação

- [ ] Backups automáticos configurados
- [ ] Logs sendo monitorados
- [ ] Plano de recuperação de desastres documentado
- [ ] Usuários treinados sobre segurança
- [ ] Política de senhas fortes comunicada

## Melhores Práticas

### Senhas

1. **Mínimo 8 caracteres**
2. **Pelo menos:**
   - 1 letra maiúscula
   - 1 letra minúscula
   - 1 número
3. **Recomendado:**
   - Caracteres especiais
   - 12+ caracteres
   - Frases-senha memoráveis

### Acesso

1. **Princípio do Menor Privilégio**: Usuários só têm o acesso necessário
2. **Revisão periódica**: Revisar permissões mensalmente
3. **Remoção de usuários**: Desativar imediatamente ao sair
4. **Logout**: Sempre fazer logout ao terminar

### Backup

1. **Backups regulares**: Mínimo diário
2. **Teste de restauração**: Testar mensalmente
3. **Armazenamento separado**: Backups em dispositivo diferente
4. **Verificação de integridade**: Sempre antes de restaurar

### Monitoramento

1. **Logs**: Revisar logs de segurança semanalmente
2. **Alertas**: Configurar alertas para eventos críticos
3. **Tentativas de login**: Investigar múltiplas falhas
4. **Acessos incomuns**: Verificar horários fora do expediente

## Resposta a Incidentes

### Em caso de suspeita de comprometimento:

1. **Isolar**: Desconectar da rede imediatamente
2. **Documentar**: Registrar tudo que foi observado
3. **Preservar**: Não alterar dados até investigação
4. **Notificar**: Informar responsável de TI e superior
5. **Investigar**: Analisar logs e backups
6. **Recuperar**: Restaurar de backup limpo se necessário
7. **Fortalecer**: Implementar medidas adicionais

## Atualizações de Segurança

### Manter Sistema Atualizado

```bash
# Atualizar dependências Python
pip install --upgrade -r requirements.txt

# Verificar vulnerabilidades conhecidas
pip install safety
safety check
```

### Monitorar Vulnerabilidades

- Assinar lista de segurança do Flask
- Monitorar CVEs de dependências
- Atualizar regularmente

## Contato para Questões de Segurança

Para reportar vulnerabilidades de segurança, entre em contato com o responsável de TI do hospital.

**NÃO** publique vulnerabilidades publicamente antes de correção.

## Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [SQLite Security](https://www.sqlite.org/security.html)
