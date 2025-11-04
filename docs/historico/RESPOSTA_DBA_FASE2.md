# 📋 RESPOSTA DO DBA - FASE 2

**Data:** 22/10/2025 12:30 BRT  
**De:** DBA  
**Para:** Desenvolvedor  
**Assunto:** ✅ Análise Concluída e Script Aprovado

---

## 🎯 RESUMO EXECUTIVO

Análise completa realizada no banco `pro_team_care`. Encontramos estruturas existentes para **Dashboard** e identificamos a necessidade de criar tabelas para os outros 3 itens.

**Status:** ✅ **SCRIPT CRIADO E APROVADO**

---

## 📊 RESULTADO DA ANÁLISE

### **ITEM 5: Sessões Seguras** 🔒
- ❌ **Não existe** estrutura atual
- ✅ **Solução:** Criar tabela `[core].[user_sessions]`
- **Uso:** Rastrear sessões ativas via JTI, suportar personificação

### **ITEM 6: Dashboard** 📊
- ✅ **Já existe** estrutura parcial
- **Tabelas encontradas:**
  - `[core].[login_logs]` (pro_team_care_logs)
  - `[core].[lgpd_audit_log]` (pro_team_care_logs)
- ✅ **Solução:** Usar tabelas existentes + criar Views/SPs para estatísticas

### **ITEM 7: Notificações** 🔔
- ❌ **Não existe** estrutura atual
- ✅ **Solução:** Criar tabela `[core].[notifications]`
- **Uso:** Notificações in-app com tipos e soft delete

### **ITEM 8: Menus Dinâmicos** 🍔
- ❌ **Não existe** estrutura atual
- ✅ **Solução:** Criar tabelas `[core].[menu_items]` e `[core].[menu_item_permissions]`
- **Uso:** Menus hierárquicos baseados em permissões

---

## 📝 TABELAS CRIADAS

### **1. user_sessions** - Sessões Ativas
```sql
[core].[user_sessions]
├── id (PK)
├── user_id (FK → users)
├── jti (JWT ID único)
├── impersonator_user_id (FK → users, NULL se não houver)
├── created_at
└── expires_at

Índices:
- IX_user_sessions_jti (busca por token)
- IX_user_sessions_user_id (sessões do usuário)
- IX_user_sessions_expires_at (limpeza de expirados)
```

**Uso:**
- Invalidar tokens JWT específicos
- Rastrear personificação (impersonate)
- Limpar sessões expiradas

---

### **2. notifications** - Notificações In-App
```sql
[core].[notifications]
├── id (PK)
├── user_id (FK → users)
├── type (info, warning, success, error)
├── title
├── message
├── link (URL opcional)
├── is_read
├── read_at
├── created_at
└── deleted_at (soft delete)

Índices:
- IX_notifications_user_id (notificações do usuário)
- IX_notifications_is_read (não lidas)
- IX_notifications_created_at (ordenação)

Constraint:
- CHK_notifications_type (valida tipo)
```

**Uso:**
- Notificações in-app para usuários
- Marcar como lida
- Soft delete para histórico

---

### **3. menu_items** - Menus Dinâmicos
```sql
[core].[menu_items]
├── id (PK)
├── parent_id (FK → menu_items, NULL se raiz)
├── name (único)
├── label (exibição)
├── icon
├── path (rota)
├── display_order
├── is_active
├── created_at
├── updated_at
└── deleted_at (soft delete)

Índices:
- IX_menu_items_parent_id (hierarquia)
- IX_menu_items_display_order (ordenação)
- IX_menu_items_is_active (filtro)
```

**Uso:**
- Menus hierárquicos (parent/children)
- Ordenação customizada
- Soft delete

---

### **4. menu_item_permissions** - Permissões de Menus
```sql
[core].[menu_item_permissions]
├── menu_item_id (PK, FK → menu_items)
├── permission_id (PK, FK → permissions)
└── created_at

Índices:
- PK composta (menu_item_id, permission_id)
- IX_menu_item_permissions_permission_id (query reversa)
```

**Uso:**
- Relacionamento N:N entre menus e permissões
- Filtrar menus por permissões do usuário

---

## 🎯 INTEGRAÇÃO COM SISTEMA EXISTENTE

### **Dashboard - Tabelas Existentes**

#### **login_logs** (pro_team_care_logs)
```sql
SELECT TOP 10 
    user_id,
    email_address,
    login_at,
    ip_address,
    user_agent
FROM [core].[login_logs]
ORDER BY login_at DESC
```

#### **lgpd_audit_log** (pro_team_care_logs)
```sql
SELECT TOP 10
    user_id,
    action,
    table_name,
    record_id,
    created_at
FROM [core].[lgpd_audit_log]
ORDER BY created_at DESC
```

