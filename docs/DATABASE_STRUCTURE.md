# Estrutura do Banco de Dados - Pro Team Care

Documentação da estrutura do banco de dados SQL Server.

---

## ⚠️ Database First

Este projeto usa a abordagem **Database First**:

- ✅ Tabelas criadas **manualmente** no SQL Server
- ✅ Models SQLAlchemy apenas **mapeiam** as tabelas existentes
- ✅ **Nenhum** código cria ou altera tabelas automaticamente
- ✅ Schema: `[core]`
- ✅ Banco de dados: `pro_team_care`

---

## 📊 Tabelas

### 1. companies (Empresas/Tenants)

Armazena as empresas clientes (tenants) do sistema SaaS.

**Principais campos:**
- `id` - Chave primária
- `person_id` - FK para person (PJ principal)
- `access_status` - Status: pending_contract, contract_signed, active, suspended
- `settings` - JSON com configurações da empresa
- `metadata` - JSON com metadados adicionais
- `contract_*` - Campos de contrato e ativação
- `deleted_at` - Soft delete

---

### 2. people (Pessoas Físicas e Jurídicas)

Entidade polimórfica que armazena PF e PJ.

**Principais campos:**
- `id` - Chave primária
- `company_id` - FK para company
- `person_type` - "PF" ou "PJ"
- `name` - Nome completo (PF) ou Razão Social (PJ)
- `trade_name` - Nome Fantasia (PJ)
- `tax_id` - CPF (PF) ou CNPJ (PJ)
- `birth_date` - Data de nascimento (PF)
- `incorporation_date` - Data de constituição (PJ)
- `status` - active, inactive, pending, suspended, blocked
- `lgpd_*` - Campos relacionados à LGPD
- `metadata` - JSON com dados adicionais

---

### 3. establishments (Estabelecimentos/Unidades)

Filiais, unidades ou postos de atendimento de uma empresa.

**Principais campos:**
- `id` - Chave primária
- `person_id` - FK para person (dados cadastrais do estabelecimento)
- `company_id` - FK para company
- `code` - Código interno único
- `type` - matriz, filial, unidade, posto
- `category` - clinica, hospital, laboratorio, etc
- `is_principal` - Flag de matriz
- `operating_hours` - JSON com horários de funcionamento
- `service_areas` - JSON com áreas de atendimento
- `deleted_at` - Soft delete

---

### 4. roles (Papéis/Permissões)

Define os papéis e níveis de acesso do sistema.

**Principais campos:**
- `id` - Chave primária
- `name` - Nome único (ex: admin, medico, enfermeiro)
- `display_name` - Nome de exibição
- `level` - Nível hierárquico (0=mais alto)
- `context_type` - system, company, establishment
- `is_system_role` - Flag de papel do sistema (não editável)
- `settings` - JSON com permissões específicas

---

### 5. users (Usuários)

Contas de usuários que podem autenticar no sistema.

**Principais campos:**
- `id` - Chave primária
- `person_id` - FK opcional para person
- `company_id` - FK para company (**NULL para super admins do sistema**)
- `establishment_id` - FK para establishment padrão
- `email_address` - Email único
- `password` - Hash da senha (bcrypt)
- `is_active` - Flag de ativo
- `is_system_admin` - Flag de admin do sistema
- `notification_settings` - JSON com configurações de notificação
- `two_factor_*` - Campos para autenticação de dois fatores
- `last_login_at` - Data do último login
- `deleted_at` - Soft delete

**Tipos de usuários:**

1. **Super Admin do Sistema:**
   - `company_id = NULL`
   - `is_system_admin = TRUE`
   - Acesso a TODAS as companies
   - Role com `context_type = 'system'`, `context_id = 0`

2. **Admin de Company:**
   - `company_id = X` (específico)
   - `is_system_admin = FALSE`
   - Acesso apenas à company X
   - Role com `context_type = 'company'`, `context_id = X`

3. **Usuário de Estabelecimento:**
   - `company_id = X`
   - `establishment_id = Y`
   - Acesso ao estabelecimento Y da company X
   - Role com `context_type = 'establishment'`, `context_id = Y`

---

### 6. user_roles (Atribuição de Papéis)

Relacionamento many-to-many entre users e roles com contexto.

**Principais campos:**
- `id` - Chave primária
- `user_id` - FK para user
- `role_id` - FK para role
- `context_type` - system, company, establishment
- `context_id` - ID do contexto (company_id ou establishment_id). **Use 0 para context_type='system'**
- `status` - active, inactive, suspended, expired
- `assigned_by_user_id` - Quem atribuiu
- `expires_at` - Data de expiração (opcional)

**⚠️ Importante:** Quando `context_type = 'system'`, use `context_id = 0` (a coluna não aceita NULL)

---

### 7. phones (Telefones Polimórficos)

