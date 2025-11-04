# 🎯 FASE 1: MVP BÁSICO - Implementação

**Data:** 21/10/2025  
**Status:** Em Andamento

---

## ✅ ITEM 1: `/auth/me` com Dados Completos

### **Status:** ✅ **CONCLUÍDO**

### **O que foi feito:**
- ✅ Schema `UserMeResponse` criado com campos adicionais
- ✅ Endpoint atualizado com JOINs para `people`, `companies`, `establishments`
- ✅ Retorna `full_name`, `company_name`, `establishment_name`
- ✅ Retorna lista de `establishments` da empresa

### **Arquivos modificados:**
- `backend/app/schemas/user.py`
- `backend/app/api/v1/auth.py`

---

## 🔄 ITEM 2: `/auth/refresh` - Refresh Token

### **Status:** ✅ **CONCLUÍDO**

### **O que precisa:**
- ❌ **NÃO PRECISA** de novas tabelas
- ✅ Usa tabela `users` existente
- ✅ JWT com payload incluindo `exp` (expiration)

### **Como funciona no sistema antigo:**
```python
@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: Request, db=Depends(get_db)):
    # 1. Pega token do header Authorization
    # 2. Decodifica token (permite expirado)
    # 3. Valida se usuário ainda existe e está ativo
    # 4. Gera novo token JWT
    # 5. Retorna novo token
```

### **Implementação realizada:**
1. ✅ Endpoint `POST /api/v1/auth/refresh` criado
2. ✅ Aceita token expirado (`verify_exp=False`)
3. ✅ Valida usuário ainda está ativo
4. ✅ Gera novo token JWT
5. ✅ Retorna `TokenResponse`

### **Arquivos modificados:**
- ✅ `backend/app/api/v1/auth.py` (endpoint adicionado)

### **Como funciona:**
```python
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: Request, db=Depends(get_db)):
    # 1. Pega token do header Authorization
    # 2. Decodifica token (permite expirado: verify_exp=False)
    # 3. Valida se usuário ainda existe e está ativo
    # 4. Gera novo token JWT
    # 5. Retorna novo token
```

### **Teste:**
```bash
# Com token expirado
curl -X POST http://192.168.11.83:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer <token_expirado>"
```

---

## 🔑 ITEM 3: `/password-reset/*` - Recuperação de Senha

### **Status:** ✅ **CONCLUÍDO**

### **O que precisa:**
- ✅ **SCRIPT SQL CRIADO:** `Database/025_Implement_RBAC_And_PasswordReset.sql`
- ✅ Adiciona campos na tabela `users`:
  - `password_reset_token` (NVARCHAR(255))
  - `password_reset_expires_at` (DATETIME2)
  - `password_changed_at` (DATETIME2)

### **Endpoints necessários:**

#### **3.1. POST `/auth/forgot-password`**
```python
# Request: { "email": "user@example.com" }
# Response: { "success": true, "message": "..." }
# 
# Fluxo:
# 1. Busca usuário por email
# 2. Gera token único (UUID)
# 3. Salva token + expires_at (1 hora)
# 4. Envia email com link
# 5. SEMPRE retorna sucesso (segurança)
```

#### **3.2. POST `/auth/validate-reset-token`**
```python
# Request: { "token": "abc123..." }
# Response: { "success": true, "message": "Token válido" }
#
# Fluxo:
# 1. Busca usuário por token
# 2. Verifica se não expirou
# 3. Verifica se usuário está ativo
# 4. Retorna validação
```

#### **3.3. POST `/auth/reset-password`**
```python
# Request: { "token": "abc123...", "new_password": "newpass123" }
# Response: { "success": true, "message": "Senha redefinida" }
#
# Fluxo:
# 1. Valida token
# 2. Hasheia nova senha (bcrypt)
# 3. Atualiza password + password_changed_at
# 4. Limpa token usado
# 5. Retorna sucesso
```

### **Implementação realizada:**
1. ✅ **SCRIPT SQL EXECUTADO** - Campos criados no banco
2. ✅ Schemas Pydantic criados (`backend/app/schemas/password_reset.py`)
3. ✅ 3 endpoints implementados em `backend/app/api/v1/auth.py`:
   - `POST /auth/forgot-password`
   - `POST /auth/validate-reset-token`
   - `POST /auth/reset-password`
4. ⚠️ Email simulado (logs no console) - Integrar serviço real em produção

### **Arquivos criados/modificados:**
- ✅ `backend/app/schemas/password_reset.py` (novo)
- ✅ `backend/app/api/v1/auth.py` (3 endpoints adicionados)

