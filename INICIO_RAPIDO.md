# 🚀 Guia de Início Rápido - HGU Digital Core v2.0

**5 minutos para o sistema funcionar!**

---

## ⚡ Instalação Express

### 1. Pré-requisitos
- Python 3.8+ instalado
- Terminal/CMD aberto na pasta do projeto

### 2. Instalar e Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python app.py
```

**Pronto!** O sistema estará rodando em `http://localhost:8080`

---

## 🎯 Primeiro Acesso

### 1. Abra o navegador
```
http://localhost:8080
```

### 2. Configure o sistema
- Preencha dados do hospital
- Crie usuário administrador
  - Login: `admin`
  - Senha: **mínimo 8 caracteres, com maiúscula, minúscula e número**
  - Exemplo: `Admin2025!`

### 3. Faça login
- Use o login e senha que você criou
- Pronto! Você está no dashboard

---

## 🌐 Acesso em Rede Local

### Windows
```bash
ipconfig
```
Procure "Endereço IPv4" → Exemplo: `192.168.1.100`

### Nos outros computadores
```
http://192.168.1.100:8080
```

---

## 🔧 Comandos Úteis

```bash
# Ver comandos disponíveis
make help

# Executar testes
make test

# Criar backup
make backup

# Limpar arquivos temporários
make clean
```

---

## ❓ Problemas Comuns

### Porta em uso?
O sistema detecta automaticamente outra porta disponível.

### Erro ao instalar?
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Esqueceu a senha?
```bash
python migrate_passwords.py
```

---

## 📚 Documentação Completa

- **Uso**: [README.md](README.md)
- **Segurança**: [SECURITY.md](SECURITY.md)
- **Auditoria**: [AUDITORIA_SEGURANCA.md](AUDITORIA_SEGURANCA.md)
- **Atualização**: [RELATORIO_ATUALIZACAO.md](RELATORIO_ATUALIZACAO.md)

---

## ✅ Checklist Pós-Instalação

- [ ] Sistema rodando e acessível
- [ ] Login funcionando
- [ ] Criar backup inicial: `make backup`
- [ ] Verificar `.env` criado automaticamente
- [ ] Testar acesso em rede local
- [ ] Ler [SECURITY.md](SECURITY.md)

---

**🏛️ HGU Digital Core - Sistema Pronto!** ✅
