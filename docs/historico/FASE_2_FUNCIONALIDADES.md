# 📋 FASE 2 - FUNCIONALIDADES IMPORTANTES

**Data:** 22/10/2025 09:50 BRT  
**Status:** 📝 **EM PLANEJAMENTO**  
**Estimativa:** 3-5 dias

---

## 🎯 OBJETIVO

Implementar funcionalidades essenciais do sistema antigo que são esperadas pelos usuários:
1. Sessões seguras (troca de perfil, personificação)
2. Dashboard com estatísticas
3. Sistema de notificações
4. Menus dinâmicos baseados em roles

---

## 📊 RESUMO DOS ITENS

| # | Item | Endpoints | Complexidade | Tempo Estimado |
|---|------|-----------|--------------|----------------|
| 5 | Sessões Seguras | 3 | Média | 4-6 horas |
| 6 | Dashboard | 2 | Baixa | 2-3 horas |
| 7 | Notificações | 3 | Média | 4-6 horas |
| 8 | Menus Dinâmicos | 6 | Alta | 6-8 horas |
| **TOTAL** | **4 itens** | **14 endpoints** | **-** | **16-23 horas** |

---

## 🔒 ITEM 5: SESSÕES SEGURAS (`/secure-sessions`)

### **Objetivo:**
Permitir que usuários troquem de perfil e que administradores personifiquem outros usuários.

### **Endpoints a implementar:**
1. `POST /secure-sessions/switch-profile` - Trocar perfil
2. `POST /secure-sessions/impersonate` - Personificar usuário
3. `POST /secure-sessions/end-impersonation` - Encerrar personificação

### **Funcionalidades:**

#### **1. Switch Profile (Trocar Perfil)**
- Usuário tem múltiplos roles em diferentes contextos
- Exemplo: Médico em Empresa A, Enfermeiro em Empresa B
- Ao trocar perfil, muda contexto ativo (company_id, establishment_id)
- Gera novo token JWT com contexto atualizado

#### **2. Impersonate (Personificar)**
- Apenas system_admin pode personificar
- Admin "vira" outro usuário temporariamente
- Token JWT contém:
  - `sub`: ID do usuário personificado
  - `impersonator_id`: ID do admin
  - `impersonating`: true
- Útil para suporte e debug

#### **3. End Impersonation (Encerrar)**
- Admin volta a ser ele mesmo
- Gera novo token JWT sem personificação

### **Banco de Dados:**
**⚠️ PRECISA VERIFICAR SE EXISTE:**
- Tabela `[core].[sessions]` ou similar?
- Campos em `[core].[users]` para contexto ativo?

**Possíveis ajustes:**
```sql
-- Adicionar campos em users (se não existir)
ALTER TABLE [core].[users] ADD
    active_company_id BIGINT NULL,
    active_establishment_id BIGINT NULL,
    active_role_id BIGINT NULL;

-- OU criar tabela de sessões
CREATE TABLE [core].[user_sessions] (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token_jti VARCHAR(255) NOT NULL,
    active_company_id BIGINT NULL,
    active_establishment_id BIGINT NULL,
    active_role_id BIGINT NULL,
    impersonator_id BIGINT NULL,
    is_impersonating BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    expires_at DATETIME2 NOT NULL,
    FOREIGN KEY (user_id) REFERENCES [core].[users](id)
);
```

### **Implementação:**
1. ✅ Verificar estrutura do banco
2. ⏳ Criar models (se necessário)
3. ⏳ Criar schemas Pydantic
4. ⏳ Criar endpoints
5. ⏳ Atualizar JWT para incluir contexto
6. ⏳ Testar fluxos

**Tempo estimado:** 4-6 horas

---

## 📊 ITEM 6: DASHBOARD (`/dashboard`)

### **Objetivo:**
Fornecer estatísticas e visão geral do sistema.

### **Endpoints a implementar:**
1. `GET /dashboard/stats` - Estatísticas gerais
2. `GET /dashboard/recent-activity` - Atividade recente

### **Funcionalidades:**

