# 📊 View: `vw_complete_company_data`

## ✅ **SIM, ESTA VIEW É EXTREMAMENTE ÚTIL!**

---

## 🎯 **PROPÓSITO**

Simplifica a consulta de dados completos de empresas, agregando informações de múltiplas tabelas em uma única view com:
- ✅ Mascaramento automático LGPD
- ✅ Dados agregados (telefones, emails)
- ✅ Performance otimizada
- ✅ Apenas endereço principal

---

## 📋 **DADOS RETORNADOS**

### **Informações da Empresa**
- `CompanyId` - ID da empresa
- `CompanyAccessStatus` - Status de acesso (pending_contract, active, etc)
- `CompanyCreatedAt` - Data de criação

### **Dados da Pessoa Jurídica**
- `PersonId` - ID da pessoa
- `PjProfileId` - ID do perfil PJ
- `RazaoSocial` - Nome completo da empresa
- `NomeFantasia` - Nome fantasia (mascarado se sem permissão)
- `CNPJ` - CNPJ mascarado conforme LGPD
- `incorporation_date` - Data de constituição

### **Endereço Principal**
- `PrincipalStreet` - Logradouro
- `PrincipalNumber` - Número
- `PrincipalNeighborhood` - Bairro
- `PrincipalCity` - Cidade
- `PrincipalState` - UF
- `PrincipalZipCode` - CEP

### **Contatos Agregados**
- `PhoneNumbers` - Todos os telefones separados por vírgula
- `EmailAddresses` - Todos os e-mails separados por vírgula

---

## 🔒 **LGPD - MASCARAMENTO AUTOMÁTICO**

### **Nome Fantasia**
```sql
-- COM permissão: "Clínica Viva Bem"
-- SEM permissão: "Clí..."
```

### **CNPJ**
```sql
-- COM permissão: "11222333000144"
-- SEM permissão: "11.***.***/**-**44"
```

**Controle:** Função `fn_CanUserUnmaskData()` verifica permissões do usuário

---

## 🚀 **COMO USAR**

### **1. SQL Direto**

```sql
-- Listar todas as empresas
SELECT * FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;

-- Buscar empresa específica
SELECT * FROM [core].[vw_complete_company_data]
WHERE CompanyId = 159;

-- Buscar por cidade
SELECT * FROM [core].[vw_complete_company_data]
WHERE PrincipalCity = 'São Paulo';

-- Com paginação
SELECT * FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC
OFFSET 0 ROWS
FETCH NEXT 10 ROWS ONLY;
```

### **2. API Endpoint**

**Novo endpoint criado:** `GET /api/v1/companies/complete-list`

```bash
# Obter token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email_address": "admin@proteamcare.com.br", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Listar empresas completas
curl -X GET "http://localhost:8000/api/v1/companies/complete-list?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Resposta:**
```json
{
    "total": 159,
    "companies": [
        {
            "company_id": 159,
            "access_status": "contract_signed",
            "person_id": 101,
            "pj_profile_id": 25,
            "razao_social": "Clinica Saúde e Vida LTDA",
            "nome_fantasia": "Clínica Viva Bem",
            "cnpj": "11.***.***/**-**44",
            "endereco": {
                "street": "Rua das Flores",
                "number": "123",
                "neighborhood": "Centro",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01001000"
            },
            "telefones": "1155551234, 1155555678",
            "emails": "contato@vivabem.com.br, financeiro@vivabem.com.br",
            "incorporation_date": "2015-08-22",
            "created_at": "2025-10-21T10:00:00"
        }
    ]
}
```

---

## ✅ **VANTAGENS**

### **1. Simplificação de Código**

**❌ ANTES (sem view):**
```python
# 6+ queries separadas
company = await get_company(id)
person = await get_person(company.person_id)
pj_profile = await get_pj_profile(person.id)
addresses = await get_addresses(pj_profile.id)
phones = await get_phones(pj_profile.id)
emails = await get_emails(pj_profile.id)
```

**✅ DEPOIS (com view):**
```python
# 1 única query
result = await db.execute(
    text("SELECT * FROM vw_complete_company_data WHERE CompanyId = :id"),
    {"id": company_id}
)
```

### **2. Performance**

| Aspecto | Sem View | Com View |
|---------|----------|----------|
| **Queries** | 6+ | 1 |
| **Round-trips** | 6+ | 1 |
| **Complexidade** | Alta | Baixa |
| **Manutenção** | Difícil | Fácil |

### **3. LGPD Compliance**

- ✅ Mascaramento automático no banco
- ✅ Não precisa implementar na API
- ✅ Consistente em todo o sistema
- ✅ Auditável

### **4. Agregação Automática**

- ✅ Telefones em uma string
- ✅ Emails em uma string
- ✅ Apenas endereço principal
- ✅ Dados prontos para exibição

---

## 🔧 **CORREÇÕES REALIZADAS**

### **Problema Original**
```sql
-- ❌ ERRADO
JOIN core.phones ph ON p.id = ph.phoneable_id 
    AND ph.phoneable_type = 'App\Models\PjProfile'
