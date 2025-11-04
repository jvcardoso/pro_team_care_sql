# 📋 REQUISIÇÃO AO DBA - FASE 2

**Data:** 22/10/2025  
**Solicitante:** Desenvolvedor  
**Prioridade:** Média  
**Prazo:** 1-2 dias

---

## 🎯 OBJETIVO

Analisar o banco de dados **antigo/atual** para identificar estruturas existentes relacionadas aos 4 itens da Fase 2:

1. **Sessões Seguras** (switch profile, impersonate)
2. **Dashboard** (estatísticas, atividades)
3. **Notificações** (in-app notifications)
4. **Menus Dinâmicos** (menus baseados em roles)

---

## 📊 O QUE PRECISO

Para cada item abaixo, preciso saber:
- ✅ **Tabelas existentes** (nome, schema, estrutura)
- ✅ **Dados de exemplo** (3-5 registros para entender o formato)
- ✅ **Relacionamentos** (FKs, constraints)
- ✅ **Índices** (se houver)
- ✅ **Views/SPs** relacionadas (se houver)

---

## 🔍 ITEM 1: SESSÕES SEGURAS

### **Funcionalidades:**
- Trocar perfil (usuário com múltiplos roles em diferentes empresas)
- Personificar usuário (admin vira outro usuário temporariamente)
- Rastrear sessões ativas

### **Tabelas a buscar:**
Procurar tabelas com nomes contendo:
- `session`, `sessao`, `sessoes`
- `impersonate`, `personificar`
- `switch`, `profile`, `perfil`
- `active_context`, `contexto_ativo`

### **Campos esperados:**
```sql
-- Exemplo de estrutura esperada
TABLE user_sessions (
    id BIGINT,
    user_id BIGINT,
    token_jti VARCHAR,
    active_company_id BIGINT,
    active_establishment_id BIGINT,
    active_role_id BIGINT,
    impersonator_id BIGINT NULL,
    is_impersonating BIT,
    created_at DATETIME2,
    expires_at DATETIME2
)
```

### **Perguntas:**
1. Existe tabela de sessões?
2. Usuários têm campo de contexto ativo (company_id, establishment_id)?
3. Existe histórico de personificação?
4. Como é rastreado o perfil ativo do usuário?

---

## 📊 ITEM 2: DASHBOARD

### **Funcionalidades:**
- Estatísticas gerais (contadores de users, companies, etc)
- Atividade recente (últimas ações dos usuários)
- Logs de auditoria

### **Tabelas a buscar:**
Procurar tabelas com nomes contendo:
- `dashboard`, `stats`, `statistics`, `estatisticas`
- `activity`, `atividade`, `atividades`
- `audit`, `auditoria`, `log`, `logs`
- `event`, `evento`, `eventos`

### **Campos esperados:**
```sql
-- Exemplo de estrutura esperada
TABLE activity_logs (
    id BIGINT,
    user_id BIGINT,
    action VARCHAR(50),           -- created, updated, deleted
    resource VARCHAR(50),          -- user, company, etc
    resource_id BIGINT,
    details NVARCHAR(MAX),         -- JSON com detalhes
    ip_address VARCHAR(45),
    user_agent NVARCHAR(500),
    created_at DATETIME2
)
```

### **Perguntas:**
1. Existe tabela de logs de atividade?
2. Existe tabela de auditoria?
3. Que tipo de eventos são registrados?
4. Existe agregação de estatísticas (tabela summary)?
5. Como são calculadas as estatísticas do dashboard?

---

## 🔔 ITEM 3: NOTIFICAÇÕES

### **Funcionalidades:**
- Notificações in-app para usuários
- Marcar como lida
- Tipos de notificação (info, warning, error, success)
- Link para recurso relacionado

### **Tabelas a buscar:**
Procurar tabelas com nomes contendo:
- `notification`, `notificacao`, `notificacoes`
- `alert`, `alerta`, `alertas`
- `message`, `mensagem`, `mensagens`
- `inbox`, `caixa_entrada`

