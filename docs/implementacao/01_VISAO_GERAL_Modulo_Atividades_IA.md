# Módulo de Gestão de Atividades com IA - Visão Geral

**Data:** 2025-11-03 | **Versão:** 1.0 | **Status:** Aprovado

---

## 🎯 Objetivo

Sistema de produtividade que:
1. Registra atividades (texto/imagem)
2. Usa Gemini para extrair dados
3. Usuário valida sugestões da IA
4. Gera base de conhecimento
5. Board Kanban para pendências

---

## 🏗️ Arquitetura

```
Frontend (React) → Backend (FastAPI) → Gemini API
                         ↓
                  SQL Server
```

**Componentes:**
- **Frontend:** Formulário registro + Tela validação + Board Kanban
- **Backend:** API REST + Engenharia de prompt + Cliente Gemini
- **Banco:** 4 tabelas (Activities, ActivityContents, ActivityEntities, Pendencies)
- **IA:** Gemini 1.5 Flash (análise texto/imagem)

---

## 🔄 Fluxo de Trabalho

1. **Entrada:** Usuário cola texto/imagem + preenche Título e Status
2. **IA:** Gemini extrai pessoas, datas, tags, pendências
3. **Validação:** Usuário corrige/aceita sugestões
4. **Gravação:** Dados salvos + cards criados no board

---

## 📊 Estrutura de Dados

### `[core].Activities`
- ActivityID, CompanyID, UserID, Title*, Status*, CreationDate, DueDate

### `[core].ActivityContents`
- ContentID, ActivityID, RawText, RawImagePath, AIExtractionJSON, UserCorrectedJSON

### `[core].ActivityEntities`
- EntityID, ActivityID, EntityType, EntityName

### `[core].Pendencies`
- PendencyID, ActivityID, Description, Owner, Status, Impediment

---

## 🎯 MVP - 3 Fases

### Fase 1: Banco + Backend (3-4 dias)
- Scripts SQL
- Modelos + Schemas
- Endpoints CRUD

### Fase 2: Frontend Manual (3-4 dias)
- Formulário registro
- Board Kanban
- Validar valor SEM IA

### Fase 3: Integração IA (2-3 dias)
- Cliente Gemini
- Tela validação
- Sistema completo

**Total:** 8-11 dias úteis

---

## 🔐 Isolamento

- ✅ Multi-tenant (CompanyID em todas tabelas)
- ✅ Módulo separado: `/backend/app/modules/activities/`
- ✅ Rotas isoladas: `/api/v1/activities/*`
- ✅ Não afeta código existente

---

## 💰 Custo Gemini

- **Modelo:** gemini-1.5-flash
- **Texto:** Gratuito (15 req/min)
- **Imagem:** ~$0.00025 cada
- **MVP:** < $10/mês (1 usuário)

---

## ✅ Viabilidade

**APROVADO** - Conceito excelente e totalmente viável:
- ✅ Stack compatível (FastAPI + React)
- ✅ Gemini CLI já instalado (v0.11.3)
- ✅ Arquitetura sólida
- ✅ Custo baixo
- ✅ Isolado do sistema principal

---

## 📝 Próximos Documentos

1. `02_IMPLEMENTACAO_DBA.md` - Scripts SQL (para DBA)
2. `03_IMPLEMENTACAO_BACKEND.md` - API + IA (para Dev)
3. `04_IMPLEMENTACAO_FRONTEND.md` - UI/UX (para Dev)
4. `05_GUIA_INTEGRACAO_GEMINI.md` - Config IA