#### **1. Stats (Estatísticas)**
Retorna contadores gerais:
```json
{
  "users": {
    "total": 150,
    "active": 120,
    "inactive": 30
  },
  "companies": {
    "total": 25,
    "active": 20
  },
  "establishments": {
    "total": 50,
    "active": 45
  },
  "roles": {
    "total": 10
  }
}
```

#### **2. Recent Activity (Atividade Recente)**
Retorna últimas ações:
```json
{
  "activities": [
    {
      "id": 1,
      "user_id": 5,
      "user_name": "João Silva",
      "action": "created",
      "resource": "company",
      "resource_id": 10,
      "timestamp": "2025-10-22T09:30:00Z"
    }
  ]
}
```

### **Banco de Dados:**
**⚠️ PRECISA VERIFICAR SE EXISTE:**
- Tabela `[core].[audit_logs]` ou similar?
- Tabela `[core].[activity_logs]`?

**Possível ajuste:**
```sql
-- Criar tabela de logs de atividade (se não existir)
CREATE TABLE [core].[activity_logs] (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    resource_id BIGINT NULL,
    details NVARCHAR(MAX) NULL,
    ip_address VARCHAR(45) NULL,
    user_agent NVARCHAR(500) NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [core].[users](id)
);
```

### **Implementação:**
1. ✅ Verificar estrutura do banco
2. ⏳ Criar models (se necessário)
3. ⏳ Criar schemas Pydantic
4. ⏳ Criar endpoints
5. ⏳ Implementar queries de agregação
6. ⏳ Testar

**Tempo estimado:** 2-3 horas

---

## 🔔 ITEM 7: NOTIFICAÇÕES (`/notifications`)

### **Objetivo:**
Sistema de notificações in-app para usuários.

### **Endpoints a implementar:**
1. `GET /notifications/` - Listar notificações
2. `PUT /notifications/{id}/read` - Marcar como lida
3. `PUT /notifications/mark-all-read` - Marcar todas como lidas

### **Funcionalidades:**

#### **1. Listar Notificações**
Retorna notificações do usuário:
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 5,
      "type": "info",
      "title": "Novo usuário cadastrado",
      "message": "João Silva foi cadastrado no sistema",
      "is_read": false,
      "created_at": "2025-10-22T09:00:00Z"
    }
  ],
  "unread_count": 5
}
```

#### **2. Marcar como Lida**
Marca notificação específica como lida.

#### **3. Marcar Todas como Lidas**
Marca todas as notificações do usuário como lidas.

### **Banco de Dados:**
**⚠️ PRECISA VERIFICAR SE EXISTE:**
- Tabela `[core].[notifications]`?

**Possível estrutura:**
```sql
-- Criar tabela de notificações (se não existir)
CREATE TABLE [core].[notifications] (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(20) NOT NULL, -- info, warning, error, success
    title NVARCHAR(200) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    link VARCHAR(500) NULL,
    is_read BIT DEFAULT 0,
    read_at DATETIME2 NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    deleted_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES [core].[users](id)
);

