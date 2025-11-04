# 🎯 PLANO DE AÇÃO - CRUD EMPRESAS

**Data:** 22/10/2025 23:00 BRT  
**Objetivo:** Implementar CRUD completo de Empresas

---

## 📊 RESUMO DA ANÁLISE

### ✅ O que já existe:
- Backend: 7 endpoints funcionais
- Frontend: Componentes completos (tabela, formulário, detalhes)
- Banco: Stored procedures, views, LGPD

### ⚠️ O que precisa ajustar:
- Paginação (frontend → backend)
- Schemas (estrutura antiga → nova)
- 6 endpoints faltantes no backend

---

## 🔥 FASE 1: AJUSTES CRÍTICOS (2h)

### 1.1. Ajustar Paginação no Frontend (30 min)

**Arquivo:** `frontend/src/services/companiesService.ts`

```typescript
// Linha 32-48: Ajustar método getAll()

async getAll(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
}): Promise<PaginatedResponse<CompanyList>> {
  // ✅ Converter page/per_page para skip/limit
  const page = params?.page || 1;
  const per_page = params?.per_page || 10;
  const skip = (page - 1) * per_page;
  const limit = per_page;

  const queryParams = new URLSearchParams();
  queryParams.append("skip", skip.toString());
  queryParams.append("limit", limit.toString());
  
  if (params?.search) queryParams.append("search", params.search);
  if (params?.status) queryParams.append("status", params.status);

  const url = `/api/v1/companies?${queryParams.toString()}`;
  return get<PaginatedResponse<CompanyList>>(url);
}
```

---

### 1.2. Criar Types Corretos (1h)

**Arquivo:** `frontend/src/types/company.types.ts`

```typescript
// ✅ SUBSTITUIR TODO O CONTEÚDO

/**
 * Company Types - Baseado na estrutura da API atual
 */

// ============================================================================
// SCHEMAS PARA CREATE/UPDATE
// ============================================================================

export interface PJProfileData {
  name: string;                      // Razão Social
  trade_name: string;                // Nome Fantasia
  tax_id: string;                    // CNPJ (apenas números)
  incorporation_date?: string;       // Data de constituição (YYYY-MM-DD)
  tax_regime?: string;               // Regime tributário
  legal_nature?: string;             // Natureza jurídica
  municipal_registration?: string;   // Inscrição municipal
}

export interface AddressData {
  street: string;
  number: string;
  details?: string;
  neighborhood: string;
  city: string;
  state: string;                     // UF (2 letras)
  zip_code: string;                  // CEP (apenas números)
  country?: string;                  // Padrão: "BR"
  type: string;                      // commercial, residential, etc
  is_principal: boolean;
}

export interface PhoneData {
  country_code?: string;             // Padrão: "55"
  number: string;                    // Apenas números
  type: string;                      // commercial, mobile, etc
  is_principal: boolean;
  is_whatsapp: boolean;
  phone_name?: string;
}

export interface EmailData {
  email_address: string;
  type: string;                      // work, personal, etc
  is_principal: boolean;
}

export interface CompanyCompleteCreate {
  access_status?: string;            // Padrão: "pending_contract"
  pj_profile: PJProfileData;
  addresses: AddressData[];
  phones: PhoneData[];
  emails: EmailData[];
}

export interface CompanyCompleteResponse {
  new_company_id: number;
  new_person_id: number;
  new_pj_profile_id: number;
  message: string;
}

// ============================================================================
// SCHEMAS PARA READ
// ============================================================================

export interface CompanyBasic {
  id: number;
  person_id: number | null;
  access_status: string;
  settings: any;
  display_order: number;
  contract_terms_version: string | null;
  contract_accepted_at: string | null;
  activated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyComplete {
  company_id: number;
  access_status: string;
  person_id: number;
  pj_profile_id: number;
  razao_social: string;
  nome_fantasia: string;
  cnpj: string;                      // Pode estar mascarado
  endereco: {
    street: string;
    number: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  } | null;
  telefones: string;                 // Agregado
  emails: string;                    // Agregado
  incorporation_date: string | null;
  created_at: string;
}

export interface CompanyListResponse {
  total: number;
  companies: CompanyBasic[];
}

export interface CompanyCompleteListResponse {
  total: number;
  companies: CompanyComplete[];
}

// ============================================================================
// TYPES AUXILIARES
// ============================================================================

export type CompanyAccessStatus = 
  | "pending_contract" 
  | "contract_signed" 
  | "active" 
  | "suspended";

// Manter compatibilidade com código antigo
export type Company = CompanyBasic;
export type CompanyDetailed = CompanyComplete;
export type CompanyList = CompanyComplete;
export type CompanyCreate = CompanyCompleteCreate;
export type CompanyUpdate = Partial<CompanyCompleteCreate>;
```

