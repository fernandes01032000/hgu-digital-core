# 📚 PDF Form Builder - Documentação da API Backend

## ✅ Status: ETAPA 1 COMPLETA

O backend Python/Flask do PDF Form Builder está **100% funcional** e pronto para uso. Esta documentação detalha todos os endpoints disponíveis.

---

## 🔐 Autenticação

**Todos os endpoints requerem autenticação via sessão Flask.**

- O usuário deve estar logado no sistema HGU Digital Core
- A sessão é validada pelo decorador `@login_requerido`
- Sessões expiram após 1 hora de inatividade (configurável em `.env`)

---

## 📋 Endpoints Disponíveis

### 1. Listar Templates

```http
GET /api/pdf-templates
```

**Descrição**: Retorna lista de todos os templates PDF ativos.

**Response** (200 OK):
```json
{
  "sucesso": true,
  "templates": [
    {
      "id": 1,
      "nome": "Formulário de Admissão",
      "descricao": "Formulário padrão para admissão de pacientes",
      "caminho_arquivo": "/path/to/file.pdf",
      "ativo": true,
      "data_criacao": "2025-10-26 00:00:00",
      "num_campos": 15,
      "file_size": 245678
    }
  ]
}
```

---

### 2. Upload de Template

```http
POST /api/pdf-templates/upload
Content-Type: multipart/form-data
```

**Descrição**: Faz upload de um PDF e cria um novo template.

**Request Body**:
```
file: <arquivo PDF> (max 10MB)
name: "Nome do Template" (3-255 caracteres)
description: "Descrição opcional" (max 1000 caracteres)
```

**Validações**:
- PDF válido (verificado com PyPDF2)
- Tamanho máximo: 10MB
- Nome obrigatório (3-255 caracteres)