### **Campos esperados:**
```sql
-- Exemplo de estrutura esperada
TABLE notifications (
    id BIGINT,
    user_id BIGINT,
    type VARCHAR(20),              -- info, warning, error, success
    title NVARCHAR(200),
    message NVARCHAR(MAX),
    link VARCHAR(500) NULL,
    is_read BIT DEFAULT 0,
    read_at DATETIME2 NULL,
    created_at DATETIME2,
    deleted_at DATETIME2 NULL
)
```

### **Perguntas:**
1. Existe tabela de notificações?
2. Que tipos de notificações existem?
3. Como são enviadas (in-app, email, push)?
4. Existe histórico de notificações deletadas?
5. Existe agrupamento de notificações?

---

## 🍔 ITEM 4: MENUS DINÂMICOS

### **Funcionalidades:**
- Menus baseados em roles/permissões
- Hierarquia de menus (parent/children)
- Ícones e paths
- Ordenação customizada

### **Tabelas a buscar:**
Procurar tabelas com nomes contendo:
- `menu`, `menus`
- `navigation`, `navegacao`
- `sidebar`, `menu_item`, `item_menu`
- `menu_permission`, `menu_role`

### **Campos esperados:**
```sql
-- Exemplo de estrutura esperada
TABLE menus (
    id BIGINT,
    name VARCHAR(100),             -- Identificador único
    label NVARCHAR(200),           -- Nome de exibição
    icon VARCHAR(50),              -- Nome do ícone
    path VARCHAR(500),             -- Rota/URL
    order_index INT,               -- Ordem de exibição
    parent_id BIGINT NULL,         -- Menu pai (hierarquia)
    required_permission VARCHAR(100) NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME2,
    updated_at DATETIME2,
    deleted_at DATETIME2 NULL
)

-- Relacionamento com permissões
TABLE menu_permissions (
    id BIGINT,
    menu_id BIGINT,
    permission_id BIGINT
)
```

### **Perguntas:**
1. Existe tabela de menus?
2. Como é feita a hierarquia (parent_id)?
3. Menus são filtrados por role ou por permissão?
4. Existe cache de menus por usuário?
5. Como são definidos os ícones?

---

## 📝 FORMATO DE RESPOSTA ESPERADO

Para cada item, fornecer:

### **1. Lista de Tabelas**
```
[schema].[nome_tabela] - Descrição
Registros: X
```

### **2. Estrutura (DDL)**
```sql
-- Script CREATE TABLE ou resultado de sp_help
```

### **3. Dados de Exemplo**
```sql
-- SELECT TOP 5 com dados reais (pode anonimizar se necessário)
```

### **4. Relacionamentos**
```sql
-- FKs, constraints, índices
```

### **5. Observações**
- Qualquer particularidade
- Campos calculados
- Triggers
- Views relacionadas

---

## 🚀 PRÓXIMOS PASSOS

Após receber as informações:

1. ✅ Desenvolvedor analisa estruturas existentes
2. ✅ Desenvolvedor cria especificação de tabelas necessárias
3. ✅ DBA valida e ajusta especificação
4. ✅ DBA cria script SQL
5. ✅ DBA executa script
6. ✅ Desenvolvedor implementa código Python

---

## 📞 CONTATO

Se tiver dúvidas ou precisar de mais informações:
- Desenvolvedor: [seu contato]
- Documentação: `/home/juliano/Projetos/meu_projeto/FASE_2_FUNCIONALIDADES.md`

---

## 🔍 SCRIPT DE ANÁLISE

Criei um script Python que pode ajudar na análise:
- **Arquivo:** `analise_banco_antigo_fase2.py`
- **Como usar:**
  ```bash
  cd /home/juliano/Projetos/meu_projeto
  cd backend
  source venv/bin/activate
  
  # Ajustar credenciais no script se necessário
  python3 ../analise_banco_antigo_fase2.py
  ```

O script busca automaticamente tabelas relacionadas e gera um JSON com a estrutura.

---

## ⚠️ IMPORTANTE

- Se não existirem tabelas para algum item, **tudo bem!**
- Vou criar a especificação do zero
- Se existirem, vou aproveitar a estrutura existente
- Prioridade: **manter compatibilidade** com sistema antigo (se houver)

---

**Aguardo retorno para prosseguir com a Fase 2!** 🚀

---

**Última atualização:** 22/10/2025 10:05 BRT
