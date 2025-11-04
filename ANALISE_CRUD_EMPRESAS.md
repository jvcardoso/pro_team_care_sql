# 🔍 Análise Completa - CRUD de Empresas

**Data:** 24/10/2025  
**Empresa Teste:** CUIDAR BEM SERVICOS DE HOME CARE LTDA (ID: 164, CNPJ: 45678912000133)  
**Problema:** Empresa criada no banco não aparece na listagem do frontend

---

## 📊 Status da Empresa no Banco

```sql
CompanyId: 164
RazaoSocial: CUIDAR BEM SERVICOS DE HOME CARE LTDA
NomeFantasia: Cuidar Bem Home Care
CNPJ: 45678912000133
Status: contract_signed
Created: 2025-10-24 21:14:48
```

✅ **Empresa existe no banco de dados**

---

## 🚨 PROBLEMA IDENTIFICADO: Incompatibilidade Estrutural Crítica

### ❌ Backend Retorna Estrutura Minimalista

**Endpoint:** `GET /api/v1/companies/` (linha 98-115)

```python
@router.get("", response_model=CompanyListResponse)
async def list_companies(skip, limit, current_user, db):
    repo = BaseRepository(Company, db)
    companies = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()
    return CompanyListResponse(total=total, companies=companies)
```

**Schema Retornado:** `CompanyResponse` (linhas 117-127)
```python
class CompanyResponse(CompanyBase):
    id: int
    person_id: Optional[int] = None
    access_status: Optional[str] = 'pending_contract'
    settings: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = 0
    contract_terms_version: Optional[str] = None
    contract_accepted_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
```

### ❌ Frontend Espera Estrutura Completa

**Interface:** `Company` (company.types.ts linhas 5-18)
```typescript
export interface Company {
  id: number;
  person_id: number;
  name: string;              // ❌ NÃO EXISTE NO BACKEND
  trade_name?: string;       // ❌ NÃO EXISTE NO BACKEND
  tax_id: string;            // ❌ NÃO EXISTE NO BACKEND
  status: "active" | "inactive" | "suspended";  // ❌ Backend usa access_status
  establishments_count?: number;  // ❌ NÃO EXISTE NO BACKEND
  clients_count?: number;    // ❌ NÃO EXISTE NO BACKEND
  professionals_count?: number;  // ❌ NÃO EXISTE NO BACKEND
  users_count?: number;      // ❌ NÃO EXISTE NO BACKEND
  created_at: string;
  updated_at?: string;
}
```

**Hook de Listagem:** `useCompaniesDataTable.ts` (linhas 91-98)
```typescript
filtered = filtered.filter(
  (company) =>
    company.name?.toLowerCase().includes(searchLower) ||      // ❌ Campo inexistente
    company.trade_name?.toLowerCase().includes(searchLower) || // ❌ Campo inexistente
    company.tax_id?.includes(searchTerm)                       // ❌ Campo inexistente
);
```

---

## 🔧 Solução Existente Não Utilizada

### ✅ Endpoint Correto Já Existe: `/complete-list`

**Localização:** `backend/app/api/v1/companies.py` (linhas 31-95)

```python
@router.get("/complete-list", status_code=status.HTTP_200_OK)
async def list_companies_complete(skip, limit, current_user, db):
    """
    Lista empresas completas usando a view vw_complete_company_data.
    
    Retorna dados agregados incluindo:
    - Informações da empresa
    - Razão social e nome fantasia
    - CNPJ (mascarado conforme LGPD)
    - Endereço principal
    - Telefones agregados
    - Emails agregados
    """
    query = text("""
        SELECT * FROM [core].[vw_complete_company_data]
        ORDER BY CompanyId DESC
        OFFSET :skip ROWS
        FETCH NEXT :limit ROWS ONLY
    """)
    
    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.fetchall()
    
    companies = []
    for row in rows:
        companies.append({
            "company_id": row.CompanyId,
            "access_status": row.CompanyAccessStatus,
            "person_id": row.PersonId,
            "pj_profile_id": row.PjProfileId,
            "razao_social": row.RazaoSocial,
            "nome_fantasia": row.NomeFantasia,
            "cnpj": row.CNPJ,
            "endereco": {...},
            "telefones": row.PhoneNumbers,
            "emails": row.EmailAddresses,
            "incorporation_date": row.incorporation_date,
            "created_at": row.CompanyCreatedAt
        })
    
    return {"total": total, "companies": companies}
```

**View SQL:** `vw_complete_company_data` (Database/023_Create_Complete_Company_View.sql)
- ✅ Une `companies`, `people`, `pj_profiles`, `addresses`, `phones`, `emails`
- ✅ Aplica mascaramento LGPD
- ✅ Agrega telefones e emails
- ✅ Retorna todos os dados necessários

---

## 📋 Plano de Correção

### 1️⃣ Atualizar Frontend para Usar Endpoint Correto

**Arquivo:** `frontend/src/services/api.js` (linha 237-240)

```javascript
// ❌ ANTES
getCompanies: async (params = {}) => {
  const response = await api.get("/api/v1/companies/", { params });
  return response.data.data || response.data;
},

// ✅ DEPOIS
getCompanies: async (params = {}) => {
  const response = await api.get("/api/v1/companies/complete-list", { params });
  return response.data;
},
```

### 2️⃣ Atualizar Interface TypeScript

**Arquivo:** `frontend/src/types/company.types.ts`

```typescript
export interface Company {
  // Campos do endpoint /complete-list
  company_id: number;           // Mapear para id
  access_status: string;        // Mapear para status
  person_id: number;
  pj_profile_id: number;
  razao_social: string;         // Mapear para name
  nome_fantasia: string;        // Mapear para trade_name
  cnpj: string;                 // Mapear para tax_id
  endereco?: {
    street: string;
    number: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  telefones?: string;           // Agregado: "11999999999, 1133333333"
  emails?: string;              // Agregado: "email1@test.com, email2@test.com"
  incorporation_date?: string;
  created_at: string;
}
```