-- Índices
CREATE INDEX IX_notifications_user_id ON [core].[notifications](user_id);
CREATE INDEX IX_notifications_is_read ON [core].[notifications](is_read);
```

### **Implementação:**
1. ✅ Verificar estrutura do banco
2. ⏳ Criar models
3. ⏳ Criar schemas Pydantic
4. ⏳ Criar endpoints
5. ⏳ Implementar filtros e paginação
6. ⏳ (Futuro) Integrar WebSocket para notificações em tempo real
7. ⏳ Testar

**Tempo estimado:** 4-6 horas

---

## 🍔 ITEM 8: MENUS DINÂMICOS (`/menus`)

### **Objetivo:**
Sistema de menus dinâmicos baseados em roles e permissões.

### **Endpoints a implementar:**
1. `GET /menus/` - Listar todos os menus
2. `GET /menus/dynamic` - Menus dinâmicos por role do usuário
3. `GET /menus/{id}` - Obter menu específico
4. `POST /menus/` - Criar menu
5. `PUT /menus/{id}` - Atualizar menu
6. `DELETE /menus/{id}` - Deletar menu

### **Funcionalidades:**

#### **1. Menus Dinâmicos**
Retorna menus baseados nas permissões do usuário:
```json
{
  "menus": [
    {
      "id": 1,
      "name": "dashboard",
      "label": "Dashboard",
      "icon": "home",
      "path": "/dashboard",
      "order": 1,
      "parent_id": null,
      "children": []
    },
    {
      "id": 2,
      "name": "users",
      "label": "Usuários",
      "icon": "users",
      "path": "/users",
      "order": 2,
      "parent_id": null,
      "children": [
        {
          "id": 3,
          "name": "users_list",
          "label": "Listar",
          "path": "/users",
          "order": 1,
          "parent_id": 2
        }
      ]
    }
  ]
}
```

#### **2. CRUD de Menus**
Gerenciamento completo de menus (admin).

### **Banco de Dados:**
**⚠️ PRECISA VERIFICAR SE EXISTE:**
- Tabela `[core].[menus]`?
- Tabela `[core].[menu_permissions]`?

**Possível estrutura:**
```sql
-- Criar tabela de menus (se não existir)
CREATE TABLE [core].[menus] (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    label NVARCHAR(200) NOT NULL,
    icon VARCHAR(50) NULL,
    path VARCHAR(500) NULL,
    order_index INT DEFAULT 0,
    parent_id BIGINT NULL,
    is_active BIT DEFAULT 1,
    required_permission VARCHAR(100) NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    deleted_at DATETIME2 NULL,
    FOREIGN KEY (parent_id) REFERENCES [core].[menus](id),
    FOREIGN KEY (required_permission) REFERENCES [core].[permissions](name)
);

-- Índices
CREATE INDEX IX_menus_parent_id ON [core].[menus](parent_id);
CREATE INDEX IX_menus_order_index ON [core].[menus](order_index);
```

### **Implementação:**
1. ✅ Verificar estrutura do banco
2. ⏳ Criar models
3. ⏳ Criar schemas Pydantic
4. ⏳ Criar endpoints
5. ⏳ Implementar lógica de hierarquia (parent/children)
6. ⏳ Implementar filtro por permissões
7. ⏳ Testar

**Tempo estimado:** 6-8 horas

---

## 📋 CHECKLIST GERAL

### **Antes de Começar:**
- [ ] Verificar estrutura do banco de dados
- [ ] Identificar tabelas existentes
- [ ] Criar script SQL com ajustes necessários
- [ ] Executar script SQL

### **Para Cada Item:**
- [ ] Criar models SQLAlchemy
- [ ] Criar schemas Pydantic
- [ ] Criar endpoints
- [ ] Registrar routers
- [ ] Testar endpoints
- [ ] Documentar

### **Após Conclusão:**
- [ ] Testar integração entre itens
- [ ] Atualizar documentação
- [ ] Criar guia de uso
- [ ] Preparar para Fase 3

---

## 🎯 ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

### **1º - Dashboard (2-3 horas)** ⭐ MAIS FÁCIL
- Menos dependências
- Queries simples
- Bom para começar

### **2º - Notificações (4-6 horas)**
- Funcionalidade independente
- Útil para outros módulos
- CRUD simples

### **3º - Sessões Seguras (4-6 horas)**
- Depende de roles (já implementado)
- Importante para UX
- Requer cuidado com JWT

### **4º - Menus Dinâmicos (6-8 horas)** ⭐ MAIS COMPLEXO
- Depende de permissões (já implementado)
- Hierarquia de menus
- Lógica mais complexa

---

## 🚀 PRÓXIMO PASSO

**AGUARDANDO VALIDAÇÃO:**

1. Você quer que eu **verifique o banco de dados** primeiro?
2. Ou prefere que eu **comece pela implementação** e te aviso se precisar de ajustes no banco?
3. Qual item quer implementar primeiro? (Recomendo: Dashboard)

---

**Última atualização:** 22/10/2025 09:55 BRT
