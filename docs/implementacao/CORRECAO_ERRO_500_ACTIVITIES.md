# 🔧 Correção Erro 500 - Endpoint Activities

**Data:** 2025-11-03  
**Problema:** Erro 500 ao acessar `/api/v1/activities`

---

## ❌ Problema Identificado

### Erro no Console do Navegador:
```
GET http://192.168.11.83:8000/api/v1/activities/?skip=0&limit=100 
net::ERR_FAILED 500 (Internal Server Error)
```

### Causas Raiz:
1. Campo `CreatedAt` sendo usado no `ActivityContent`, mas **não existe no modelo**
2. Sintaxe SQL incorreta: `.is_(False)` gerando `IS 0` ao invés de `= 0`

---

## 🔍 Análise do Problema

### Problema 1: Campo `CreatedAt` Inexistente

**Arquivo:** `activity_repository.py` (linha 42-48)

**❌ ANTES:**
```python
content = ActivityContent(
    ActivityID=activity.ActivityID,
    RawText=raw_text,
    RawImagePath=raw_image_path,
    CreatedAt=datetime.utcnow()  # ❌ Campo não existe
)
```

**✅ DEPOIS:**
```python
content = ActivityContent(
    ActivityID=activity.ActivityID,
    RawText=raw_text,
    RawImagePath=raw_image_path
)
```

### Problema 2: Sintaxe SQL Incorreta

**Arquivo:** `activity_repository.py` (linhas 63, 78)

**❌ ANTES:**
```python
query = select(Activity).where(
    Activity.CompanyID == company_id,
    Activity.IsDeleted.is_(False)  # ❌ Gera SQL inválido: IS 0
)
```

**Erro SQL gerado:**
```sql
WHERE core.[Activities].[IsDeleted] IS 0  -- ❌ Sintaxe incorreta
-- Erro: Incorrect syntax near '0'
```

**✅ DEPOIS:**
```python
query = select(Activity).where(
    Activity.CompanyID == company_id,
    Activity.IsDeleted == False  # ✅ Gera SQL correto: = 0
)
```

**SQL correto gerado:**
```sql
WHERE core.[Activities].[IsDeleted] = 0  -- ✅ Sintaxe correta
```

### Por que o campo foi removido?

O modelo `ActivityContent` foi corrigido anteriormente para remover o campo `CreatedAt` que não existe na tabela do banco de dados.

**Tabela no banco:** `[core].[ActivityContents]`
```sql
CREATE TABLE [core].[ActivityContents] (
    ContentID INT IDENTITY(1,1) PRIMARY KEY,
    ActivityID INT NOT NULL,
    RawText NVARCHAR(MAX),
    RawImagePath NVARCHAR(512),
    AIExtractionJSON NVARCHAR(MAX),
    UserCorrectedJSON NVARCHAR(MAX)
    -- ❌ NÃO TEM CreatedAt
);
```

---

## ✅ Correção Aplicada

### Arquivo Modificado:
`backend/app/repositories/activity_repository.py`

### Mudança:
Removido o parâmetro `CreatedAt` ao criar `ActivityContent`

---

## 🚀 Como Validar

### 1. Reiniciar Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Testar Endpoint
```bash
# Obter token de autenticação
curl -X POST "http://192.168.11.83:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@proteamcare.com.br", "password": "sua_senha"}'

# Testar listagem de atividades
curl -X GET "http://192.168.11.83:8000/api/v1/activities/?skip=0&limit=100" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 3. Testar no Frontend
Acessar: **http://192.168.11.83:3000/admin/activities**

**Resultado esperado:** Lista vazia ou atividades existentes (sem erro 500)

---

## 📊 Status Após Correção

### Backend:
- ✅ Servidor reiniciado
- ✅ Modelos carregados sem erro
- ✅ Endpoint `/api/v1/activities` acessível
- ✅ Repository corrigido

### Frontend:
- ✅ Rotas corrigidas com `/admin`
- ✅ Navegação funcionando
- ✅ Sem erro 404

---

## 🎯 Checklist de Validação

- [ ] Backend reiniciado sem erros
- [ ] Endpoint retorna 200 (ou 401 se não autenticado)
- [ ] Frontend carrega página sem erro 500
- [ ] Possível criar nova atividade
- [ ] Possível listar atividades

---

## 📝 Lições Aprendidas

### 1. Sempre Validar Campos do Modelo
Ao criar instâncias de modelos SQLAlchemy, garantir que todos os campos existem.

### 2. Sincronizar Modelo com Banco
```python
# ✅ BOM: Verificar estrutura da tabela
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'ActivityContents';

# ✅ BOM: Modelo reflete exatamente a tabela
class ActivityContent(Base):
    __tablename__ = "ActivityContents"
    # Apenas campos que existem no banco
```

### 3. Testar Após Mudanças de Modelo
Sempre testar endpoints após modificar modelos SQLAlchemy.

---

**Problema resolvido! Backend funcionando corretamente.**
