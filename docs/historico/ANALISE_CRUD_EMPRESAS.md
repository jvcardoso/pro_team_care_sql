# 📋 ANÁLISE COMPLETA - CRUD DE EMPRESAS

**Data:** 22/10/2025 22:55 BRT  
**Objetivo:** Mapear estrutura existente e identificar ajustes necessários

---

## 🎯 RESUMO EXECUTIVO

### Status Atual:
- ✅ **Backend:** 70% pronto (stored procedures, view, endpoints básicos)
- ✅ **Frontend:** 80% pronto (componentes, hooks, services)
- ⚠️ **Incompatibilidades:** Rotas e schemas diferentes

### Ação Necessária:
1. 🔄 Ajustar rotas do frontend (paginação)
2. 🔄 Ajustar schemas (estrutura mudou)
3. ➕ Criar endpoints faltantes no backend
4. ➕ Criar stored procedure para UPDATE completo

---

## 📊 ESTRUTURA DO BANCO

### Tabelas Principais:
- **companies** → Conta da empresa (tenant)
- **people** → Entidade raiz (Razão Social)
- **pj_profiles** → Dados fiscais (CNPJ, Nome Fantasia)
- **addresses** → Endereços (polimórfico)
- **phones** → Telefones (polimórfico)
- **emails** → E-mails (polimórfico)

### Stored Procedures:
- ✅ **sp_create_company_from_json** → CREATE completo
- ⏳ **sp_update_company_from_json** → UPDATE completo (FALTA CRIAR)
- ✅ **sp_reveal_sensitive_data** → LGPD
- ✅ **sp_cleanup_incomplete_registrations** → Limpeza

### Views:
- ✅ **vw_complete_company_data** → READ com LGPD

---

## 🔧 BACKEND - ENDPOINTS

### ✅ Implementados:
1. `GET /api/v1/companies/complete-list` → Lista completa (view)
2. `GET /api/v1/companies` → Lista básica
3. `GET /api/v1/companies/{id}` → Buscar por ID
4. `POST /api/v1/companies` → Criar (legado)
5. `POST /api/v1/companies/complete` → Criar completo (SP)
6. `PUT /api/v1/companies/{id}` → Atualizar (só companies)
7. `DELETE /api/v1/companies/{id}` → Soft delete

### ❌ Faltam Criar:
1. `GET /api/v1/companies/cnpj/{cnpj}` → Buscar por CNPJ
2. `POST /api/v1/companies/{id}/reactivate` → Reativar
3. `GET /api/v1/companies/search` → Busca com filtros
4. `GET /api/v1/companies/validate/cnpj/{cnpj}` → Validar CNPJ
5. `GET /api/v1/companies/{id}/stats` → Estatísticas
6. `PUT /api/v1/companies/{id}/complete` → Atualizar completo

---

## 🎨 FRONTEND - INCOMPATIBILIDADES

### 1. Paginação ⚠️
**Frontend envia:** `page=1&per_page=10`  
**Backend espera:** `skip=0&limit=10`  
**Ação:** Converter no frontend

### 2. Schema CREATE ⚠️
**Frontend usa:** Estrutura antiga com `people`, `company`  
**Backend espera:** Estrutura nova com `pj_profile`, `access_status`  
**Ação:** Atualizar types e service

### 3. Métodos Inexistentes ❌
- `getByCNPJ()` → Backend não tem
- `reactivate()` → Backend não tem
- `search()` → Backend não tem
- `validateCNPJ()` → Backend não tem
- `getCompanyStats()` → Backend não tem

---

## 📝 PLANO DE AÇÃO

### FASE 1: Ajustes Críticos (2 horas)
1. ✅ Ajustar paginação no frontend
2. ✅ Criar types corretos baseados no backend
3. ✅ Ajustar método `create()` para usar `/complete`

### FASE 2: Endpoints Backend (4 horas)
1. ⏳ Criar `GET /cnpj/{cnpj}`
2. ⏳ Criar `POST /{id}/reactivate`
3. ⏳ Criar `GET /search`
4. ⏳ Criar `GET /validate/cnpj/{cnpj}`
5. ⏳ Criar `GET /{id}/stats`

### FASE 3: UPDATE Completo (3 horas)
1. ⏳ Criar SP `sp_update_company_from_json`
2. ⏳ Criar endpoint `PUT /{id}/complete`
3. ⏳ Ajustar frontend para usar novo endpoint

### FASE 4: Testes (2 horas)
1. ⏳ Testar CREATE completo
2. ⏳ Testar READ com LGPD
3. ⏳ Testar UPDATE completo
4. ⏳ Testar DELETE/Reactivate

---

## 🚨 ALERTAS IMPORTANTES

### ❌ NUNCA FAZER:
- Hard-code de dados
- Ignorar stored procedures
- Atualizar tabelas manualmente (usar SPs)
- Expor dados sem LGPD

### ✅ SEMPRE FAZER:
- Usar `sp_create_company_from_json` para CREATE
- Usar `vw_complete_company_data` para READ
- Usar `sp_update_company_from_json` para UPDATE (quando criado)
- Validar CNPJ antes de criar
- Aplicar mascaramento LGPD

---

**Tempo Total Estimado:** 11 horas  
**Prioridade:** FASE 1 (crítico) → FASE 2 (importante) → FASE 3 (normal)