Armazena telefones associados a diferentes entidades (Person, Establishment, etc).

**Principais campos:**
- `id` - Chave primária
- `company_id` - FK para company
- `phoneable_type` - Tipo da entidade (Person, Establishment, etc)
- `phoneable_id` - ID da entidade proprietária
- `phone_number` - Número do telefone
- `country_code` - Código do país (padrão: +55)
- `area_code` - DDD / código de área
- `extension` - Ramal
- `type` - residencial, comercial, celular, recado
- `is_principal` - Telefone principal (único por entidade)
- `is_whatsapp` - Possui WhatsApp
- `whatsapp_verified_at` - Data de verificação do WhatsApp
- `contact_name` - Nome do contato (para recados)
- `contact_priority` - Prioridade de contato
- `carrier_name` - Nome da operadora
- `carrier_type` - movel, fixo, voip
- `api_data` - JSON com dados de APIs externas
- `deleted_at` - Soft delete

---

### 8. emails (Emails Polimórficos)

Armazena emails associados a diferentes entidades (Person, Establishment, etc).

**Principais campos:**
- `id` - Chave primária
- `company_id` - FK para company
- `emailable_type` - Tipo da entidade (Person, Establishment, etc)
- `emailable_id` - ID da entidade proprietária
- `email_address` - Endereço de email (único)
- `type` - pessoal, profissional, comercial, financeiro, suporte, outro
- `is_principal` - Email principal (único por entidade)
- `is_verified` - Email verificado
- `verified_at` - Data de verificação
- `verification_token` - Token para verificação
- `verification_expires_at` - Expiração do token
- `notes` - Observações
- `deleted_at` - Soft delete

---

### 9. addresses (Endereços Polimórficos)

Armazena endereços associados a diferentes entidades (Person, Establishment, etc).

**Principais campos:**
- `id` - Chave primária
- `company_id` - FK para company
- `addressable_type` - Tipo da entidade (Person, Establishment, etc)
- `addressable_id` - ID da entidade proprietária
- `postal_code` - CEP
- `street` - Logradouro
- `number` - Número
- `complement` - Complemento
- `neighborhood` - Bairro
- `city` - Cidade
- `state` - UF (2 letras)
- `country` - Código do país (padrão: BR)
- `type` - residencial, comercial, cobranca, entrega, correspondencia, outro
- `is_principal` - Endereço principal (único por entidade)
- `ibge_code` - Código IBGE do município
- `latitude` - Coordenada geográfica
- `longitude` - Coordenada geográfica
- `api_data` - JSON com dados de APIs externas (ex: ViaCEP)
- `deleted_at` - Soft delete

---

## 🔗 Relacionamentos

```
companies (1) ──┬─── (N) people
                ├─── (N) establishments
                ├─── (N) users
                ├─── (N) phones
                ├─── (N) emails
                └─── (N) addresses

people (1) ───────── (N) establishments

establishments (1) ── (N) users (establishment_id)

users (N) ────────── (N) roles (via user_roles)

Relacionamentos Polimórficos:
- phones      → Person, Establishment, Company (via phoneable_type/phoneable_id)
- emails      → Person, Establishment, Company (via emailable_type/emailable_id)
- addresses   → Person, Establishment, Company (via addressable_type/addressable_id)
```

---

## 📐 Schema Hierarchy

```
[core]
├── companies       (Tenants SaaS)
├── people          (PF/PJ polimórfico)
├── establishments  (Unidades/Filiais)
├── roles           (Papéis/Permissões)
├── users           (Contas de usuário)
├── user_roles      (Atribuição de papéis)
├── phones          (Telefones polimórficos)
├── emails          (Emails polimórficos)
└── addresses       (Endereços polimórficos)
```

---

## 🔒 Soft Delete

Todas as tabelas principais usam soft delete:

- `companies.deleted_at`
- `establishments.deleted_at`
- `users.deleted_at`
- `phones.deleted_at`
- `emails.deleted_at`
- `addresses.deleted_at`

Quando `deleted_at` está preenchido, o registro é considerado inativo.

---

## 📋 Campos JSON

Várias tabelas usam colunas JSON para flexibilidade:

**companies:**
- `settings` - Configurações (tema, módulos habilitados)
- `metadata` - Metadados adicionais

**people:**
- `metadata` - Dados adicionais

**establishments:**
- `settings` - Configurações específicas
- `metadata` - Metadados
- `operating_hours` - Horários: `{"monday": "08:00-18:00"}`
- `service_areas` - Áreas de atendimento

**roles:**
- `settings` - Permissões específicas

**users:**
- `notification_settings` - Preferências de notificação
- `two_factor_recovery_codes` - Códigos de recuperação

**phones:**
- `api_data` - Dados de APIs externas (validação, portabilidade, etc)