**Response** (200 OK):
```json
{
  "sucesso": true,
  "mensagem": "Template criado com sucesso!",
  "template": {
    "id": 2,
    "nome": "Formulário de Admissão",
    "descricao": "Formulário padrão",
    "num_pages": 1,
    "width": 595.0,
    "height": 842.0,
    "file_size": 245678,
    "filename": "template_20251026_025000_1.pdf"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Arquivo inválido ou muito grande
- `500 Internal Server Error`: Erro ao salvar

---

### 3. Obter Template

```http
GET /api/pdf-templates/:id
```

**Descrição**: Retorna informações completas de um template específico, incluindo campos mapeados.

**Response** (200 OK):
```json
{
  "sucesso": true,
  "template": {
    "id": 1,
    "nome": "Formulário de Admissão",
    "descricao": "Descrição",
    "caminho_arquivo": "/path/to/file.pdf",
    "campos": [
      {
        "field_id": "abc123",
        "name": "Nome Completo",
        "type": "text",
        "x": 100,
        "y": 200,
        "width": 300,
        "height": 30,
        "font_size": 12,
        "required": true,
        "placeholder": "Digite seu nome",
        "default_value": "",
        "options": null,
        "validation": {
          "minLength": 3,
          "maxLength": 200
        }
      }
    ],
    "ativo": true,
    "data_criacao": "2025-10-26 00:00:00",
    "file_size": 245678,
    "num_pages": 1,
    "width": 595.0,
    "height": 842.0
  }
}
```

**Error Responses**:
- `404 Not Found`: Template não encontrado

---

### 4. Obter PDF do Template

```http
GET /api/pdf-templates/:id/pdf
```

**Descrição**: Retorna o arquivo PDF original do template.

**Response** (200 OK):
- `Content-Type: application/pdf`
- Retorna bytes do PDF

**Error Responses**:
- `404 Not Found`: Template ou arquivo não encontrado

---

### 5. Atualizar Template

```http
PUT /api/pdf-templates/:id
Content-Type: application/json
```

**Descrição**: Atualiza informações básicas do template (nome, descrição, status).

**Request Body**:
```json
{
  "name": "Novo Nome",
  "description": "Nova descrição",
  "ativo": true
}
```

**Response** (200 OK):
```json
{
  "sucesso": true,
  "mensagem": "Template atualizado com sucesso!"
}
```

**Error Responses**:
- `404 Not Found`: Template não encontrado

---

### 6. Deletar Template

```http
DELETE /api/pdf-templates/:id
```

**Descrição**: Deleta um template (soft delete - marca como inativo).

**Response** (200 OK):
```json
{
  "sucesso": true,
  "mensagem": "Template deletado com sucesso!"
}
```

**Error Responses**:
- `404 Not Found`: Template não encontrado

---

### 7. Duplicar Template

```http
POST /api/pdf-templates/:id/duplicate
```

**Descrição**: Cria uma cópia completa do template (PDF + campos).

**Response** (200 OK):
```json
{
  "sucesso": true,
  "mensagem": "Template duplicado com sucesso!",
  "template": {
    "id": 3,
    "nome": "Formulário de Admissão (Cópia)",
    "descricao": "Descrição original",
    "num_pages": 1,
    "width": 595.0,
    "height": 842.0
  }
}
```

**Error Responses**:
- `404 Not Found`: Template original não encontrado

---

### 8. Salvar Campos do Template

```http
PUT /api/pdf-templates/:id/fields
Content-Type: application/json
```

**Descrição**: Salva/atualiza todos os campos mapeados de um template.

**Request Body**:
```json
{
  "fields": [
    {
      "field_id": "abc123",
      "name": "Nome Completo",
      "type": "text",
      "x": 100,
      "y": 200,
      "width": 300,
      "height": 30,
      "font_size": 12,
      "required": true,
      "placeholder": "Digite seu nome",
      "default_value": "",
      "options": null,
      "validation": {
        "minLength": 3,
        "maxLength": 200
      }
    },
    {
      "field_id": "def456",
      "name": "Data de Nascimento",
      "type": "date",
      "x": 100,
      "y": 250,
      "width": 200,
      "height": 30,
      "font_size": 12,
      "required": true
    }
  ]
}
```

**Tipos de Campo Suportados**:
- `text`: Input de linha única
- `textarea`: Área de texto multilinha
- `checkbox`: Checkbox booleano (true/false)
- `radio`: Grupo de opções (escolha única)
- `dropdown`: Menu select dropdown
- `date`: Seletor de data
- `signature`: Assinatura digital (data URL base64)
- `image`: Upload de imagem (data URL base64)

**Validações**:
- `field_id`: obrigatório (1-100 caracteres)
- `name`: obrigatório (1-255 caracteres)
- `type`: obrigatório (um dos 8 tipos)
- `x, y`: obrigatórios (≥0)
- `width, height`: obrigatórios (10-2000 pixels)
- `font_size`: opcional (8-72)
- `required`: opcional (boolean)
- `options`: opcional (array de strings, para dropdown/radio)
- `validation`: opcional (objeto JSON)

**Response** (200 OK):
```json
{
  "sucesso": true,
  "mensagem": "Campos salvos com sucesso!"
}
```

**Error Responses**:
- `400 Bad Request`: Dados inválidos
- `404 Not Found`: Template não encontrado

---

### 9. Obter Campos do Template

```http
GET /api/pdf-templates/:id/fields
```

**Descrição**: Retorna apenas os campos mapeados do template.

**Response** (200 OK):
```json
{
  "sucesso": true,
  "campos": [
    {
      "field_id": "abc123",
      "name": "Nome Completo",
      "type": "text",
      "x": 100,
      "y": 200,
      "width": 300,
      "height": 30,
      "font_size": 12,
      "required": true
    }
  ]
}
```

---

### 10. Gerar PDF Preenchido

```http
POST /api/pdf-templates/:id/generate
Content-Type: application/json
```

**Descrição**: Gera um PDF preenchido com os dados fornecidos.

**Request Body**:
```json
{
  "formData": {
    "abc123": "João da Silva",
    "def456": "1990-05-15",
    "ghi789": true,
    "jkl012": "data:image/png;base64,iVBORw0KGgo..."
  }
}
```

**Observações**:
- Chaves do `formData` devem corresponder aos `field_id` dos campos
- Valores vazios/null são ignorados (campo não é desenhado)
- Imagens e assinaturas devem ser data URLs base64
- Checkboxes: true = ☑, false = ☐

**Response** (200 OK):
- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename=documento_1_20251026_025530.pdf`
- Retorna bytes do PDF gerado

**Error Responses**:
- `400 Bad Request`: Dados inválidos
- `404 Not Found`: Template não encontrado

---

### 11. Upload de Imagem

```http
POST /api/upload-image
Content-Type: multipart/form-data
```

**Descrição**: Faz upload de uma imagem e retorna data URL base64 (para campos `signature` e `image`).

**Request Body**:
```
file: <arquivo de imagem> (max 5MB)
```