---

### 1.3. Ajustar Método create() (30 min)

**Arquivo:** `frontend/src/services/companiesService.ts`

```typescript
// Linha 66-76: Ajustar método create()

/**
 * Criar nova empresa completa
 */
async create(data: CompanyCompleteCreate): Promise<CompanyCompleteResponse> {
  const result = await post<CompanyCompleteResponse, CompanyCompleteCreate>(
    `${this.basePath}/complete`,  // ✅ Usar rota /complete
    data
  );
  // Invalidar cache de empresas após criação
  httpCache.invalidatePattern("/api/v1/companies");
  return result;
}
```

---

## 🔧 FASE 2: ENDPOINTS BACKEND (4h)

### 2.1. GET /api/v1/companies/cnpj/{cnpj} (30 min)

**Arquivo:** `backend/app/api/v1/companies.py`

```python
# Adicionar após linha 138 (depois do get_company)

@router.get("/cnpj/{cnpj}")
async def get_company_by_cnpj(
    cnpj: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca empresa por CNPJ.
    
    Remove formatação do CNPJ antes de buscar.
    Requer autenticação JWT.
    """
    # Remover formatação
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    
    if len(clean_cnpj) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido. Deve conter 14 dígitos."
        )
    
    # Buscar na view
    query = text("""
        SELECT * FROM [core].[vw_complete_company_data]
        WHERE REPLACE(REPLACE(REPLACE(CNPJ, '.', ''), '/', ''), '-', '') = :cnpj
    """)
    
    result = await db.execute(query, {"cnpj": clean_cnpj})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada com este CNPJ"
        )
    
    # Converter para dict
    return {
        "company_id": row.CompanyId,
        "access_status": row.CompanyAccessStatus,
        "person_id": row.PersonId,
        "pj_profile_id": row.PjProfileId,
        "razao_social": row.RazaoSocial,
        "nome_fantasia": row.NomeFantasia,
        "cnpj": row.CNPJ,
        "endereco": {
            "street": row.PrincipalStreet,
            "number": row.PrincipalNumber,
            "neighborhood": row.PrincipalNeighborhood,
            "city": row.PrincipalCity,
            "state": row.PrincipalState,
            "zip_code": row.PrincipalZipCode
        } if row.PrincipalStreet else None,
        "telefones": row.PhoneNumbers,
        "emails": row.EmailAddresses,
        "incorporation_date": row.incorporation_date,
        "created_at": row.CompanyCreatedAt
    }
```

---

### 2.2. POST /api/v1/companies/{id}/reactivate (15 min)

```python
# Adicionar após linha 353 (depois do delete_company)

@router.post("/{company_id}/reactivate", status_code=status.HTTP_200_OK)
async def reactivate_company(
    company_id: int,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Reativa empresa inativa (remove soft delete).
    
    Requer autenticação JWT + privilégios de superusuário.
    """
    repo = BaseRepository(Company, db)
    
    # Verificar se empresa existe
    company = await repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company não encontrada"
        )
    
    # Reativar (remover deleted_at)
    company = await repo.update(company_id, {"deleted_at": None})
    
    return {
        "message": "Empresa reativada com sucesso",
        "company_id": company_id
    }
```

