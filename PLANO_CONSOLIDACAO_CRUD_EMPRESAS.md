# 🎯 PLANO DE CONSOLIDAÇÃO: CRUD DE EMPRESAS

**Data:** 26/10/2025  
**Objetivo:** Eliminar erros 404 e consolidar estrutura do CRUD de empresas  
**Estimativa Total:** 24-32 horas (3-4 dias úteis)

---

## 📊 DIAGNÓSTICO

### ✅ O que está funcionando:
- Views do banco de dados (`vw_complete_company_data`) corrigidas e funcionais
- Rotas frontend registradas no `App.jsx`
- Endpoints básicos de CRUD implementados no backend
- Autenticação JWT funcionando

### ⚠️ Problemas Identificados:

#### 1. **Duplicação de Endpoints no Backend** (CRÍTICO)
- **Listagem:** `GET /complete-list` vs `GET /`
- **Criação:** `POST /` vs `POST /complete`
- **Impacto:** Frontend confuso sobre qual endpoint usar

#### 2. **Duplicação de Serviços no Frontend** (ALTO)
- `api.js` (JavaScript, antigo)
- `companiesService.ts` (TypeScript, novo)
- **Impacto:** Diferentes partes do app chamam diferentes APIs

#### 3. **APIs Inexistentes** (MÉDIO)
- `GET /companies/{id}/contacts` - Contatos da empresa
- `GET /companies/{id}/audit-log` - Log de auditoria LGPD
- `POST /lgpd/companies/{id}/reveal-field` - Revelar campo sensível
- `POST /lgpd/companies/{id}/reveal-fields` - Revelar múltiplos campos
- `POST /lgpd/companies/{id}/audit-action` - Auditar ação sensível
- **Impacto:** Telas de detalhes retornam 404

---

## 🚀 PLANO DE AÇÃO

### **FASE 1: Backend - Implementar APIs Faltantes** (12-16h)

#### 1.1. Criar Router LGPD Dedicado
**Arquivo:** `backend/app/api/v1/endpoints/lgpd.py`  
**Estimativa:** 8-10h

```python
# Endpoints a implementar:
POST /api/v1/lgpd/companies/{id}/reveal-field
POST /api/v1/lgpd/companies/{id}/reveal-fields
POST /api/v1/lgpd/companies/{id}/audit-action
GET /api/v1/lgpd/companies/{id}/audit-log
```

**Queries SQL necessárias:**
- ✅ Já documentadas no Relatório 2
- ✅ Tabela `core.lgpd_audit_log` já existe
- ✅ Usar stored procedures se existirem

**Checklist:**
- [ ] Criar `lgpd.py` com estrutura base
- [ ] Implementar `reveal_field()` com auditoria
- [ ] Implementar `reveal_fields()` com auditoria consolidada
- [ ] Implementar `audit_action()` para ações sensíveis
- [ ] Implementar `get_audit_log()` com paginação
- [ ] Adicionar schemas Pydantic (Request/Response)
- [ ] Registrar router em `api.py`
- [ ] Criar testes unitários

#### 1.2. Adicionar Endpoint de Contatos em Companies
**Arquivo:** `backend/app/api/v1/endpoints/companies.py`  
**Estimativa:** 2-3h

```python
# Endpoint a implementar:
GET /api/v1/companies/{id}/contacts
```

**Query SQL necessária:**
- ✅ Já documentada no Relatório 2
- ✅ Retorna JSON com phones e emails

**Checklist:**
- [ ] Adicionar função `get_company_contacts()`
- [ ] Criar schema `CompanyContactsResponse`
- [ ] Adicionar tratamento de erros
- [ ] Criar testes unitários

#### 1.3. Criar Schemas Pydantic
**Arquivo:** `backend/app/schemas/lgpd.py`  
**Estimativa:** 2-3h

**Schemas necessários:**
```python
# Request Schemas
class RevealFieldRequest(BaseModel)
class RevealFieldsRequest(BaseModel)
class AuditActionRequest(BaseModel)

# Response Schemas
class RevealFieldResponse(BaseModel)
class AuditLogEntry(BaseModel)
class AuditLogResponse(BaseModel)
class CompanyContactsResponse(BaseModel)
```

**Checklist:**
- [ ] Criar todos os schemas com validação
- [ ] Adicionar docstrings em inglês
- [ ] Adicionar exemplos no schema
- [ ] Validar tipos e constraints

---

### **FASE 2: Backend - Padronizar Endpoints** (4-6h)