```

### **Correção Aplicada**
```sql
-- ✅ CORRETO
JOIN core.phones ph ON pjp.person_id = ph.phoneable_id 
    AND ph.phoneable_type = 'Person'
```

**Mesmas correções em:**
- ✅ Phones JOIN
- ✅ Emails JOIN
- ✅ Addresses JOIN

---

## 📊 **CASOS DE USO**

### **1. Dashboard de Empresas**
```sql
-- Top 10 empresas mais recentes
SELECT TOP 10 
    CompanyId,
    RazaoSocial,
    NomeFantasia,
    PrincipalCity,
    CompanyCreatedAt
FROM [core].[vw_complete_company_data]
ORDER BY CompanyCreatedAt DESC;
```

### **2. Relatório de Empresas por Estado**
```sql
-- Agrupar por estado
SELECT 
    PrincipalState,
    COUNT(*) as Total
FROM [core].[vw_complete_company_data]
WHERE PrincipalState IS NOT NULL
GROUP BY PrincipalState
ORDER BY Total DESC;
```

### **3. Busca de Empresas**
```sql
-- Buscar por nome
SELECT * FROM [core].[vw_complete_company_data]
WHERE RazaoSocial LIKE '%Clínica%'
   OR NomeFantasia LIKE '%Clínica%';
```

### **4. Exportação de Dados**
```sql
-- Exportar para CSV/Excel
SELECT 
    CompanyId,
    RazaoSocial,
    CNPJ,
    PrincipalCity,
    PrincipalState,
    PhoneNumbers,
    EmailAddresses
FROM [core].[vw_complete_company_data]
ORDER BY RazaoSocial;
```

---

## 🎯 **QUANDO USAR**

### ✅ **USE a View quando:**
- Listar empresas em grids/tabelas
- Exportar relatórios
- Dashboards e estatísticas
- Busca e filtros
- Dados para exibição (read-only)

### ❌ **NÃO use a View quando:**
- Criar/atualizar dados (use stored procedure)
- Precisar de dados não mascarados (use queries diretas com permissões)
- Precisar de relacionamentos complexos (use JOINs específicos)

---

## 🔄 **INTEGRAÇÃO COM SISTEMA**

### **Fluxo Completo**

```
1. CRIAR EMPRESA
   POST /api/v1/companies/complete
   └─> Stored Procedure: sp_create_company_from_json
       └─> Cria: Company + Person + PJ Profile + Contacts

2. LISTAR EMPRESAS
   GET /api/v1/companies/complete-list
   └─> View: vw_complete_company_data
       └─> Retorna: Dados agregados + LGPD mascarado

3. CONSULTAR EMPRESA
   GET /api/v1/companies/{id}
   └─> Query direta ou View
       └─> Retorna: Dados completos
```

---

## 📚 **ARQUIVOS RELACIONADOS**

| Arquivo | Descrição |
|---------|-----------|
| `Database/023_Create_Complete_Company_View.sql` | Definição da view (CORRIGIDA) |
| `backend/app/api/v1/companies.py` | Endpoint `/complete-list` |
| `Database/022_Create_Company_From_JSON.sql` | Stored procedure de criação |
| `CONSTRAINTS_VALORES_ACEITOS.md` | Valores válidos para constraints |

---

## ✅ **CONCLUSÃO**

**SIM, esta view é MUITO ÚTIL e resolve vários problemas:**

1. ✅ **Simplifica queries complexas** - 1 query ao invés de 6+
2. ✅ **LGPD automático** - Mascaramento no banco
3. ✅ **Performance** - Dados agregados e otimizados
4. ✅ **Manutenção** - Centraliza lógica de negócio
5. ✅ **Consistência** - Mesma estrutura em todo sistema

**Recomendação:** Use esta view para TODAS as listagens de empresas no sistema!

---

## 🚀 **PRÓXIMOS PASSOS**

1. ✅ **Executar script corrigido no banco**
   ```sql
   -- Executar: Database/023_Create_Complete_Company_View.sql
   ```

2. ✅ **Testar endpoint**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/companies/complete-list" \
     -H "Authorization: Bearer $TOKEN"
   ```

3. ✅ **Usar no frontend**
   - Substituir queries complexas pela view
   - Exibir dados agregados diretamente
   - Aproveitar mascaramento LGPD automático
