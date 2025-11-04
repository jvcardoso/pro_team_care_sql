# Correção: Padronização de Rotas `/empresas` → `/companies`

## 🎯 Problema Identificado

**Sintoma:** Erro 404 ao clicar nos atalhos do dashboard e menu lateral.

**Causa Raiz:** Inconsistência entre:
- ✅ **Rotas definidas**: `/admin/companies` (App.jsx)
- ❌ **Links navegando para**: `/admin/empresas`

---

## 🔧 Arquivos Corrigidos

### 1. **companies.config.tsx** (Tabela de Empresas)
```typescript
// ANTES:
navigate(`/admin/empresas/${company.id}?tab=informacoes`)
navigate(`/admin/empresas?companyId=${company.id}&action=edit`)
navigate("/admin/empresas?view=create")

// DEPOIS:
navigate(`/admin/companies/${company.id}?tab=informacoes`)
navigate(`/admin/companies?companyId=${company.id}&action=edit`)
navigate("/admin/companies?view=create")
```

**Impacto:** Ações da tabela (Ver, Editar, Criar)

---

### 2. **CompanyDetailsNew.tsx** (Detalhes da Empresa)
```typescript
// ANTES:
navigate("/admin/empresas")
navigate(`/admin/empresas?companyId=${id}&action=edit`)

// DEPOIS:
navigate("/admin/companies")
navigate(`/admin/companies?companyId=${id}&action=edit`)
```

**Impacto:** Botões "Voltar" e "Editar"

---

### 3. **CompanyDetails.jsx** (Detalhes Legado)
```typescript
// ANTES:
navigate(`/admin/empresas/${companyId}?tab=${newTab}`)
navigate("/admin/empresas")

// DEPOIS:
navigate(`/admin/companies/${companyId}?tab=${newTab}`)
navigate("/admin/companies")
```

**Impacto:** Navegação entre abas e botão "Voltar"

---

### 4. **CompaniesWithoutSubscription.jsx** (Dashboard)
```typescript
// ANTES:
navigate(`/admin/empresas/${company.id}`)

// DEPOIS:
navigate(`/admin/companies/${company.id}`)
```

**Impacto:** Card "Empresas sem assinatura" no dashboard

---

### 5. **B2BBillingPage.tsx** (Faturamento B2B)
```typescript
// ANTES:
navigate(`/empresas/${companyId}`)

// DEPOIS:
navigate(`/admin/companies/${companyId}`)
```

**Impacto:** Link para empresa na página de faturamento

---

### 6. **SubscriptionPlansPage.tsx** (Planos de Assinatura)
```typescript
// ANTES:
window.location.href = `/admin/empresas/${company.id}?tab=informacoes`

// DEPOIS:
window.location.href = `/admin/companies/${company.id}?tab=informacoes`
```

**Impacto:** Link "Ver Empresa" na página de planos

---

### 7. **CompanyActivationActions.tsx** (Ativação de Empresa)
```typescript
// ANTES:
window.location.href = `/admin/empresas/${company.id}?tab=ativacao`

// DEPOIS:
window.location.href = `/admin/companies/${company.id}?tab=ativacao`
```

**Impacto:** Botão "Ver Status" na ativação

---

### 8. **CompanyActivationTab.tsx** (Aba de Ativação)
```typescript
// ANTES:
window.location.href = `/admin/empresas`

// DEPOIS:
window.location.href = `/admin/companies`
```

**Impacto:** Botão "Ir para Lista" após ativação

---

## ✅ Validação

Verificado que **NÃO HÁ MAIS** referências a `/empresas` em:
- ✅ Arquivos `.ts`
- ✅ Arquivos `.tsx`
- ✅ Arquivos `.js`
- ✅ Arquivos `.jsx`

```bash
# Comando executado:
grep -r "/empresas" frontend/src --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx"

# Resultado: 0 ocorrências ✅
```

---

## 📋 Rotas Padronizadas

### ✅ Agora TODAS usam `/companies`:

| Rota | Finalidade |
|------|------------|
| `/admin/companies` | Lista de empresas |
| `/admin/companies/:id` | Detalhes da empresa |
| `/admin/companies?view=create` | Criar empresa |
| `/admin/companies?companyId=X&action=edit` | Editar empresa |
| `/admin/companies/:id?tab=informacoes` | Aba Informações |
| `/admin/companies/:id?tab=ativacao` | Aba Ativação |
| `/admin/companies/:id?tab=...` | Outras abas |

---

## 🧪 Como Testar

### 1. Dashboard
- ✅ Clicar em card "Empresas sem assinatura"
- ✅ Deve navegar para `/admin/companies/:id`

### 2. Tabela de Empresas
- ✅ Clicar em "Ver" (ícone olho)
- ✅ Clicar em "Editar" (ícone lápis)
- ✅ Clicar em "Criar" (botão +)
- ✅ Todas devem funcionar sem 404

### 3. Detalhes da Empresa
- ✅ Botão "Voltar"
- ✅ Botão "Editar"
- ✅ Navegação entre abas
- ✅ Todas devem funcionar

### 4. Outros Módulos
- ✅ Faturamento B2B → Link empresa
- ✅ Planos de Assinatura → Ver empresa
- ✅ Ativação → Ver status

---

## 🚀 Próximos Passos (Opcional)

Para completar a padronização, considere também padronizar:

| Rota Atual | Sugestão |
|------------|----------|
| `/admin/estabelecimentos` | `/admin/establishments` |
| `/admin/clientes` | `/admin/clients` |
| `/admin/contratos` | `/admin/contracts` |
| `/admin/pacientes` | `/admin/patients` |
| `/admin/profissionais` | `/admin/professionals` |
| `/admin/consultas` | `/admin/appointments` |
| `/admin/autorizacoes` | `/admin/authorizations` |
| `/admin/relatorios` | `/admin/reports` |
| `/admin/servicos` | `/admin/services` |

**Benefícios:**
- ✅ Consistência total (inglês)
- ✅ API RESTful padronizada
- ✅ Internacionalização facilitada
- ✅ Melhor manutenibilidade

---

## 📊 Resumo

| Métrica | Valor |
|---------|-------|
| **Arquivos corrigidos** | 8 |
| **Linhas modificadas** | ~15 |
| **Referências `/empresas`** | 0 ✅ |
| **Erros 404 esperados** | 0 ✅ |

---

**Data:** 2025-01-26
**Status:** ✅ Concluído
**Validado:** Sim
**Hot Reload:** Funciona automaticamente (Vite HMR)
