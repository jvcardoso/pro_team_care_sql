# ⚡ Lembrete: Hot Reload Ativo!

## IMPORTANTE: Não Reinicie Desnecessariamente

### Backend (Uvicorn)
- ✅ **Hot reload ATIVO** com flag `--reload`
- ✅ Detecta mudanças em arquivos `.py`
- ✅ Recarrega automaticamente em 1-2 segundos
- ❌ **NÃO** use `./stop.sh` e `./start.sh` para mudanças de código

### Frontend (Vite)
- ✅ **HMR (Hot Module Replacement) ATIVO**
- ✅ Detecta mudanças em `.tsx`, `.ts`, `.jsx`, `.js`, `.css`
- ✅ Atualiza **instantaneamente** no browser
- ✅ **Preserva estado** do React (useState mantém valores)
- ❌ **NÃO** use `./stop.sh` e `./start.sh` para mudanças de código

### Quando REALMENTE Reiniciar
- 🔄 Mudou `.env` (backend ou frontend)
- 🔄 Instalou nova dependência (`pip install` ou `npm install`)
- 🔄 Mudou configuração (`vite.config.ts`, `uvicorn config`)

### Workflow Correto
1. `./start.sh` (uma vez no início)
2. Altere código
3. **Salve arquivo** (Ctrl+S)
4. Espere 1-2 segundos
5. ✅ Mudança aplicada automaticamente!

**Economize 90% do tempo de desenvolvimento!**