---

### 2.3. GET /api/v1/companies/search (1h)

```python
# Adicionar após linha 95 (depois do list_companies_complete)

@router.get("/search", status_code=status.HTTP_200_OK)
async def search_companies(
    name: Optional[str] = Query(None, description="Buscar por razão social ou nome fantasia"),
    tax_id: Optional[str] = Query(None, description="Buscar por CNPJ"),
    city: Optional[str] = Query(None, description="Buscar por cidade"),
    state: Optional[str] = Query(None, description="Buscar por UF"),
    access_status: Optional[str] = Query(None, description="Filtrar por status"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca empresas por filtros avançados.
    
    Permite combinar múltiplos filtros.
    Requer autenticação JWT.
    """
    conditions = []
    params = {"skip": skip, "limit": limit}
    
    if name:
        conditions.append("(RazaoSocial LIKE :name OR NomeFantasia LIKE :name)")
        params["name"] = f"%{name}%"
    
    if tax_id:
        clean_tax_id = ''.join(filter(str.isdigit, tax_id))
        conditions.append("REPLACE(REPLACE(REPLACE(CNPJ, '.', ''), '/', ''), '-', '') LIKE :tax_id")
        params["tax_id"] = f"%{clean_tax_id}%"
    
    if city:
        conditions.append("PrincipalCity LIKE :city")
        params["city"] = f"%{city}%"
    
    if state:
        conditions.append("PrincipalState = :state")
        params["state"] = state.upper()
    
    if access_status:
        conditions.append("CompanyAccessStatus = :access_status")
        params["access_status"] = access_status
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = text(f"""
        SELECT * FROM [core].[vw_complete_company_data]
        WHERE {where_clause}
        ORDER BY CompanyId DESC
        OFFSET :skip ROWS
        FETCH NEXT :limit ROWS ONLY
    """)
    
    result = await db.execute(query, params)
    rows = result.fetchall()
    
    # Converter para lista
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
            "endereco": {
                "street": row.PrincipalStreet,
                "number": row.PrincipalNumber,
                "city": row.PrincipalCity,
                "state": row.PrincipalState
            } if row.PrincipalStreet else None,
            "telefones": row.PhoneNumbers,
            "emails": row.EmailAddresses
        })
    
    # Contar total
    count_query = text(f"""
        SELECT COUNT(*) as total FROM [core].[vw_complete_company_data]
        WHERE {where_clause}
    """)
    count_result = await db.execute(count_query, {k: v for k, v in params.items() if k not in ['skip', 'limit']})
    total = count_result.scalar()
    
    return {
        "total": total,
        "companies": companies
    }
```

---

### 2.4. GET /api/v1/companies/validate/cnpj/{cnpj} (15 min)

```python
# Adicionar após o endpoint de busca por CNPJ

@router.get("/validate/cnpj/{cnpj}")
async def validate_cnpj(
    cnpj: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Valida se CNPJ já está cadastrado.
    
    Retorna exists=true se encontrar, false caso contrário.
    Requer autenticação JWT.
    """
    from sqlalchemy import select
    
    # Remover formatação
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    
    if len(clean_cnpj) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido. Deve conter 14 dígitos."
        )
    
    # Buscar na tabela pj_profiles
    stmt = select(PJProfile).where(PJProfile.tax_id == clean_cnpj)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return {
            "exists": True,
            "company_id": existing.company_id,
            "pj_profile_id": existing.id
        }
    
    return {"exists": False}
```

---

### 2.5. GET /api/v1/companies/{id}/stats (1h)