#### 2.1. Definir Endpoints Oficiais
**Arquivo:** `backend/app/api/v1/endpoints/companies.py`  
**Estimativa:** 2-3h

**Decisão de Padronização:**

| Operação | Endpoint Oficial | Deprecar | Motivo |
|----------|------------------|----------|--------|
| **Listagem** | `GET /complete-list` | `GET /` | Usa View segura com LGPD |
| **Detalhes** | `GET /{id}` | - | Mantém padrão REST |
| **Criação** | `POST /complete` | `POST /` | Aceita JSON aninhado completo |
| **Atualização** | `PUT /{id}/complete` | `PUT /{id}` | Aceita JSON aninhado completo |

**Checklist:**
- [ ] Marcar endpoints antigos como `@deprecated`
- [ ] Adicionar warnings nos logs
- [ ] Documentar migração no README
- [ ] Atualizar OpenAPI/Swagger docs

#### 2.2. Atualizar Documentação Backend
**Arquivo:** `backend/README.md`  
**Estimativa:** 1-2h

**Checklist:**
- [ ] Documentar endpoints oficiais
- [ ] Adicionar exemplos de request/response
- [ ] Documentar processo de migração
- [ ] Adicionar seção de LGPD/Auditoria

---

### **FASE 3: Frontend - Consolidar Serviços** (6-8h)

#### 3.1. Migrar api.js para companiesService.ts
**Arquivos:**
- `frontend/src/services/api.js` (remover)
- `frontend/src/services/companiesService.ts` (consolidar)

**Estimativa:** 4-5h

**Checklist:**
- [ ] Copiar funções faltantes de `api.js` para `companiesService.ts`
- [ ] Atualizar para usar endpoints oficiais:
  - `getCompanies()` → `GET /complete-list`
  - `createCompany()` → `POST /complete`
  - `updateCompany()` → `PUT /{id}/complete`
- [ ] Implementar funções comentadas:
  - `getCompanyContacts()`
  - `getAuditLog()`
  - `revealField()`
  - `revealFields()`
  - `auditAction()`
- [ ] Adicionar tipos TypeScript completos
- [ ] Adicionar tratamento de erros robusto

#### 3.2. Atualizar Componentes que Usam api.js
**Estimativa:** 2-3h

**Arquivos a atualizar:**
```
frontend/src/pages/EmpresasPage.jsx
frontend/src/components/companies/CompanyDetails.jsx
frontend/src/components/modals/CleanupPendingCompaniesModal.tsx
```

**Checklist:**
- [ ] Substituir imports de `api.js` por `companiesService.ts`
- [ ] Atualizar chamadas de função
- [ ] Testar cada componente individualmente
- [ ] Remover `api.js` após migração completa

---

### **FASE 4: Testes e Validação** (2-4h)

#### 4.1. Testes Backend
**Estimativa:** 1-2h

**Checklist:**
- [ ] Testar endpoints LGPD com Postman/curl
- [ ] Validar auditoria sendo gravada
- [ ] Testar paginação do audit log
- [ ] Testar reveal de campos sensíveis
- [ ] Validar isolamento multi-tenant (company_id)

**Comandos de teste:**
```bash
# Testar listagem
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/companies/complete-list

# Testar contatos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/companies/164/contacts

# Testar reveal
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/lgpd/companies/164/reveal-field?field_name=tax_id

# Testar audit log
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/lgpd/companies/164/audit-log?page=1&size=50
```

#### 4.2. Testes Frontend
**Estimativa:** 1-2h

**Checklist:**
- [ ] Testar listagem de empresas
- [ ] Testar criação de empresa
- [ ] Testar edição de empresa
- [ ] Testar visualização de contatos
- [ ] Testar reveal de campos sensíveis
- [ ] Testar audit log
- [ ] Validar que não há mais 404s

**Comandos de teste:**
```bash
cd frontend
npm run test -- --testPathPattern=companies
npm run lint
```

---

## 📁 ESTRUTURA DE ARQUIVOS

### Novos Arquivos a Criar:

```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   └── lgpd.py                    # ✨ NOVO
│   └── schemas/
│       └── lgpd.py                    # ✨ NOVO

frontend/
└── src/
    └── services/
        └── companiesService.ts        # ✏️ ATUALIZAR (consolidar)
```

### Arquivos a Remover:

```
frontend/
└── src/
    └── services/
        └── api.js                     # ❌ DELETAR (após migração)
```

