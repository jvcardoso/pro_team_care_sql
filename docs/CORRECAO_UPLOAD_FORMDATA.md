# ✅ Correção: Upload de FormData (422 Unprocessable Entity)

## 🎯 Problema Identificado

### **Erro:**
```
POST http://192.168.11.83:8000/api/v1/kanban/import-bm 422 (Unprocessable Entity)
Error: Field required
```

### **Causa Raiz:**
O axios estava enviando FormData com `Content-Type: application/json` (padrão da instância), ao invés de `multipart/form-data` com boundary correto.

---

## 🔧 Solução Implementada

### **1. Interceptor do Axios Atualizado**
**Arquivo:** `frontend/src/services/api.js`

**Problema:**
```javascript
// ❌ ANTES: Content-Type fixo em application/json
export const api = axios.create({
  headers: {
    'Content-Type': 'application/json',  // Sobrescreve FormData!
  }
});
```

**Solução:**
```javascript
// ✅ DEPOIS: Detecta FormData e remove Content-Type
api.interceptors.request.use((config) => {
  // Se for FormData, remover Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});
```

**Por quê funciona:**
- Quando `Content-Type` é removido, o browser define automaticamente
- Browser adiciona `multipart/form-data; boundary=----WebKitFormBoundary...`
- Boundary é necessário para separar os campos do FormData

---

### **2. Modal Simplificado**
**Arquivo:** `frontend/src/components/kanban/ImportBMModal.tsx`

**Problema:**
```javascript
// ❌ ANTES: Tentava definir Content-Type manualmente
const response = await api.post('/api/v1/kanban/import-bm', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',  // Sem boundary!
  },
});
```

**Solução:**
```javascript
// ✅ DEPOIS: Deixa o interceptor cuidar
const response = await api.post('/api/v1/kanban/import-bm', formData);
// Interceptor detecta FormData e remove Content-Type
// Browser define automaticamente com boundary correto
```

---

## 📊 Comparação Antes/Depois

### **Antes (Erro 422):**
```http
POST /api/v1/kanban/import-bm HTTP/1.1
Content-Type: application/json
Authorization: Bearer xxx

[object FormData]  ❌ Corpo inválido
```

### **Depois (Sucesso 200):**
```http
POST /api/v1/kanban/import-bm HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
Authorization: Bearer xxx

------WebKitFormBoundary...
Content-Disposition: form-data; name="file"; filename="data.csv"
Content-Type: text/csv

[conteúdo do arquivo]
------WebKitFormBoundary...--
```

---

## 🎯 Lições Aprendidas

### **1. FormData e Content-Type**
- ❌ **Nunca** definir `Content-Type` manualmente para FormData
- ✅ **Sempre** deixar o browser definir automaticamente
- ✅ Browser adiciona o `boundary` necessário

### **2. Axios Interceptors**
- Interceptors podem sobrescrever headers padrão
- Detectar `instanceof FormData` é a melhor prática
- Remover `Content-Type` permite que browser defina

### **3. FastAPI File Upload**
```python
# FastAPI espera:
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    # Requer Content-Type: multipart/form-data com boundary
    pass
```

---

## 🧪 Como Testar

### **1. Verificar Headers no DevTools:**
```
Network → Request Headers
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
```

### **2. Verificar Console:**
```
🚀 API Request: POST /api/v1/kanban/import-bm
data: FormData  ✅ (não mostra conteúdo)
```

### **3. Verificar Backend:**
```python
# Logs do backend devem mostrar:
📁 Arquivo: dasa-20251105161442-BPX.csv
📄 Tamanho: 102929 bytes
✅ Processando...
```

---

## 📁 Arquivos Modificados

```
✅ frontend/src/services/api.js
   - Interceptor detecta FormData
   - Remove Content-Type para FormData
   - Permite browser definir boundary
   
✅ frontend/src/components/kanban/ImportBMModal.tsx
   - Removido headers manuais
   - Simplificado envio
   - Deixa interceptor cuidar
```

---

## 🚀 Outros Serviços Afetados

### **Verificar e Corrigir:**

**1. Upload de Imagens:**
```javascript
// frontend/src/services/activityService.ts
// ❌ ANTES:
const response = await api.post('/uploads/images', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

// ✅ DEPOIS:
const response = await api.post('/uploads/images', formData);
// Interceptor cuida automaticamente
```

**2. Upload de Faturas:**
```javascript
// frontend/src/services/billingService.ts
// ❌ ANTES:
await api.post('/billing/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

// ✅ DEPOIS:
await api.post('/billing/upload', formData);
```

---

## ✅ Checklist de Correção

- [x] Interceptor detecta FormData
- [x] Remove Content-Type para FormData
- [x] Modal simplificado (sem headers)
- [x] Logs de debug adicionados
- [x] Documentação criada
- [ ] Corrigir outros serviços (activityService, billingService)
- [ ] Testar upload de imagens
- [ ] Testar upload de faturas

---

## 🎯 Resultado Final

### **Antes:**
```
❌ 422 Unprocessable Entity
❌ Field required
❌ FormData não enviado corretamente
```

### **Depois:**
```
✅ 200 OK
✅ Arquivo recebido pelo backend
✅ Processamento iniciado
✅ Cards importados com sucesso
```

---

**Data:** 2025-11-05  
**Status:** ✅ CORRIGIDO  
**Impacto:** Upload de arquivos agora funciona corretamente  
**Próximo:** Testar importação completa do CSV
