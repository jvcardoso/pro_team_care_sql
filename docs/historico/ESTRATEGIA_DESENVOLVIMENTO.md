# 🎯 ESTRATÉGIA DE DESENVOLVIMENTO INCREMENTAL

## ✅ **SITUAÇÃO ATUAL**

### **Frontend**
- ✅ **30+ páginas migradas** (pro_team_care_16)
- ✅ **Sistema completo de componentes**
- ✅ **Autenticação corrigida** (email_address)
- ✅ **CORS configurado**
- ⚠️ **Algumas páginas vão dar erro** (tabelas ainda não existem)

### **Backend**
- ✅ **Estrutura base criada**
- ✅ **Autenticação funcionando**
- ✅ **Companies com stored procedure**
- ✅ **View completa de companies**
- ⚠️ **Faltam algumas tabelas** (você está remodelando)

---

## 🎯 **ABORDAGEM: DESENVOLVIMENTO INCREMENTAL**

Você vai **implementar as tabelas aos poucos** no backend, e o frontend já está pronto para usar quando estiverem prontas!

---

## 📋 **PLANO DE IMPLEMENTAÇÃO**

### **FASE 1: CORE (ATUAL)** ✅

Tabelas já implementadas:

```sql
✅ companies
✅ people
✅ pj_profiles
✅ pf_profiles
✅ users
✅ roles
✅ user_roles
✅ phones
✅ emails
✅ addresses
✅ login_logs
```

**Páginas funcionando:**
- ✅ Login
- ✅ Dashboard (básico)
- ✅ Companies (com CRUD completo)
- ✅ Users

---

### **FASE 2: ESTABELECIMENTOS** 🔄

Tabelas a implementar:

```sql
⚠️ establishments
⚠️ establishment_types
⚠️ establishment_services
```

**Páginas que vão funcionar:**
- EstablishmentsPage
- Gestão de filiais/unidades

**Stored Procedures necessárias:**
- `sp_create_establishment_from_json`
- `sp_update_establishment`

**Views necessárias:**
- `vw_complete_establishment_data`

---

### **FASE 3: CONTRATOS** 🔄

Tabelas a implementar:

```sql
⚠️ contracts
⚠️ contract_types
⚠️ contract_items
⚠️ contract_lives
⚠️ contract_acceptance_logs
```

**Páginas que vão funcionar:**
- ContractsPage
- ContractAcceptancePage
- ClientsPage (depende de contracts)

**Stored Procedures necessárias:**
- `sp_create_contract`
- `sp_accept_contract`
- `sp_add_contract_life`

---

### **FASE 4: FATURAMENTO** 🔄

Tabelas a implementar:

```sql
⚠️ invoices
⚠️ invoice_items
⚠️ payments
⚠️ subscription_plans
⚠️ recurrent_billing
```

**Páginas que vão funcionar:**
- BillingDashboardPage
- InvoicesPage
- B2BBillingPage
- SubscriptionPlansPage

**Stored Procedures necessárias:**
- `sp_generate_invoice`
- `sp_process_payment`
- `sp_create_recurrent_billing`

---

### **FASE 5: AUTORIZAÇÕES MÉDICAS** 🔄

Tabelas a implementar:

```sql
⚠️ medical_authorizations
⚠️ authorization_types
⚠️ authorization_items
⚠️ authorization_status_history
```

**Páginas que vão funcionar:**
- MedicalAuthorizationsPage
- Workflow de aprovação

**Stored Procedures necessárias:**
- `sp_create_medical_authorization`
- `sp_approve_authorization`
- `sp_reject_authorization`

---

### **FASE 6: CATÁLOGO DE SERVIÇOS** 🔄

Tabelas a implementar:

```sql
⚠️ services
⚠️ service_categories
⚠️ service_prices
⚠️ service_contracts
```

**Páginas que vão funcionar:**
- ServicesCatalogPage
- Gestão de preços

---

### **FASE 7: PROFISSIONAIS E PACIENTES** 🔄

Tabelas a implementar:

```sql
⚠️ professionals
⚠️ professional_specialties
⚠️ patients
⚠️ patient_medical_records
```

**Páginas que vão funcionar:**
- ProfissionaisPage
- PacientesPage
- ConsultasPage

---