### **Como testar:**
```bash
# 1. Solicitar reset
curl -X POST http://192.168.11.83:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email_address":"admin@proteamcare.com.br"}'

# 2. Copiar token do log do backend (console)

# 3. Validar token
curl -X POST http://192.168.11.83:8000/api/v1/auth/validate-reset-token \
  -H "Content-Type: application/json" \
  -d '{"token":"<token_aqui>"}'

# 4. Redefinir senha
curl -X POST http://192.168.11.83:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"<token_aqui>","new_password":"NovaSenha@123"}'

# 5. Fazer login com nova senha
curl -X POST http://192.168.11.83:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email_address":"admin@proteamcare.com.br","password":"NovaSenha@123"}'
```

---

## 🎭 ITEM 4: Sistema Básico de Roles/Permissões

### **Status:** ✅ **CONCLUÍDO**

### **O que precisa:**
- ✅ **SCRIPT SQL CRIADO:** `Database/025_Implement_RBAC_And_PasswordReset.sql`
- ✅ Cria 2 novas tabelas + atualiza 2 existentes:
  1. `[core].[permissions]` - **NOVA** - Permissões do sistema
  2. `[core].[role_permissions]` - **NOVA** - Relacionamento N:N
  3. `[core].[roles]` - **ATUALIZADA** - Adiciona deleted_at
  4. `[core].[user_roles]` - **ATUALIZADA** - Adiciona expires_at, deleted_at, assigned_by_user_id

### **Estrutura criada:**

#### **Tabela: roles (existente, atualizada)**
```sql
- id (BIGINT, PK)
- name (NVARCHAR(50), UNIQUE) -- Ex: system_admin, company_admin
- display_name (NVARCHAR(100)) -- Ex: Administrador do Sistema
- description (NVARCHAR(500))
- level (INT) -- Hierarquia (0 = mais poder)
- context_type (NVARCHAR(20)) -- system, company, establishment
- is_active (BIT)
- is_system_role (BIT) -- Não pode ser deletada
- created_at, updated_at, deleted_at
```

#### **Tabela: permissions (nova)**
```sql
- id (BIGINT, PK)
- name (NVARCHAR(100), UNIQUE) -- Ex: users.view, companies.create
- display_name (NVARCHAR(100))
- description (NVARCHAR(500))
- resource (NVARCHAR(50)) -- users, companies, etc
- action (NVARCHAR(50)) -- view, create, update, delete, manage
- is_active (BIT)
- created_at, updated_at, deleted_at
```

#### **Tabela: role_permissions (nova)**
```sql
- id (BIGINT, PK)
- role_id (BIGINT, FK → roles)
- permission_id (BIGINT, FK → permissions)
- created_at
```

#### **Tabela: user_roles (existente, atualizada)**
```sql
- id (BIGINT, PK)
- user_id (BIGINT, FK → users)
- role_id (BIGINT, FK → roles)
- context_type (NVARCHAR(20)) -- system, company, establishment
- context_id (INT) -- ID da company ou establishment
- status (NVARCHAR(20)) -- active, inactive, expired, revoked
- expires_at (DATETIME2) -- Role temporária
- assigned_by_user_id (BIGINT, FK → users) -- **NOVO**
- assigned_at, created_at, updated_at, deleted_at
```

### **Roles padrão criadas:**
1. **system_admin** (level 0) - Acesso total
2. **company_admin** (level 10) - Gerencia empresa
3. **establishment_admin** (level 20) - Gerencia estabelecimento
4. **manager** (level 50) - Gerencia equipes
5. **user** (level 100) - Usuário padrão

### **Permissões básicas criadas:**
- **users:** view, create, update, delete, manage
- **companies:** view, create, update, delete, manage
- **establishments:** view, create, update, delete, manage
- **roles:** view, create, update, delete, manage

### **Endpoints necessários:**

#### **4.1. GET `/roles/`**
```python
# Lista todos os roles
# Filtros: is_active, context_type
# Paginação: page, size
```

#### **4.2. GET `/roles/{id}`**
```python
# Obter role por ID
# Inclui permissões associadas
```

#### **4.3. POST `/roles/`**
```python
# Criar novo role
# Requer: system_admin
```

#### **4.4. PUT `/roles/{id}`**
```python
# Atualizar role
# Requer: system_admin
```

#### **4.5. DELETE `/roles/{id}`**
```python
# Deletar role (soft delete)
# Não permite deletar is_system_role=true
# Requer: system_admin
```

#### **4.6. GET `/roles/{id}/permissions`**
```python
# Listar permissões do role
```

#### **4.7. PUT `/roles/{id}/permissions`**
```python
# Atualizar permissões do role
# Body: { "permission_ids": [1, 2, 3] }
```

#### **4.8. GET `/users/{id}/roles`**
```python
# Listar roles do usuário
# Já existe, mas precisa atualizar para usar nova tabela
```

#### **4.9. PUT `/users/{id}/roles`**
```python
# Atribuir roles ao usuário
# Body: { "role_ids": [1, 2], "context_type": "company", "context_id": 1 }
```

