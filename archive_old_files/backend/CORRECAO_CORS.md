# 🔧 CORREÇÃO: Erro de CORS

## ❌ **PROBLEMA**

```
Access to XMLHttpRequest at 'http://192.168.11.83:8000/api/v1/auth/login' 
from origin 'http://192.168.11.83:3000' has been blocked by CORS policy
```

**Causa:** O backend só estava permitindo requisições de `http://localhost:3000`, mas o frontend está rodando em `http://192.168.11.83:3000`.

---

## ✅ **SOLUÇÃO APLICADA**

### **1. Atualizado `app/core/config.py`**

```python
# ANTES
CORS_ORIGINS: str = "http://localhost:3000"

# DEPOIS
CORS_ORIGINS: str = "http://localhost:3000,http://192.168.11.83:3000,http://127.0.0.1:3000"
```

### **2. Atualizar arquivo `.env`**

Edite o arquivo `/home/juliano/Projetos/meu_projeto/backend/.env` e altere a linha:

```bash
# ANTES
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# DEPOIS
CORS_ORIGINS=http://localhost:3000,http://192.168.11.83:3000,http://127.0.0.1:3000,http://localhost:5173
```

---

## 🚀 **COMO APLICAR**

### **Opção 1: Editar manualmente**

```bash
nano /home/juliano/Projetos/meu_projeto/backend/.env
```

Altere a linha `CORS_ORIGINS` para:
```
CORS_ORIGINS=http://localhost:3000,http://192.168.11.83:3000,http://127.0.0.1:3000,http://localhost:5173
```

### **Opção 2: Usar sed (automático)**

```bash
cd /home/juliano/Projetos/meu_projeto/backend

# Fazer backup
cp .env .env.backup

# Atualizar CORS_ORIGINS
sed -i 's|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:3000,http://192.168.11.83:3000,http://127.0.0.1:3000,http://localhost:5173|' .env
```

---

## 🔄 **REINICIAR O BACKEND**

Após alterar o `.env`, você **DEVE REINICIAR** o servidor FastAPI:

```bash
# Se estiver rodando, pare com Ctrl+C

# Depois inicie novamente
cd /home/juliano/Projetos/meu_projeto/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ **VERIFICAR SE FUNCIONOU**

### **1. Verificar configuração carregada**

```bash
curl http://192.168.11.83:8000/health
```

### **2. Testar CORS do navegador**

Abra o console do navegador (F12) e execute:

```javascript
fetch('http://192.168.11.83:8000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

Se funcionar, você verá:
```json
{
  "status": "ok",
  "app": "Pro Team Care",
  "version": "1.0.0",
  "environment": "development"
}
```

### **3. Testar login do frontend**

Acesse `http://192.168.11.83:3000/login` e tente fazer login.

**Não deve mais aparecer erro de CORS!**

---

## 📋 **ORIGENS PERMITIDAS AGORA**

Após a correção, o backend aceita requisições de:

- ✅ `http://localhost:3000` (desenvolvimento local)
- ✅ `http://192.168.11.83:3000` (acesso via IP)
- ✅ `http://127.0.0.1:3000` (localhost alternativo)
- ✅ `http://localhost:5173` (Vite dev server)

---

## 🔒 **SEGURANÇA EM PRODUÇÃO**

**⚠️ IMPORTANTE:** Em produção, configure apenas as origens reais:

```bash
# Produção - exemplo
CORS_ORIGINS=https://app.proteamcare.com.br,https://www.proteamcare.com.br
```

**Nunca use `*` (todas as origens) em produção!**

---

## 🐛 **TROUBLESHOOTING**

### **Erro persiste após reiniciar?**

1. **Verificar se o .env foi atualizado:**
   ```bash
   grep CORS_ORIGINS /home/juliano/Projetos/meu_projeto/backend/.env
   ```

2. **Verificar se o servidor reiniciou:**
   ```bash
   # Matar processo antigo
   pkill -f uvicorn
   
   # Iniciar novamente
   cd /home/juliano/Projetos/meu_projeto/backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Limpar cache do navegador:**
   - Pressione `Ctrl+Shift+Delete`
   - Limpe cache e cookies
   - Ou use aba anônima

4. **Verificar porta correta:**
   - Backend: `http://192.168.11.83:8000`
   - Frontend: `http://192.168.11.83:3000`

---

## 📝 **RESUMO**

| Item | Status |
|------|--------|
| **config.py** | ✅ Atualizado |
| **.env** | ⚠️ Precisa atualizar manualmente |
| **Reiniciar backend** | ⚠️ Necessário após alterar .env |

---

**🎯 PRÓXIMO PASSO:** Edite o arquivo `.env` e reinicie o backend!