### **FASE 8: RELATÓRIOS** 🔄

Tabelas a implementar:

```sql
⚠️ reports
⚠️ report_templates
⚠️ report_schedules
```

**Páginas que vão funcionar:**
- ReportsPage
- Dashboard completo com gráficos

---

## 🔧 **COMO TRABALHAR INCREMENTALMENTE**

### **1. Escolha uma FASE**

Exemplo: Vou implementar ESTABELECIMENTOS

### **2. Crie as tabelas no SQL Server**

```sql
-- 024_Create_Establishments_Tables.sql
CREATE TABLE [core].[establishments] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    company_id INT NOT NULL,
    person_id INT NULL,
    establishment_type VARCHAR(50),
    ...
);
```

### **3. Crie Stored Procedures**

```sql
-- 025_Create_Establishment_From_JSON.sql
CREATE OR ALTER PROCEDURE [core].[sp_create_establishment_from_json]
    @jsonData NVARCHAR(MAX)
AS
BEGIN
    -- Lógica similar à sp_create_company_from_json
END;
```

### **4. Crie Views**

```sql
-- 026_Create_Complete_Establishment_View.sql
CREATE OR ALTER VIEW [core].[vw_complete_establishment_data]
AS
SELECT
    e.id,
    e.company_id,
    p.name,
    ...
FROM establishments e
LEFT JOIN people p ON e.person_id = p.id;
```

### **5. Implemente Endpoints no Backend**

```python
# app/api/v1/endpoints/establishments.py
@router.post("/")
async def create_establishment(data: EstablishmentCreate):
    # Chamar sp_create_establishment_from_json
    pass

@router.get("/complete-list")
async def list_establishments():
    # Usar vw_complete_establishment_data
    pass
```

### **6. Teste no Frontend**

```bash
# Frontend já tem a página pronta!
# Acesse: http://192.168.11.83:3000/establishments
```

---

## 🎨 **DESABILITANDO PÁGINAS TEMPORARIAMENTE**

Enquanto não implementa uma fase, você pode desabilitar as páginas no menu:

### **Opção 1: Comentar rotas**

```jsx
// src/App.jsx
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/dashboard" element={<DashboardPage />} />
  <Route path="/companies" element={<CompaniesPage />} />
  
  {/* ⚠️ Desabilitado até implementar tabelas */}
  {/* <Route path="/establishments" element={<EstablishmentsPage />} /> */}
  {/* <Route path="/contracts" element={<ContractsPage />} /> */}
</Routes>
```

### **Opção 2: Criar página "Em Desenvolvimento"**

```jsx
// src/pages/UnderDevelopmentPage.jsx
export const UnderDevelopmentPage = ({ feature }) => (
  <div className="p-8 text-center">
    <h1 className="text-2xl font-bold mb-4">
      {feature} - Em Desenvolvimento
    </h1>
    <p>Esta funcionalidade será implementada em breve.</p>
  </div>
);

// Usar nas rotas:
<Route path="/establishments" element={
  <UnderDevelopmentPage feature="Estabelecimentos" />
} />
```

---

## 📊 **PRIORIZAÇÃO SUGERIDA**

Baseado na importância e dependências:

| Fase | Prioridade | Tempo Estimado | Dependências |
|------|------------|----------------|--------------|
| **1. Core** | ✅ FEITO | - | Nenhuma |
| **2. Estabelecimentos** | 🔥 ALTA | 8h | Companies |
| **3. Contratos** | 🔥 ALTA | 12h | Companies, Establishments |
| **4. Faturamento** | 🟡 MÉDIA | 16h | Contracts |
| **5. Autorizações** | 🟡 MÉDIA | 12h | Contracts, Professionals |
| **6. Catálogo** | 🟢 BAIXA | 8h | Nenhuma |
| **7. Profissionais** | 🔥 ALTA | 10h | Nenhuma |
| **8. Relatórios** | 🟢 BAIXA | 6h | Todas |

---

## 🚀 **WORKFLOW RECOMENDADO**

### **Para cada FASE:**

