# 📋 Modelo Kanban Board - Documentação Completa

## 🎯 Visão Geral

Sistema de gestão de fluxo de trabalho estilo Kanban, evoluindo do modelo simples de "Activities" para um sistema completo de **Cards + Movements** com histórico auditável e rastreamento de tempo.

---

## 🗄️ Estrutura de Banco de Dados

### Tabelas Principais

#### 1. **[core].CardColumns**
Define as colunas do board (Backlog, A Fazer, Em Andamento, etc.)

```sql
- ColumnID (PK)
- CompanyID (FK)
- ColumnName (ex: "Backlog", "Em Andamento")
- DisplayOrder (ordem de exibição)
- Color (cor da coluna, ex: "#3B82F6")
- IsActive
```

**Colunas Padrão:**
1. Backlog (Cinza #6B7280)
2. A Fazer (Azul #3B82F6)
3. Em Andamento (Amarelo #F59E0B)
4. Revisão (Roxo #8B5CF6)
5. Concluído (Verde #10B981)

---

#### 2. **[core].Cards**
Card principal do board (substitui Activities + Pendencies)

```sql
- CardID (PK)
- CompanyID, UserID, ColumnID (FKs)
- Title (título do card)
- Description (descrição melhorada pela IA)
- OriginalText (texto original colado)
- SubStatus (ex: "Bloqueado - Depende de outro")
- Priority ("Baixa", "Média", "Alta", "Urgente")
- StartDate, DueDate, CompletedDate
- IsDeleted, DeletedAt (soft delete)
```

**SubStatus Possíveis:**
- `null` - Livre para trabalhar
- `"Bloqueado - Depende de outro"` - Aguardando outra pessoa/equipe
- `"Bloqueado - Depende de mim"` - Preciso fazer algo antes
- `"Aguardando aprovação"` - Aguardando validação

---

#### 3. **[core].CardMovements**
Histórico de movimentos/lançamentos (substitui ActivityContents)

```sql
- MovementID (PK)
- CardID, UserID (FKs)
- LogDate (data/hora do lançamento)
- Subject (assunto, ex: "CHG0076721 - Deploy Sprint 10")
- Description (descrição detalhada)
- TimeSpent (tempo gasto em MINUTOS)
- MovementType ("Update", "Comment", "StatusChange", "ColumnChange")
- OldColumnID, NewColumnID (auditoria de mudanças)
- OldSubStatus, NewSubStatus (auditoria de status)
```

**Tipos de Movimento:**
- `Update` - Atualização de progresso
- `Comment` - Comentário/observação
- `StatusChange` - Mudança de SubStatus
- `ColumnChange` - Moveu entre colunas (drag & drop)

---

#### 4. **[core].CardAssignees**
Pessoas responsáveis pelo card (N:N)

```sql
- AssigneeID (PK)
- CardID (FK)
- PersonName (nome da pessoa)
- PersonID (FK para Persons, opcional)
- AssignedAt
```

---

#### 5. **[core].CardTags**
Tags/categorias do card (N:N)

```sql
- CardTagID (PK)
- CardID (FK)
- TagName (ex: "Deploy", "Bug Fix")
- TagColor (ex: "#10B981")
```

---

#### 6. **[core].CardImages**
Imagens anexadas ao CARD (contexto geral)

```sql
- CardImageID (PK)
- CardID (FK)
- ImagePath
- ImageType ("problem", "solution", "reference", "diagram")
- Description
- UploadedBy, UploadedAt
```

**Quando usar CardImages:**
- Print do erro original
- Diagrama de arquitetura
- Screenshot do problema
- Documentação de referência

---

#### 7. **[core].MovementImages**
Imagens anexadas a MOVIMENTOS específicos (evidências)

```sql
- MovementImageID (PK)
- MovementID (FK)
- ImagePath
- ImageType ("evidence", "before", "after", "screenshot")
- Description
- UploadedAt
```

**Quando usar MovementImages:**
- Print da solução aplicada
- Evidência de deploy
- Screenshot "antes/depois"
- Comprovante de execução

---

### View: **[core].vw_CardTotalTime**
Calcula tempo total gasto por card

```sql
SELECT 
  CardID,
  Title,
  SUM(TimeSpent) AS TotalTimeSpentMinutes,
  SUM(TimeSpent) / 60 AS TotalTimeSpentHours,
  COUNT(MovementID) AS TotalMovements
FROM Cards + CardMovements
```

---

## 🤖 Análise da IA (Gemini)

### Novo Prompt Otimizado

A IA agora extrai:

1. **description** - Descrição profissional do card (2-3 frases)
2. **assignees** - Pessoas responsáveis
3. **systems** - Sistemas/tecnologias mencionados
4. **tags** - 3-5 tags para categorização
5. **priority** - "Baixa", "Média", "Alta", "Urgente"
6. **sub_status** - Impedimento se houver
7. **due_date** - Prazo (YYYY-MM-DD)
8. **movements** - Lista de sub-tarefas com:
   - `subject` - Título (preserva IDs de tickets)
   - `description` - Descrição detalhada
   - `estimated_time` - Tempo estimado em minutos
   - `assignee` - Responsável específico

### Exemplo de Resposta da IA

```json
{
  "description": "Realizar aprovações de mudanças da Sprint 10 do sistema PSCD. Inclui deploy de demandas homologadas, manutenção de performance e reconstrução de réplicas. Aguardando aprovação do gestor Ray.",
  "assignees": ["Ray", "Juliano"],
  "systems": ["PSCD", "RDM"],
  "tags": ["Gestão de Mudanças", "Deploy", "Performance", "Aprovação"],
  "priority": "Alta",
  "sub_status": "Aguardando aprovação",
  "due_date": "2025-11-10",
  "movements": [
    {
      "subject": "CHG0076721 - Deploy de Demandas Homologadas Sprint 10",
      "description": "Realizar deploy das demandas homologadas da Sprint 10 no ambiente de produção do PSCD",
      "estimated_time": 120,
      "assignee": "Juliano"
    },
    {
      "subject": "CHG0076643 - Manutenção de Performance PSCD",
      "description": "Aplicar otimizações de performance no banco de dados do PSCD",
      "estimated_time": 60,
      "assignee": null
    }
  ]
}
```

---

## 🎨 Interface (React)

### Componentes Principais

1. **KanbanBoard** - Board principal com drag & drop
2. **KanbanColumn** - Coluna do board
3. **KanbanCard** - Card individual
4. **CardDetailModal** - Modal com detalhes + histórico
5. **MovementForm** - Formulário para adicionar movimento
6. **TimeTracker** - Componente de rastreamento de tempo

### Bibliotecas Recomendadas

- **react-beautiful-dnd** - Drag & drop
- **date-fns** - Manipulação de datas
- **recharts** - Gráficos de tempo/produtividade

---

## 📊 Fluxo de Trabalho

### 1. Criação de Card

```
Usuário cola texto → IA analisa → Cria Card com:
  - Description (melhorada)
  - Assignees
  - Tags
  - Priority
  - SubStatus
  - Movements (sub-tarefas)
```

### 2. Movimentação no Board

```
Drag & Drop → Atualiza ColumnID → Cria Movement:
  - MovementType: "ColumnChange"
  - OldColumnID → NewColumnID
  - LogDate
```

### 3. Registro de Progresso

```
Usuário adiciona Movement → Preenche:
  - Subject
  - Description
  - TimeSpent (minutos)
  - Anexos (opcional)
```

### 4. Conclusão

```
Move para "Concluído" → Atualiza:
  - CompletedDate
  - Cria Movement final
  - Calcula tempo total
```

---

## 📈 Relatórios e Métricas

### Métricas Disponíveis

1. **Tempo Total por Card** - `vw_CardTotalTime`
2. **Tempo Médio por Coluna** - Calcular diferença entre movements
3. **Produtividade por Pessoa** - Somar TimeSpent por assignee
4. **Cards por Prioridade** - Agrupar por Priority
5. **Taxa de Conclusão** - Cards em "Concluído" vs Total
6. **Impedimentos** - Cards com SubStatus bloqueado

### Queries Úteis

```sql
-- Tempo total por card
SELECT * FROM [core].[vw_CardTotalTime]
WHERE CompanyID = 1
ORDER BY TotalTimeSpentMinutes DESC;

-- Cards bloqueados
SELECT CardID, Title, SubStatus
FROM [core].[Cards]
WHERE SubStatus LIKE 'Bloqueado%'
AND IsDeleted = 0;

-- Produtividade por pessoa
SELECT 
  ca.PersonName,
  SUM(cm.TimeSpent) / 60.0 AS HorasTrabalhadas,
  COUNT(DISTINCT c.CardID) AS CardsAtendidos
FROM [core].[CardAssignees] ca
JOIN [core].[Cards] c ON ca.CardID = c.CardID
LEFT JOIN [core].[CardMovements] cm ON c.CardID = cm.CardID
GROUP BY ca.PersonName
ORDER BY HorasTrabalhadas DESC;
```

---

## 🔄 Migração do Modelo Antigo

### Estratégia de Migração

**Opção 1: Hard Cut (Recomendado)**
- Executar script `046_Create_Kanban_Board_Tables.sql`
- Desativar rotas antigas (`/activities`, `/pendencies`)
- Implementar novas rotas (`/cards`, `/movements`)
- Não migrar dados antigos (começar limpo)

**Opção 2: Migração de Dados**
```sql
-- Migrar Activities para Cards
INSERT INTO [core].[Cards] (
  CompanyID, UserID, ColumnID,
  Title, OriginalText, 
  CreatedAt, IsDeleted
)
SELECT 
  CompanyID, UserID, 
  2 AS ColumnID, -- "A Fazer"
  Title, RawText,
  CreationDate, IsDeleted
FROM [core].[Activities];

-- Migrar Pendencies para Movements
INSERT INTO [core].[CardMovements] (
  CardID, UserID, LogDate,
  Subject, Description
)
SELECT 
  ActivityID, 1 AS UserID, GETUTCDATE(),
  Description, Impediment
FROM [core].[Pendencies];
```

---

## ✅ Checklist de Implementação

### Backend
- [ ] Executar script `046_Create_Kanban_Board_Tables.sql`
- [ ] Criar models Python (Card, CardMovement, etc.)
- [ ] Criar schemas Pydantic
- [ ] Criar repositories
- [ ] Criar services
- [ ] Criar endpoints FastAPI
- [ ] Testar com Postman/curl

### Frontend
- [ ] Instalar `react-beautiful-dnd`
- [ ] Criar componente KanbanBoard
- [ ] Criar componente KanbanCard
- [ ] Implementar drag & drop
- [ ] Criar modal de detalhes
- [ ] Criar formulário de movimento
- [ ] Implementar rastreamento de tempo
- [ ] Testar fluxo completo

### IA
- [x] Atualizar prompt Gemini
- [x] Atualizar parser de resposta
- [ ] Testar com dados reais
- [ ] Ajustar conforme feedback

---

## 🎯 Próximos Passos

1. **Executar script SQL** no banco de dados
2. **Criar models Python** para as novas tabelas
3. **Implementar endpoints** FastAPI
4. **Criar board React** com drag & drop
5. **Testar fluxo completo** de ponta a ponta
6. **Migrar dados** (se necessário)
7. **Desativar rotas antigas**

---

## 📚 Referências

- **Trello**: Inspiração para UI/UX
- **Jira**: Inspiração para workflows
- **react-beautiful-dnd**: https://github.com/atlassian/react-beautiful-dnd
- **FastAPI**: https://fastapi.tiangolo.com/

---

**Versão:** 1.0  
**Data:** 2025-11-03  
**Autor:** Cascade AI + Juliano