### 3️⃣ Criar Adapter/Mapper

**Novo arquivo:** `frontend/src/adapters/companyAdapter.ts`

```typescript
export function adaptCompanyFromAPI(apiCompany: any): Company {
  return {
    id: apiCompany.company_id,
    person_id: apiCompany.person_id,
    name: apiCompany.razao_social,
    trade_name: apiCompany.nome_fantasia,
    tax_id: apiCompany.cnpj,
    status: mapAccessStatusToStatus(apiCompany.access_status),
    created_at: apiCompany.created_at,
    // Campos adicionais
    endereco: apiCompany.endereco,
    telefones: apiCompany.telefones,
    emails: apiCompany.emails,
  };
}

function mapAccessStatusToStatus(access_status: string): "active" | "inactive" | "suspended" {
  switch (access_status) {
    case "active": return "active";
    case "suspended": return "suspended";
    default: return "inactive";
  }
}
```

### 4️⃣ Atualizar Hook useCompaniesDataTable

**Arquivo:** `frontend/src/hooks/useCompaniesDataTable.ts` (linha 67-68)

```typescript
// ✅ DEPOIS
const response = await companiesService.getCompanies({...});
const adaptedCompanies = response.companies.map(adaptCompanyFromAPI);
setData(adaptedCompanies);
```

---

## 🎯 Alternativa: Corrigir Endpoint Principal

Se preferir manter o endpoint `/api/v1/companies/` como principal:

### Opção A: Enriquecer CompanyResponse

**Arquivo:** `backend/app/schemas/company.py`

```python
class CompanyResponse(CompanyBase):
    id: int
    person_id: Optional[int] = None
    # Adicionar campos de PJ Profile
    name: Optional[str] = None           # Razão Social
    trade_name: Optional[str] = None     # Nome Fantasia
    tax_id: Optional[str] = None         # CNPJ
    # ... outros campos
```

### Opção B: Usar Eager Loading

**Arquivo:** `backend/app/api/v1/companies.py`

```python
@router.get("", response_model=CompanyListResponse)
async def list_companies(skip, limit, current_user, db):
    # Usar query com JOIN para carregar dados relacionados
    query = select(Company).options(
        selectinload(Company.person).selectinload(Person.pj_profile)
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    # Enriquecer resposta com dados de PJ
    enriched = []
    for company in companies:
        company_dict = {
            "id": company.id,
            "person_id": company.person_id,
            "access_status": company.access_status,
            "name": company.person.name if company.person else None,
            "trade_name": company.person.pj_profile.trade_name if company.person and company.person.pj_profile else None,
            "tax_id": company.person.pj_profile.tax_id if company.person and company.person.pj_profile else None,
            "created_at": company.created_at,
            "updated_at": company.updated_at
        }
        enriched.append(company_dict)
    
    return CompanyListResponse(total=await repo.count(), companies=enriched)
```

---

## ⚠️ Impactos Identificados

### Frontend Afetado
- ✅ `CompaniesPage.tsx` - Usa hook useCompaniesDataTable
- ✅ `EmpresasPage.jsx` - Usa companiesService.getCompanies
- ✅ `useCompaniesDataTable.ts` - Filtra por campos inexistentes
- ✅ `companies.config.ts` - Configuração de colunas da tabela

### Backend
- ✅ Endpoint `/complete-list` funcional mas não usado
- ✅ Endpoint `/` retorna estrutura incompleta
- ✅ View `vw_complete_company_data` pronta e testada

---

## 🚀 Recomendação Final

### Solução Mais Rápida (30 minutos)
1. Alterar `api.js` para usar `/complete-list`
2. Criar adapter para mapear campos
3. Atualizar interface TypeScript
4. Testar listagem

### Solução Mais Robusta (2 horas)
1. Deprecar endpoint `/` atual
2. Renomear `/complete-list` para `/`
3. Atualizar todos os schemas
4. Atualizar testes
5. Documentar mudança

---

## 📝 Checklist de Validação

Após correção, validar:

- [ ] Empresa ID 164 aparece na listagem
- [ ] Filtros de busca funcionam (nome, fantasia, CNPJ)
- [ ] Paginação funciona corretamente
- [ ] Métricas são calculadas (total, ativas, inativas)
- [ ] Detalhes da empresa carregam corretamente
- [ ] Edição de empresa funciona
- [ ] Inativação/reativação funciona
- [ ] Performance da listagem (< 2s para 1000 empresas)

---

## 🔗 Arquivos Relacionados

### Backend
- `backend/app/api/v1/companies.py` - Endpoints
- `backend/app/schemas/company.py` - Schemas Pydantic
- `backend/app/models/company.py` - Model SQLAlchemy
- `backend/app/repositories/base.py` - Repositório genérico
- `Database/023_Create_Complete_Company_View.sql` - View completa

### Frontend
- `frontend/src/services/api.js` - Chamadas HTTP
- `frontend/src/hooks/useCompaniesDataTable.ts` - Lógica de listagem
- `frontend/src/types/company.types.ts` - Interfaces TypeScript
- `frontend/src/pages/CompaniesPage.tsx` - Página principal
- `frontend/src/pages/EmpresasPage.jsx` - Página alternativa

---

**Conclusão:** A empresa existe no banco mas não aparece porque o endpoint usado pelo frontend retorna apenas dados da tabela `companies`, sem os campos `name`, `trade_name` e `tax_id` que vêm das tabelas relacionadas `people` e `pj_profiles`. O endpoint `/complete-list` resolve isso mas não está sendo usado.