```bash
# 1. Criar branch
git checkout -b feature/establishments

# 2. Criar tabelas SQL
cd Database
# Criar: 024_Create_Establishments_Tables.sql

# 3. Executar no banco
python3 execute_corrections_simple.py Jvc@1702

# 4. Criar stored procedures
# Criar: 025_Create_Establishment_From_JSON.sql

# 5. Criar views
# Criar: 026_Create_Complete_Establishment_View.sql

# 6. Implementar backend
cd ../backend/app/api/v1/endpoints
# Criar: establishments.py

# 7. Testar
cd ../../..
pytest tests/test_establishments.py -v

# 8. Testar no frontend
cd ../../frontend
npm run dev
# Acessar: http://192.168.11.83:3000/establishments

# 9. Commit
git add .
git commit -m "feat: implementar estabelecimentos"
git push origin feature/establishments
```

---

## 📝 **TEMPLATE DE STORED PROCEDURE**

Use como base para novas entidades:

```sql
-- ###_Create_ENTITY_From_JSON.sql
CREATE OR ALTER PROCEDURE [core].[sp_create_ENTITY_from_json]
    @jsonData NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Variáveis
        DECLARE @entityId INT;
        DECLARE @personId INT;
        
        -- 1. Criar Person (se necessário)
        INSERT INTO [core].[people] (name, ...)
        VALUES (...);
        SET @personId = SCOPE_IDENTITY();
        
        -- 2. Criar Entidade Principal
        INSERT INTO [core].[ENTITY] (person_id, ...)
        VALUES (@personId, ...);
        SET @entityId = SCOPE_IDENTITY();
        
        -- 3. Inserir contatos (phones, emails, addresses)
        -- Similar ao sp_create_company_from_json
        
        -- 4. Retornar IDs
        SELECT 
            @entityId AS new_entity_id,
            @personId AS new_person_id,
            'Entidade criada com sucesso' AS message;
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
```

---

## 📝 **TEMPLATE DE VIEW**

```sql
-- ###_Create_Complete_ENTITY_View.sql
CREATE OR ALTER VIEW [core].[vw_complete_ENTITY_data]
AS
WITH AllPhones AS (
    SELECT entity_id, STRING_AGG(ph.number, ', ') AS PhoneNumbers
    FROM [core].[ENTITY] e
    JOIN [core].[phones] ph ON e.id = ph.phoneable_id 
        AND ph.phoneable_type = 'ENTITY'
    GROUP BY entity_id
),
AllEmails AS (
    SELECT entity_id, STRING_AGG(em.email_address, ', ') AS EmailAddresses
    FROM [core].[ENTITY] e
    JOIN [core].[emails] em ON e.id = em.emailable_id 
        AND em.emailable_type = 'ENTITY'
    GROUP BY entity_id
)
SELECT
    e.id,
    e.company_id,
    p.name,
    phones.PhoneNumbers,
    emails.EmailAddresses,
    ...
FROM [core].[ENTITY] e
LEFT JOIN [core].[people] p ON e.person_id = p.id
LEFT JOIN AllPhones phones ON e.id = phones.entity_id
LEFT JOIN AllEmails emails ON e.id = emails.entity_id;
GO
```

---

## ✅ **CHECKLIST POR FASE**

### **Estabelecimentos**
- [ ] Tabela `establishments`
- [ ] Tabela `establishment_types`
- [ ] SP `sp_create_establishment_from_json`
- [ ] View `vw_complete_establishment_data`
- [ ] Endpoint POST `/establishments`
- [ ] Endpoint GET `/establishments/complete-list`
- [ ] Testar no frontend

### **Contratos**
- [ ] Tabela `contracts`
- [ ] Tabela `contract_types`
- [ ] Tabela `contract_lives`
- [ ] SP `sp_create_contract`
- [ ] SP `sp_accept_contract`
- [ ] View `vw_complete_contract_data`
- [ ] Endpoints CRUD
- [ ] Testar no frontend

---

## 🎯 **RESUMO**

1. ✅ **Frontend completo migrado** (30+ páginas prontas)
2. ✅ **Backend base funcionando** (auth, companies)
3. 🔄 **Implementar tabelas aos poucos** (seguir fases)
4. ✅ **Frontend já funciona** quando backend estiver pronto
5. 📝 **Usar templates** para acelerar desenvolvimento

---

**🚀 Próximo passo:** Escolha uma FASE e comece a implementar!

**Sugestão:** Comece por **ESTABELECIMENTOS** (FASE 2)