### **Estatísticas - Views Recomendadas**
```sql
-- View para estatísticas do dashboard
CREATE VIEW [core].[v_dashboard_stats] AS
SELECT
    (SELECT COUNT(*) FROM [core].[users] WHERE deleted_at IS NULL) as total_users,
    (SELECT COUNT(*) FROM [core].[users] WHERE is_active = 1 AND deleted_at IS NULL) as active_users,
    (SELECT COUNT(*) FROM [core].[companies] WHERE deleted_at IS NULL) as total_companies,
    (SELECT COUNT(*) FROM [core].[establishments] WHERE deleted_at IS NULL) as total_establishments,
    (SELECT COUNT(*) FROM [core].[roles] WHERE deleted_at IS NULL) as total_roles;
```

---

## 📄 SCRIPT SQL APROVADO

**Arquivo:** `Database/026_Create_Phase2_Tables.sql`

### **Características:**
- ✅ Transação segura (BEGIN TRY/CATCH)
- ✅ Verificação de existência
- ✅ FKs com CASCADE apropriadas
- ✅ Índices otimizados
- ✅ Constraints de validação
- ✅ Soft delete onde necessário
- ✅ Timestamps automáticos
- ✅ Mensagens de progresso

### **Como Executar:**
```bash
sqlcmd -S 192.168.11.83 -U sa -P SuaSenha -d pro_team_care \
  -i Database/026_Create_Phase2_Tables.sql
```

---

## 🚀 PRÓXIMOS PASSOS

### **1. Executar Script** ⏳
```bash
cd /home/juliano/Projetos/meu_projeto
sqlcmd -S 192.168.11.83 -U sa -P SuaSenha -d pro_team_care \
  -i Database/026_Create_Phase2_Tables.sql
```

### **2. Inserir Menus Padrão** ⏳
Após criar as tabelas, precisamos popular `menu_items` com os menus básicos do sistema.

**Sugestão de menus:**
```sql
-- Dashboard
INSERT INTO [core].[menu_items] (name, label, icon, path, display_order)
VALUES ('dashboard', 'Dashboard', 'home', '/dashboard', 1);

-- Usuários
INSERT INTO [core].[menu_items] (name, label, icon, path, display_order)
VALUES ('users', 'Usuários', 'users', '/users', 2);

-- Empresas
INSERT INTO [core].[menu_items] (name, label, icon, path, display_order)
VALUES ('companies', 'Empresas', 'building', '/companies', 3);

-- Estabelecimentos
INSERT INTO [core].[menu_items] (name, label, icon, path, display_order)
VALUES ('establishments', 'Estabelecimentos', 'map-pin', '/establishments', 4);

-- Roles
INSERT INTO [core].[menu_items] (name, label, icon, path, display_order)
VALUES ('roles', 'Roles', 'shield', '/roles', 5);
```

### **3. Criar Views de Dashboard** ⏳
```sql
-- View de estatísticas
CREATE VIEW [core].[v_dashboard_stats] AS ...

-- View de atividade recente
CREATE VIEW [core].[v_recent_activity] AS ...
```

### **4. Desenvolvedor Implementa Código** ⏳
- Models SQLAlchemy
- Schemas Pydantic
- Endpoints FastAPI
- Testes

---

## 📊 ESTIMATIVA DE TEMPO

| Tarefa | Tempo | Responsável |
|--------|-------|-------------|
| Executar script 026 | 5 min | DBA |
| Inserir menus padrão | 10 min | DBA |
| Criar views dashboard | 15 min | DBA |
| Implementar código | 16-23h | Desenvolvedor |
| **TOTAL** | **~17-24h** | - |

---

## ✅ VALIDAÇÕES REALIZADAS

- ✅ Nomenclatura consistente com padrão existente
- ✅ FKs apontam para tabelas corretas
- ✅ Índices nos campos mais consultados
- ✅ Soft delete onde apropriado
- ✅ Constraints de validação
- ✅ Integração com RBAC existente
- ✅ Compatibilidade com sistema de logs

---

## 💡 RECOMENDAÇÕES ADICIONAIS

### **Performance:**
1. Criar job para limpar sessões expiradas diariamente
2. Criar job para arquivar notificações antigas (>90 dias)
3. Considerar particionamento de `notifications` se crescer muito

### **Segurança:**
1. Auditar todas as ações de personificação
2. Limitar tempo máximo de personificação (ex: 1 hora)
3. Notificar usuário quando for personificado

### **Monitoramento:**
1. Alertar se muitas sessões ativas (possível vazamento de tokens)
2. Alertar se muitas notificações não lidas (>100)
3. Monitorar performance de queries de dashboard

---

## 📞 CONTATO

Se tiver dúvidas ou precisar de ajustes:
- DBA: [contato]
- Documentação: `FASE_2_FUNCIONALIDADES.md`
- Script: `Database/026_Create_Phase2_Tables.sql`

---

## 🎉 CONCLUSÃO

**Estrutura aprovada e pronta para execução!**

O script `026_Create_Phase2_Tables.sql` está otimizado, seguro e alinhado com as melhores práticas. Após a execução, o desenvolvedor terá toda a base necessária para implementar os 4 itens da Fase 2.

**Aguardando confirmação para executar o script.** 🚀

---

**Última atualização:** 22/10/2025 12:35 BRT