```python
# Adicionar após o endpoint de get_company

@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna estatísticas agregadas da empresa.
    
    Conta estabelecimentos, clientes, profissionais e usuários.
    Requer autenticação JWT.
    """
    # Verificar se empresa existe
    repo = BaseRepository(Company, db)
    company = await repo.get_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company não encontrada"
        )
    
    # Buscar estatísticas
    query = text("""
        SELECT 
            :company_id as company_id,
            (SELECT COUNT(*) FROM [core].[establishments] 
             WHERE company_id = :company_id AND deleted_at IS NULL) as establishments_count,
            (SELECT COUNT(*) FROM [core].[users] 
             WHERE company_id = :company_id AND deleted_at IS NULL) as users_count
    """)
    
    result = await db.execute(query, {"company_id": company_id})
    row = result.fetchone()
    
    return {
        "company_id": row.company_id,
        "establishments_count": row.establishments_count,
        "users_count": row.users_count
    }
```

---

## 📝 FASE 3: UPDATE COMPLETO (3h)

### 3.1. Criar SP no Banco (2h)

**Arquivo:** `Database/XXX_sp_update_company_from_json.sql`

```sql
-- ⚠️ PRECISA SER CRIADO PELO DBA
-- Stored Procedure para atualizar empresa completa
-- Similar ao sp_create_company_from_json mas para UPDATE

CREATE OR ALTER PROCEDURE [core].[sp_update_company_from_json]
    @company_id BIGINT,
    @jsonData NVARCHAR(MAX)
AS
BEGIN
    -- Implementação completa pelo DBA
    -- Deve atualizar:
    -- 1. companies
    -- 2. people
    -- 3. pj_profiles
    -- 4. addresses (adicionar/atualizar/remover)
    -- 5. phones (adicionar/atualizar/remover)
    -- 6. emails (adicionar/atualizar/remover)
END
```

### 3.2. Criar Endpoint (1h)

```python
# Adicionar após o endpoint de update_company

@router.put("/{company_id}/complete", status_code=status.HTTP_200_OK)
async def update_company_complete(
    company_id: int,
    company_data: CompanyCompleteCreate,  # Reusar schema de create
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza empresa completa usando stored procedure.
    
    ⚠️ REQUER: sp_update_company_from_json no banco
    
    Atualiza em uma única transação:
    - Company
    - Person
    - PJ Profile
    - Addresses
    - Phones
    - Emails
    
    Requer autenticação JWT + privilégios de superusuário.
    """
    import json
    
    try:
        # Converter dados para JSON
        json_data = company_data.model_dump()
        
        # Executar stored procedure
        result = await db.execute(
            text("""
                EXEC [core].[sp_update_company_from_json] 
                @company_id = :company_id, 
                @jsonData = :json_data
            """),
            {
                "company_id": company_id,
                "json_data": json.dumps(json_data, default=str)
            }
        )
        
        # Capturar resultado
        row = result.fetchone()
        
        if not row or not row._mapping.get('Success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao atualizar empresa"
            )
        
        return {
            "message": "Empresa atualizada com sucesso",
            "company_id": company_id
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar empresa: {str(e)}"
        )
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### FASE 1: Ajustes Críticos
- [ ] Ajustar paginação no frontend
- [ ] Criar types corretos
- [ ] Ajustar método create()
- [ ] Testar criação de empresa

### FASE 2: Endpoints Backend
- [ ] Criar GET /cnpj/{cnpj}
- [ ] Criar POST /{id}/reactivate
- [ ] Criar GET /search
- [ ] Criar GET /validate/cnpj/{cnpj}
- [ ] Criar GET /{id}/stats
- [ ] Testar todos os endpoints

### FASE 3: UPDATE Completo
- [ ] Solicitar SP ao DBA
- [ ] Criar endpoint PUT /{id}/complete
- [ ] Testar atualização completa

### FASE 4: Testes Finais
- [ ] Testar CRUD completo
- [ ] Validar LGPD (mascaramento)
- [ ] Validar soft delete
- [ ] Validar reativação
- [ ] Documentar APIs

---

**Tempo Total:** 9 horas  
**Prioridade:** FASE 1 → FASE 2 → FASE 3 → FASE 4
