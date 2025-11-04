# ⚡ Hot Reload - Não Reinicie Desnecessariamente!

## 🎯 Resumo

**Backend e Frontend têm hot reload ATIVO!**

✅ **NÃO precisa** reiniciar ao alterar código
❌ **NÃO use** `./stop.sh` e `./start.sh` a cada mudança

---

## 🔥 Backend - Uvicorn Hot Reload

### Como funciona:
```bash
# start.sh usa flag --reload
uvicorn app.main:app --reload
```

### O que detecta:
✅ Mudanças em arquivos `.py`
✅ Recarrega automaticamente em ~1 segundo
✅ Preserva estado do banco de dados

### Como testar:
1. Altere um endpoint em `backend/app/api/v1/users.py`
2. Salve o arquivo (Ctrl+S)
3. Veja no terminal: `Reloading...`
4. **Pronto!** Endpoint atualizado

### NÃO precisa reiniciar:
- Alterações em código Python
- Adicionar/modificar endpoints
- Mudanças em models/schemas
- Alterações em services/repositories

### Precisa reiniciar APENAS se:
- Mudou `backend/.env` (variáveis de ambiente)
- Instalou nova dependência (`pip install`)
- Mudou configuração do uvicorn

---

## ⚡ Frontend - Vite HMR (Hot Module Replacement)

### Como funciona:
```bash
# Vite tem HMR nativo
npm run dev
```

### O que detecta:
✅ Mudanças em `.tsx`, `.ts`, `.jsx`, `.js`
✅ Mudanças em `.css`, Tailwind classes
✅ Atualiza **instantaneamente** no browser (sem refresh!)
✅ Preserva estado do React (useState mantém valores)

### Como testar:
1. Altere componente em `frontend/src/components/UserCard.tsx`
2. Salve o arquivo (Ctrl+S)
3. Veja no browser: **atualização instantânea**
4. **Estado preservado!** (sem perder dados de formulário)

### NÃO precisa reiniciar:
- Alterações em componentes React
- Mudanças em hooks customizados
- Alterações em CSS/Tailwind
- Mudanças em services/types

### Precisa reiniciar APENAS se:
- Mudou `frontend/.env` (VITE_API_URL, etc)
- Instalou nova dependência (`npm install`)
- Mudou `vite.config.ts` ou `tailwind.config.js`

---

## 🚫 Erros Comuns

### ❌ Erro: "Reiniciando a cada mudança"
**Problema:** Você está usando `./stop.sh` e `./start.sh` desnecessariamente

**Solução:**
- **Apenas salve o arquivo** (Ctrl+S)
- Espere 1-2 segundos
- Mudanças aplicadas automaticamente

---

### ❌ Erro: "Mudança não aparece"
**Causas possíveis:**

1. **Cache do browser**
   - Solução: Ctrl+Shift+R (hard refresh)

2. **Mudou .env mas não reiniciou**
   - Solução: `./stop.sh` e `./start.sh` (só neste caso)

3. **Erro de sintaxe no código**
   - Solução: Veja console do terminal/browser

4. **Porta errada**
   - Solução: Verifique http://localhost:3000 (frontend) e :8000 (backend)

---

## 📊 Quando REALMENTE Reiniciar

### Backend - Precisa reiniciar:
```bash
# Mudou .env
vim backend/.env
./stop.sh && ./start.sh

# Instalou dependência
cd backend && pip install nova-lib
./stop.sh && ./start.sh
```

### Frontend - Precisa reiniciar:
```bash
# Mudou .env
vim frontend/.env
./stop.sh && ./start.sh

# Instalou dependência
cd frontend && npm install nova-lib
./stop.sh && ./start.sh

# Mudou config Vite
vim frontend/vite.config.ts
./stop.sh && ./start.sh
```

---

## ⚡ Dicas de Produtividade

### 1. Use 2 terminais lado a lado:
```
Terminal 1: tail -f logs/backend.log
Terminal 2: tail -f logs/frontend.log
```

### 2. Veja reload em tempo real:
```bash
# Backend mostra:
INFO: Will watch for changes in these directories: ['/backend']
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Started reloader process [12345]

# Quando alterar código:
INFO: Reloading...
INFO: Application startup complete.
```

```bash
# Frontend mostra:
vite v4.1.0 dev server running at:
> Local:   http://localhost:3000/

# Quando alterar código:
hmr update /src/components/UserCard.tsx
```

### 3. Reload automático no browser:
- Instale extensão "Vite" no browser (opcional)
- Vite já faz HMR automaticamente
- **Sem extensão necessária!**

---

## 🎯 Checklist Antes de Reiniciar

Antes de fazer `./stop.sh` e `./start.sh`, pergunte:

- [ ] Mudei apenas código Python/React? → **NÃO reinicie**
- [ ] Mudei .env? → **SIM, reinicie**
- [ ] Instalei dependência? → **SIM, reinicie**
- [ ] Mudei config (vite.config, uvicorn)? → **SIM, reinicie**
- [ ] Erro de sintaxe no código? → **NÃO reinicie, corrija o erro**

---

## 💡 Resumo Final

```
🔄 Hot Reload ATIVO = NÃO REINICIE!

Workflow correto:
1. ./start.sh                 (uma vez no início)
2. Altere código
3. Salve (Ctrl+S)
4. Espere 1-2 seg
5. ✅ Mudança aplicada!

❌ Workflow ERRADO:
1. Altere código
2. ./stop.sh
3. ./start.sh
4. ❌ Perde tempo esperando reiniciar
```

**Economize 90% do tempo de desenvolvimento!** ⚡
