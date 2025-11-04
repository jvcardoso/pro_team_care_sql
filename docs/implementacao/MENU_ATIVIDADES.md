# 📋 Cadastro do Módulo de Atividades no Menu

**Script:** `043_Add_Activities_Module_To_Menu.sql`  
**Data:** 2025-11-03

---

## 🎯 O que o Script Faz

### 1. Cria Permissões (5)
- `activities.view` - Visualizar Atividades
- `activities.create` - Criar Atividades
- `activities.edit` - Editar Atividades
- `pendencies.view` - Visualizar Pendências
- `pendencies.manage` - Gerenciar Pendências

### 2. Cria Estrutura de Menu
```
📋 Atividades (menu principal)
  ├── 📄 Minhas Atividades (/activities)
  ├── ➕ Nova Atividade (/activities/new)
  └── 📊 Board de Pendências (/pendencies)
```

### 3. Associa Permissões aos Menus
- **Minhas Atividades** → `activities.view`
- **Nova Atividade** → `activities.create`
- **Board de Pendências** → `pendencies.view`

### 4. Associa ao Role Superuser
Todas as 5 permissões são automaticamente associadas ao role `superuser`.

---

## 🚀 Como Executar

### Opção 1: SQL Server Management Studio (SSMS)
```sql
-- 1. Abrir o arquivo
Database/043_Add_Activities_Module_To_Menu.sql

-- 2. Conectar ao servidor
Server: 192.168.11.84
Database: pro_team_care
User: sa

-- 3. Executar (F5)
```

### Opção 2: Azure Data Studio
```sql
-- 1. Abrir o arquivo
-- 2. Conectar ao servidor
-- 3. Clicar em "Run" ou Ctrl+Shift+E
```

### Opção 3: Linha de Comando (sqlcmd)
```bash
sqlcmd -S 192.168.11.84 -U sa -P Jvc@1702 -d pro_team_care -i Database/043_Add_Activities_Module_To_Menu.sql
```

---

## ✅ Validação

### 1. Verificar Permissões Criadas
```sql
SELECT * FROM [core].[permissions]
WHERE name LIKE 'activities.%' OR name LIKE 'pendencies.%'
ORDER BY name;
```

**Resultado esperado:** 5 linhas

### 2. Verificar Menus Criados
```sql
SELECT 
    m.id,
    m.name,
    m.label,
    m.icon,
    m.path,
    m.display_order,
    CASE WHEN m.parent_id IS NULL THEN 'Menu Principal' ELSE 'Submenu' END AS tipo
FROM [core].[menu_items] m
WHERE m.name IN ('atividades', 'minhas_atividades', 'nova_atividade', 'board_pendencias')
ORDER BY m.parent_id, m.display_order;
```

**Resultado esperado:** 4 linhas (1 menu principal + 3 submenus)

### 3. Verificar Associações Menu-Permissão
```sql
SELECT 
    m.label AS Menu,
    p.display_name AS Permissao
FROM [core].[menu_item_permissions] mp
JOIN [core].[menu_items] m ON mp.menu_item_id = m.id
JOIN [core].[permissions] p ON mp.permission_id = p.id
WHERE m.name IN ('minhas_atividades', 'nova_atividade', 'board_pendencias')
ORDER BY m.display_order;
```

**Resultado esperado:** 3 linhas

### 4. Verificar Permissões do Superuser
```sql
SELECT 
    r.name AS Role,
    p.display_name AS Permissao
FROM [core].[role_permissions] rp
JOIN [core].[roles] r ON rp.role_id = r.id
JOIN [core].[permissions] p ON rp.permission_id = p.id
WHERE r.name = 'superuser'
  AND p.name LIKE 'activities.%' OR p.name LIKE 'pendencies.%'
ORDER BY p.name;
```

**Resultado esperado:** 5 linhas

---

## 🎨 Ícones Utilizados

| Menu | Ícone | Descrição |
|------|-------|-----------|
| Atividades | `clipboard-list` | Menu principal |
| Minhas Atividades | `list` | Listagem |
| Nova Atividade | `plus-circle` | Criar novo |
| Board de Pendências | `trello` | Board Kanban |

**Biblioteca:** Lucide Icons (já utilizada no projeto)

---

## 🔍 Troubleshooting

### Erro: "Role Superuser não encontrado"
**Causa:** Script 040_Seed_System_Roles.sql não foi executado  
**Solução:** Executar o script 040 primeiro

### Erro: "Violation of PRIMARY KEY constraint"
**Causa:** Script já foi executado anteriormente  
**Solução:** Normal, o script é idempotente (pode rodar múltiplas vezes)

### Menu não aparece no frontend
**Possíveis causas:**
1. Usuário não tem permissão
2. Cache do frontend não foi limpo
3. Stored procedure `sp_get_dynamic_menus` precisa ser atualizada

**Solução:**
```sql
-- Verificar permissões do usuário
EXEC [core].[sp_get_dynamic_menus] @user_id = 1; -- Substituir pelo ID do usuário
```

---

## 📊 Estrutura Final do Menu

Após execução, o menu do sistema terá:

```
🏠 Dashboard
📁 Cadastros
   ├── Pessoas
   ├── Usuários
   ├── Empresas
   └── Estabelecimentos
📋 Atividades ⭐ NOVO
   ├── Minhas Atividades
   ├── Nova Atividade
   └── Board de Pendências
🛡️ Segurança
   ├── Roles
   ├── Permissões
   └── Logs de Auditoria
```

---

## 🎯 Próximos Passos

Após executar o script:

1. **Fazer logout e login** - Para recarregar permissões
2. **Verificar menu** - Deve aparecer "Atividades" no menu lateral
3. **Testar acesso** - Clicar em cada submenu
4. **Criar atividade** - Testar fluxo completo

---

## 📝 Notas

- Script é **idempotente** (pode rodar múltiplas vezes sem erro)
- Usa **transação** (rollback automático em caso de erro)
- Compatível com estrutura existente de menus
- Segue padrão dos scripts anteriores (028, 033)

---

**Script pronto para execução pelo DBA!**
