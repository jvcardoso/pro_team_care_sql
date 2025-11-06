# 🔧 Solução: CORS + 500 Error no Endpoint /process-image

## 🐛 Problema Identificado

### **Erro 1: CORS Policy**
```
Access to XMLHttpRequest at 'http://192.168.11.83:8000/api/v1/kanban/cards/2/process-image' 
from origin 'http://192.168.11.83:3000' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### **Erro 2: 500 Internal Server Error**
```
POST http://192.168.11.83:8000/api/v1/kanban/cards/2/process-image 
net::ERR_FAILED 500 (Internal Server Error)
```

### **Erro 3: Frontend - uploading is not defined**
```
ReferenceError: uploading is not defined
at ImageUploadWithAI (ImageUploadWithAI.tsx:126:156)
```

---

## 🔍 Diagnóstico

### **1. CORS Error**
**Causa:** Endpoint `/process-image` retorna erro 500 ANTES do CORS ser aplicado.

**Por que:** CORS middleware só adiciona headers em respostas bem-sucedidas. Se o endpoint falha com 500, o CORS não é aplicado.

### **2. 500 Internal Server Error**
**Causa Provável:** Endpoint `/process-image` não está registrado corretamente OU tem erro interno.

**Verificar:**
- Endpoint está no router?
- Router está incluído no `main.py`?
- Pydantic model está correto?
- Dependências estão OK?

### **3. Frontend Cache**
**Causa:** Hot reload do Vite mantém código antigo em cache.

**Solução:** Reiniciar com `./start.sh --skip-cache`

---

## ✅ Soluções Aplicadas

### **1. Verificar Registro do Endpoint**

Vou verificar se o endpoint está registrado:

**Arquivo:** `backend/app/api/v1/uploads_kanban.py`
```python
router = APIRouter(prefix="/kanban", tags=["Kanban Uploads"])

@router.post("/cards/{card_id}/process-image", status_code=status.HTTP_201_CREATED)
async def process_card_image_with_ai(
    card_id: int,
    payload: ProcessImageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # ...
```

**URL completa:** `/api/v1/kanban/cards/{id}/process-image` ✅

---

### **2. Verificar Inclusão do Router**

**Arquivo:** `backend/app/api/v1/router.py`

Deve incluir:
```python
from app.api.v1 import uploads_kanban

api_router.include_router(uploads_kanban.router)
```

---

### **3. Testar Endpoint Diretamente**

**Swagger UI:** http://192.168.11.83:8000/docs

Procurar por:
- **Tag:** "Kanban Uploads"
- **Endpoint:** `POST /api/v1/kanban/cards/{card_id}/process-image`

**Testar com:**
```json
{
  "image_id": 18,
  "user_description": "tela dispositivo movel"
}
```

---

### **4. Verificar Logs do Backend**

```bash
tail -f logs/backend.log
```

**Procurar por:**
- Erro ao processar imagem
- Erro no Gemini Service
- Erro no banco de dados

---

## 🧪 Checklist de Verificação

### **Backend:**
- [ ] Endpoint `/process-image` está em `uploads_kanban.py`?
- [ ] Router tem prefixo `/kanban`?
- [ ] Router está incluído em `router.py`?
- [ ] `ProcessImageRequest` (Pydantic) está correto?
- [ ] Endpoint aparece no Swagger (/docs)?
- [ ] Teste direto no Swagger funciona?

### **Frontend:**
- [ ] Arquivo `ImageUploadWithAI.tsx` não tem `uploading`?
- [ ] Cache do Vite foi limpo?
- [ ] Aplicação foi reiniciada?
- [ ] Console não mostra erro de compilação?

### **CORS:**
- [ ] `main.py` tem `CORSMiddleware` configurado?
- [ ] `allow_origins` inclui frontend URL?
- [ ] `allow_methods=["*"]`?
- [ ] `allow_headers=["*"]`?

---

## 🔧 Comandos de Diagnóstico

### **1. Verificar se endpoint está registrado:**
```bash
grep -r "process-image" backend/app/api/v1/
```

### **2. Verificar routers incluídos:**
```bash
cat backend/app/api/v1/router.py | grep "include_router"
```

### **3. Testar endpoint com curl:**
```bash
curl -X POST "http://192.168.11.83:8000/api/v1/kanban/cards/2/process-image" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_id": 18, "user_description": "teste"}'
```

### **4. Verificar logs em tempo real:**
```bash
tail -f logs/backend.log | grep "process-image"
```

---

## 📊 Fluxo de Debug

```
1. Testar no Swagger
   ├─ Funciona? → Problema no frontend
   └─ Não funciona? → Problema no backend
   
2. Verificar logs do backend
   ├─ Erro 404? → Endpoint não registrado
   ├─ Erro 422? → Payload inválido
   ├─ Erro 500? → Erro interno (ver traceback)
   └─ Sem logs? → Endpoint não foi chamado
   
3. Verificar CORS
   ├─ Erro CORS antes do 500? → Backend falhou primeiro
   └─ Erro CORS sem 500? → CORS mal configurado
```

---

## 🎯 Próximos Passos

1. **Verificar router.py:**
   - Confirmar que `uploads_kanban.router` está incluído

2. **Testar no Swagger:**
   - Acessar http://192.168.11.83:8000/docs
   - Procurar endpoint `/process-image`
   - Testar com payload válido

3. **Verificar logs:**
   - `tail -f logs/backend.log`
   - Procurar por erros

4. **Corrigir problema:**
   - Se 404: Incluir router
   - Se 422: Corrigir Pydantic model
   - Se 500: Debugar código interno

---

**Data:** 2025-11-04  
**Status:** 🔍 EM INVESTIGAÇÃO  
**Próximo:** Verificar `router.py`