**addresses:**
- `api_data` - Dados de APIs externas (ViaCEP, geolocalização, etc)

---

## 🎯 Contextos (Multi-tenancy)

O sistema usa o conceito de **contextos** para multi-tenancy:

1. **system** - Nível de sistema (super admin)
2. **company** - Nível de empresa (tenant)
3. **establishment** - Nível de estabelecimento/unidade

Usuários podem ter diferentes papéis em diferentes contextos.

**Exemplo:**
- User A → Role "Admin" → Context: Company X (context_type='company', context_id=X)
- User A → Role "Médico" → Context: Establishment Y (context_type='establishment', context_id=Y)
- User B → Role "Super Admin" → Context: System (context_type='system', context_id=0)

---

## 🔑 Chaves e Índices

### Unique Constraints

- `companies.person_id` - UNIQUE
- `people.tax_id` + `company_id` - UNIQUE
- `establishments.code` + `company_id` - UNIQUE
- `roles.name` - UNIQUE
- `users.email_address` - UNIQUE
- `user_roles` (user_id, role_id, context_type, context_id) - UNIQUE
- `phones` (phoneable_type, phoneable_id) - UNIQUE WHERE `is_principal = 1 AND deleted_at IS NULL`
- `emails.email_address` - UNIQUE WHERE `deleted_at IS NULL`
- `emails` (emailable_type, emailable_id) - UNIQUE WHERE `is_principal = 1 AND deleted_at IS NULL`
- `addresses` (addressable_type, addressable_id) - UNIQUE WHERE `is_principal = 1 AND deleted_at IS NULL`

### Índices Filtrados

- `users.email_address` WHERE `deleted_at IS NULL`
- `establishments.company_id, is_active` WHERE `deleted_at IS NULL`
- `phones` (phoneable_type, phoneable_id, deleted_at)
- `emails` (emailable_type, emailable_id, deleted_at)
- `addresses` (addressable_type, addressable_id, deleted_at)
- `addresses` (city, state, deleted_at)
- `addresses` (postal_code, deleted_at)

---

## ✅ Checks

### companies
- `access_status` IN ('pending_contract', 'contract_signed', 'pending_user', 'active', 'suspended')

### people
- `person_type` IN ('PF', 'PJ')
- `status` IN ('active', 'inactive', 'pending', 'suspended', 'blocked')

### establishments
- `type` IN ('matriz', 'filial', 'unidade', 'posto')
- `category` IN ('clinica', 'hospital', 'laboratorio', 'farmacia', 'consultorio', 'upa', 'ubs', 'outro')

### roles
- `context_type` IN ('system', 'company', 'establishment')

### user_roles
- `context_type` IN ('system', 'company', 'establishment')
- `status` IN ('active', 'inactive', 'suspended', 'expired')

### phones
- `type` IN ('residencial', 'comercial', 'celular', 'recado')
- `carrier_type` IN ('movel', 'fixo', 'voip')

### emails
- `type` IN ('pessoal', 'profissional', 'comercial', 'financeiro', 'suporte', 'outro')

### addresses
- `type` IN ('residencial', 'comercial', 'cobranca', 'entrega', 'correspondencia', 'outro')

---

## 📝 Exemplo de Dados

### Criar uma Company

```sql
INSERT INTO [core].[companies] (
    person_id, access_status, display_order,
    created_at, updated_at
) VALUES (
    NULL, 'pending_contract', 0,
    GETDATE(), GETDATE()
);
```

### Criar uma Person (PJ para Company)

```sql
INSERT INTO [core].[people] (
    company_id, person_type, name, tax_id,
    status, created_at, updated_at
) VALUES (
    1, 'PJ', 'Acme Corporation LTDA', '12.345.678/0001-90',
    'active', GETDATE(), GETDATE()
);
```

### Criar um User

```sql
INSERT INTO [core].[users] (
    email_address, password, company_id,
    is_active, is_system_admin,
    created_at, updated_at
) VALUES (
    'admin@acme.com', '$2b$12$...', 1,
    1, 0,
    GETDATE(), GETDATE()
);
```

---

## 🔍 Queries Úteis

### Listar Companies ativas

```sql
SELECT * FROM [core].[companies]
WHERE deleted_at IS NULL
  AND access_status = 'active';
```

### Listar Users de uma Company

```sql
SELECT u.* FROM [core].[users] u
WHERE u.company_id = 1
  AND u.deleted_at IS NULL;
```

### Listar Roles de um User

```sql
SELECT r.* FROM [core].[roles] r
INNER JOIN [core].[user_roles] ur ON ur.role_id = r.id
WHERE ur.user_id = 1
  AND ur.status = 'active';
```

---

## 📚 Referências

- Extended Properties: Descrições completas nos metadados do banco
- Constraints: FKs, Checks, Unique definidos no script de criação
- Índices: Otimizados para queries mais comuns