### Arquivos a Atualizar:

```
backend/
├── app/api/v1/endpoints/
│   └── companies.py                   # ✏️ Adicionar get_contacts + deprecations
└── app/api/v1/api.py                  # ✏️ Registrar router LGPD

frontend/
├── src/pages/
│   └── EmpresasPage.jsx               # ✏️ Usar companiesService.ts
└── src/components/
    └── companies/
        └── CompanyDetails.jsx         # ✏️ Usar companiesService.ts
```

---

## 🔄 ORDEM DE EXECUÇÃO

### Semana 1 - Backend (Dias 1-2)
1. ✅ Criar `lgpd.py` com estrutura base
2. ✅ Implementar endpoints de reveal
3. ✅ Implementar endpoint de audit log
4. ✅ Adicionar endpoint de contatos em `companies.py`
5. ✅ Criar schemas Pydantic
6. ✅ Registrar routers
7. ✅ Testar com Postman/curl

### Semana 1 - Backend (Dia 3)
8. ✅ Marcar endpoints antigos como deprecated
9. ✅ Atualizar documentação
10. ✅ Criar testes unitários

### Semana 2 - Frontend (Dias 1-2)
11. ✅ Consolidar `companiesService.ts`
12. ✅ Implementar funções faltantes
13. ✅ Atualizar componentes
14. ✅ Remover `api.js`

### Semana 2 - Testes (Dia 3)
15. ✅ Testes de integração completos
16. ✅ Validação de auditoria LGPD
17. ✅ Correção de bugs encontrados

---

## 📊 MÉTRICAS DE SUCESSO

### Antes da Consolidação:
- ❌ 5 endpoints retornando 404
- ❌ 2 serviços duplicados no frontend
- ❌ 4 endpoints duplicados no backend
- ❌ Telas de detalhes com erros

### Depois da Consolidação:
- ✅ 0 endpoints retornando 404
- ✅ 1 serviço único no frontend (TypeScript)
- ✅ Endpoints padronizados e documentados
- ✅ Auditoria LGPD completa
- ✅ Telas de detalhes funcionais
- ✅ Código limpo e manutenível

---

## ⚠️ RISCOS E MITIGAÇÕES

### Risco 1: Quebrar funcionalidades existentes
**Mitigação:**
- Marcar endpoints antigos como deprecated (não deletar)
- Manter ambos funcionando por 1 sprint
- Testar exaustivamente antes de remover

### Risco 2: Stored Procedures inexistentes
**Mitigação:**
- Queries SQL já documentadas
- Implementar lógica em Python se SPs não existirem
- Validar com DBA antes de criar novas SPs

### Risco 3: Tabela lgpd_audit_log não existir
**Mitigação:**
- Verificar existência antes de implementar
- Criar script SQL de criação se necessário
- Seguir padrão Database-First

---

## 📝 CHECKLIST FINAL

### Backend:
- [ ] 5 endpoints LGPD implementados
- [ ] Endpoint de contatos implementado
- [ ] Schemas Pydantic criados
- [ ] Endpoints antigos marcados como deprecated
- [ ] Documentação atualizada
- [ ] Testes unitários criados
- [ ] Testes de integração passando

### Frontend:
- [ ] `companiesService.ts` consolidado
- [ ] Funções faltantes implementadas
- [ ] Componentes atualizados
- [ ] `api.js` removido
- [ ] Testes passando
- [ ] Lint sem erros

### Validação:
- [ ] Nenhum erro 404 em produção
- [ ] Auditoria LGPD funcionando
- [ ] Logs sendo gravados corretamente
- [ ] Performance aceitável
- [ ] Documentação completa

---

## 🎯 PRÓXIMOS PASSOS

Após consolidação, considerar:

1. **Otimização de Performance:**
   - Cache de listagens
   - Lazy loading de contatos
   - Paginação otimizada

2. **Melhorias de UX:**
   - Loading states
   - Error boundaries
   - Toast notifications

3. **Segurança:**
   - Rate limiting em endpoints de reveal
   - Validação de permissões granulares
   - Logs de segurança

4. **Monitoramento:**
   - Métricas de uso de reveal
   - Alertas de auditoria
   - Dashboard de compliance LGPD

---

**Estimativa Total:** 24-32 horas (3-4 dias úteis)  
**Prioridade:** ALTA  
**Impacto:** Elimina erros 404 e consolida arquitetura  
**Risco:** MÉDIO (com mitigações adequadas)