### **Implementação realizada:**
1. ✅ **SCRIPT SQL EXECUTADO** - Tabelas e permissões criadas
2. ✅ Models SQLAlchemy criados (`backend/app/models/permission.py`)
   - Permission, RolePermission, UserRole
3. ✅ Schemas Pydantic criados (`backend/app/schemas/role.py`)
   - 15+ schemas para CRUD completo
4. ✅ Endpoints implementados (`backend/app/api/v1/roles.py`)
   - 11 endpoints de roles e permissões
5. ✅ Decorators de permissões (`backend/app/core/permissions.py`)
   - `@require_permission`, `@require_any_permission`, `@require_all_permissions`
6. ✅ Router registrado e backend reiniciado

### **Arquivos criados:**
- ✅ `backend/app/models/permission.py` - Models (Permission, RolePermission, UserRole)
- ✅ `backend/app/schemas/role.py` - Schemas Pydantic completos
- ✅ `backend/app/api/v1/roles.py` - 11 endpoints
- ✅ `backend/app/core/permissions.py` - Decorators e funções auxiliares

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### **Passo 1: Banco de Dados** ✅
- [x] Executar `Database/025_Implement_RBAC_And_PasswordReset.sql`
- [x] Verificar se todas as tabelas foram criadas
- [x] Verificar se permissões foram inseridas
- [x] Verificar se admin recebeu permissões

### **Passo 2: Refresh Token** ✅
- [x] Criar endpoint `POST /auth/refresh`
- [ ] Testar com token válido
- [ ] Testar com token expirado
- [ ] Testar com usuário inativo

### **Passo 3: Password Reset** ✅
- [x] Criar schemas Pydantic
- [x] Criar endpoint `POST /auth/forgot-password`
- [x] Criar endpoint `POST /auth/validate-reset-token`
- [x] Criar endpoint `POST /auth/reset-password`
- [ ] Testar fluxo completo
- [ ] (Futuro) Integrar email service real

### **Passo 4: Roles/Permissões** ✅
- [x] Criar models SQLAlchemy
- [x] Criar schemas Pydantic
- [x] Criar arquivo `backend/app/api/v1/roles.py`
- [x] Implementar 11 endpoints de roles
- [x] Criar decorators de permissões
- [ ] Testar CRUD completo
- [ ] (Futuro) Integrar decorators nos endpoints existentes

---

## 🎯 ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

### **1º - Banco de Dados (5 minutos)**
```bash
# Executar script SQL
sqlcmd -S 192.168.11.83 -U sa -P SuaSenha -d pro_team_care -i Database/025_Implement_RBAC_And_PasswordReset.sql
```

### **2º - Refresh Token (30 minutos)**
- Mais simples
- Não depende de email
- Melhora UX imediatamente

### **3º - Password Reset (1-2 horas)**
- Funcionalidade crítica
- Pode usar logs ao invés de email inicialmente
- Testar com Postman

### **4º - Roles/Permissões (3-4 horas)**
- Mais complexo
- Requer models, schemas, endpoints
- Base para controle de acesso avançado

---

## 📊 ESTIMATIVA DE TEMPO

| Item | Complexidade | Tempo Estimado |
|------|--------------|----------------|
| 1. `/auth/me` completo | ✅ Fácil | ✅ **CONCLUÍDO** |
| 2. `/auth/refresh` | 🟢 Fácil | 30 min |
| 3. `/password-reset/*` | 🟡 Médio | 1-2 horas |
| 4. Roles/Permissões | 🔴 Complexo | 3-4 horas |
| **TOTAL** | | **~5-7 horas** |

---

## 🚀 PRÓXIMOS PASSOS

### **AGORA:**
1. **EXECUTAR SCRIPT SQL** `025_Implement_RBAC_And_PasswordReset.sql`
2. Verificar se tudo foi criado corretamente
3. Confirmar que admin tem role system_admin

### **DEPOIS:**
4. Implementar `/auth/refresh`
5. Implementar `/password-reset/*`
6. Implementar sistema de roles

---

## 📝 NOTAS IMPORTANTES

### **Sobre Password Reset:**
- ⚠️ Token expira em 1 hora (segurança)
- ⚠️ Sempre retorna sucesso em `/forgot-password` (não revela se email existe)
- ⚠️ Token é invalidado após uso
- ⚠️ Pode usar logs ao invés de email inicialmente

### **Sobre Roles:**
- ⚠️ Roles do sistema (`is_system_role=true`) não podem ser deletadas
- ⚠️ Usuário pode ter múltiplos roles
- ⚠️ Roles podem ser temporárias (`expires_at`)
- ⚠️ Hierarquia por `level` (menor = mais poder)

### **Sobre Permissões:**
- ⚠️ Formato: `resource.action` (ex: `users.view`)
- ⚠️ Actions: view, create, update, delete, manage
- ⚠️ Decorator `@require_permission` valida automaticamente

---

**Última atualização:** 21/10/2025 16:00 BRT