**Validações**:
- Formato válido (PNG, JPG, etc.)
- Tamanho máximo: 5MB
- Redimensionado automaticamente se > 800x800px

**Response** (200 OK):
```json
{
  "sucesso": true,
  "dataUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Error Responses**:
- `400 Bad Request`: Imagem inválida ou muito grande

---

## 🗄️ Estrutura do Banco de Dados

### Tabela `templates_pdf`

```sql
CREATE TABLE templates_pdf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    caminho_arquivo TEXT NOT NULL,
    mapeamento_campos TEXT,  -- JSON array de campos
    ativo INTEGER DEFAULT 1,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela `template_fields` (Futura - não usada atualmente)

```sql
CREATE TABLE template_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    field_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    font_size INTEGER DEFAULT 12,
    required INTEGER DEFAULT 0,
    placeholder TEXT,
    default_value TEXT,
    options TEXT,  -- JSON array
    validation TEXT,  -- JSON object
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates_pdf(id) ON DELETE CASCADE
);
```

**Nota**: Atualmente, os campos são armazenados como JSON no campo `mapeamento_campos` da tabela `templates_pdf`. A tabela `template_fields` está disponível para migração futura se necessário.

---

## 🔧 Tecnologias Backend

- **Flask 3.0.0**: Framework web
- **PyPDF2 3.0.1**: Leitura e manipulação de PDFs
- **ReportLab 4.0.7**: Desenho de campos no PDF
- **Pillow 11.3.0**: Processamento de imagens
- **Marshmallow 3.20.1**: Validação de schemas
- **SQLite**: Banco de dados

---

## 📦 Arquivos Criados

### Backend (Python)
- `pdf_builder.py` - Lógica principal (620 linhas)
- `app.py` - Rotas adicionadas (11 endpoints)
- `schemas.py` - Schemas de validação (4 novos)
- `models.py` - Modelo de dados (tabela + índice)
- `migrate_pdf_builder.py` - Script de migration

### Templates
- `templates/pdf_builder.html` - Página placeholder

### Documentação
- `PDF_BUILDER_API.md` - Esta documentação

---

## 🧪 Como Testar

### 1. Verificar Instalação

```bash
python3 migrate_pdf_builder.py
python3 -c "import pdf_builder; print('OK')"
```

### 2. Iniciar Servidor

```bash
python3 app.py
```

### 3. Testar com cURL

#### Upload de Template
```bash
curl -X POST http://localhost:8080/api/pdf-templates/upload \
  -H "Cookie: session=..." \
  -F "file=@formulario.pdf" \
  -F "name=Meu Formulário" \
  -F "description=Teste"
```

#### Listar Templates
```bash
curl http://localhost:8080/api/pdf-templates \
  -H "Cookie: session=..."
```

#### Salvar Campos
```bash
curl -X PUT http://localhost:8080/api/pdf-templates/1/fields \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "fields": [
      {
        "field_id": "nome",
        "name": "Nome Completo",
        "type": "text",
        "x": 100,
        "y": 200,
        "width": 300,
        "height": 30,
        "font_size": 12,
        "required": true
      }
    ]
  }'
```

#### Gerar PDF
```bash
curl -X POST http://localhost:8080/api/pdf-templates/1/generate \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "formData": {
      "nome": "João da Silva"
    }
  }' \
  --output documento.pdf
```

---

## 🚀 Próximos Passos (Etapa 2)

A **Etapa 1 (Backend) está 100% completa**. A próxima fase é:

### Etapa 2: Frontend React (12-16 horas estimadas)

1. **Setup React + Vite**
   - Configurar projeto React em `/static/pdf-builder/`
   - Instalar dependências (React, PDF.js, Shadcn UI)

2. **Componentes Principais**
   - PDFCanvas (drag-drop de campos)
   - FieldLibrary (biblioteca de 8 tipos)
   - FieldOverlay (redimensionamento visual)
   - FieldProperties (painel de configuração)
   - FormBuilder (formulário dinâmico)
   - PDFPreview (preview em tempo real)

3. **Integração**
   - API client TypeScript
   - Gerenciamento de estado (localStorage ou React Query)
   - Upload de arquivos
   - Preview de PDF com PDF.js

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema em `logs/sistema.log`
2. Verificar logs de segurança
3. Consultar esta documentação

---

**✅ Backend 100% Funcional e Pronto para Produção!**
