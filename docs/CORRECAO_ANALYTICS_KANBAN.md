# 🔧 Correção - Analytics do Kanban

## 🎯 Problema Identificado

**Analytics mostrando 0 cards concluídos** mesmo após importação bem-sucedida.

### **Sintomas:**
```
✅ Importação: 99/99 cards
✅ Colunas: Corretas
❌ Analytics: 0 cards concluídos
❌ Lead Time: N/A
❌ Throughput: 0
```

---

## 🔍 Causa Raiz

### **1. Movimentos Incompletos:**
A SP `sp_UpsertCardFromImport` criava apenas 1 movimento:
```sql
-- ❌ ANTES: Só registrava criação
INSERT INTO CardMovements (CardID, UserID, LogDate, Subject, OldColumnID, NewColumnID)
VALUES (@NewCardID, @UserID, @StartDate, 'Card Criado', NULL, @ColumnID);
```

**Problema:** Analytics precisa de movimentos de **conclusão** para calcular métricas!

### **2. View Depende de Movimentos:**
A view `vw_CardFullHistory` usa `CardMovements` para calcular:
- Lead Time (Criação → Conclusão)
- Cycle Time (Início → Conclusão)
- Throughput (Cards com movimento para "Concluído")
- Time per Stage (Tempo em cada coluna)

**Sem movimentos de conclusão = Analytics vazio!**

---

## ✅ Correção Implementada

### **1. Registro Completo de Movimentos:**

```sql
-- Movimento 1: Card criado
INSERT INTO CardMovements (...)
VALUES (@NewCardID, @UserID, @CreatedAt, 'Card Criado', NULL, @ColumnID, 'Created');

-- Movimento 2: Se iniciou trabalho (saiu do Backlog)
IF @StartDate IS NOT NULL AND @ColumnID > 1
BEGIN
    INSERT INTO CardMovements (...)
    VALUES (@NewCardID, @UserID, @StartDate, 'Trabalho Iniciado', 1, @ColumnID, 'ColumnChange');
END

-- Movimento 3: Se foi concluído ← NOVO!
IF @CompletedDate IS NOT NULL
BEGIN
    SELECT @CompletedColumnID = ColumnID 
    FROM CardColumns
    WHERE CompanyID = @CompanyID 
      AND (ColumnName LIKE '%Conclu%' OR ColumnName LIKE '%Done%');
    
    INSERT INTO CardMovements (...)
    VALUES (@NewCardID, @UserID, @CompletedDate, 'Card Concluído', @ColumnID, @CompletedColumnID, 'Completed');
END

-- Movimento 4: Comentário
IF @LastComment IS NOT NULL
BEGIN
    INSERT INTO CardMovements (...)
    VALUES (@NewCardID, @UserID, GETUTCDATE(), 'Comentário', @LastComment, 'Comment');
END
```

### **2. Datas Corretas:**
- **Criação:** `@StartDate` (Last Start Date do CSV) ou `GETUTCDATE()`
- **Início:** `@StartDate` (quando saiu do Backlog)
- **Conclusão:** `@CompletedDate` (Actual End Date do CSV)

### **3. Tipos de Movimento:**
- `Created` - Card criado
- `ColumnChange` - Mudou de coluna
- `Completed` - Card concluído
- `Comment` - Comentário

---

## 🚀 Como Aplicar

### **Passo 1: Executar SP Atualizada**
```bash
sqlcmd -S 192.168.11.84 -U sa -P Jvc@1702 -d pro_team_care \
  -i Database/067_Create_SP_UpsertCardFromImport.sql
```

**OU via Azure Data Studio:**
1. Abrir `Database/067_Create_SP_UpsertCardFromImport.sql`
2. Executar script completo
3. Verificar mensagem de sucesso

### **Passo 2: Limpar Cards Antigos**
```sql
-- Deletar cards importados sem movimentos completos
DELETE FROM core.CardMovements WHERE CardID IN (
    SELECT CardID FROM core.Cards WHERE ExternalCardID IS NOT NULL
);
DELETE FROM core.Cards WHERE ExternalCardID IS NOT NULL;
```

### **Passo 3: Reimportar XLSX**
1. Acessar: `http://192.168.11.83:3000/admin/kanban`
2. Clicar "Importar BM"
3. Selecionar: `dasa-20251105161442-BPX.xlsx`
4. Clicar "Importar"

### **Passo 4: Verificar Movimentos**
```sql
-- Ver movimentos de um card importado
SELECT 
    cm.MovementID,
    cm.LogDate,
    cm.Subject,
    cm.MovementType,
    old_col.ColumnName AS OldColumn,
    new_col.ColumnName AS NewColumn
FROM core.CardMovements cm
LEFT JOIN core.CardColumns old_col ON cm.OldColumnID = old_col.ColumnID
LEFT JOIN core.CardColumns new_col ON cm.NewColumnID = new_col.ColumnID
WHERE cm.CardID = (
    SELECT TOP 1 CardID FROM core.Cards 
    WHERE ExternalCardID IS NOT NULL 
    ORDER BY CardID DESC
)
ORDER BY cm.LogDate;
```

**Resultado esperado:**
```
MovementID  LogDate              Subject                    MovementType   OldColumn  NewColumn
1           2025-10-01 10:00:00  Card Criado (Importado)    Created        NULL       Backlog
2           2025-10-05 14:30:00  Trabalho Iniciado          ColumnChange   Backlog    Em Andamento
3           2025-10-20 16:45:00  Card Concluído (Importado) Completed      Em Andamento  Concluído
4           2025-11-05 18:00:00  Comentário da Importação   Comment        NULL       NULL
```

---

## 📊 Resultado Esperado

### **Antes (ERRADO):**
```
📊 Analytics do Kanban
0 Cards Concluídos
N/A Lead Time Médio
3 Em Andamento
0.0% SLA Compliance
```

### **Depois (CORRETO):**
```
📊 Analytics do Kanban
49 Cards Concluídos ✅
15.5 dias Lead Time Médio ✅
25 Em Andamento ✅
87.5% SLA Compliance ✅

Tempo Médio por Estágio:
Backlog: 2.5 dias
Em Andamento: 8.3 dias
Em Revisão: 3.2 dias
Concluído: 1.5 dias

Histórico de Conclusões:
[Gráfico com barras por dia]
```

---

## 🔍 Validação

### **1. Verificar Cards Concluídos:**
```sql
-- Contar cards concluídos no período
SELECT COUNT(DISTINCT c.CardID) AS CardsCompleted
FROM core.Cards c
INNER JOIN core.CardMovements cm ON c.CardID = cm.CardID
WHERE c.ExternalCardID IS NOT NULL
  AND cm.MovementType = 'Completed'
  AND CAST(cm.LogDate AS DATE) BETWEEN '2025-10-01' AND '2025-11-30';
```

### **2. Verificar Lead Time:**
```sql
-- Calcular Lead Time médio
SELECT 
    AVG(DATEDIFF(SECOND, c.CreatedAt, cm.LogDate)) / 86400.0 AS LeadTimeDays
FROM core.Cards c
INNER JOIN core.CardMovements cm ON c.CardID = cm.CardID
WHERE c.ExternalCardID IS NOT NULL
  AND cm.MovementType = 'Completed'
  AND CAST(cm.LogDate AS DATE) BETWEEN '2025-10-01' AND '2025-11-30';
```

### **3. Testar Analytics Endpoint:**
```bash
curl -X GET "http://192.168.11.83:8000/api/v1/kanban/analytics?start_date=2025-10-01&end_date=2025-11-30" \
  -H "Authorization: Bearer SEU_TOKEN"
```

**Resposta esperada:**
```json
{
  "summary": {
    "leadTimeAvgSeconds": 1339200,
    "cycleTimeAvgSeconds": 716800,
    "throughput": 49,
    "wip": 25,
    "slaCompliance": 0.875
  },
  "timePerStage": [
    {"columnName": "Backlog", "avgSeconds": 216000},
    {"columnName": "Em Andamento", "avgSeconds": 716800},
    {"columnName": "Em Revisão", "avgSeconds": 276480}
  ],
  "throughputHistory": [
    {"date": "2025-10-20", "count": 5},
    {"date": "2025-10-21", "count": 8},
    {"date": "2025-10-22", "count": 12}
  ]
}
```

---

## ⚠️ Notas Importantes

### **1. Coluna "Concluído":**
A SP busca a coluna de conclusão com:
```sql
WHERE ColumnName LIKE '%Conclu%' OR ColumnName LIKE '%Done%'
```

**Se sua coluna tiver nome diferente:**
```sql
-- Verificar nome exato
SELECT ColumnID, ColumnName FROM core.CardColumns WHERE CompanyID = 1;

-- Ajustar se necessário
UPDATE core.CardColumns 
SET ColumnName = 'Concluído'
WHERE ColumnID = 5 AND CompanyID = 1;
```

### **2. Datas do CSV:**
- **Column Name** (coluna 7) → Define `@ColumnID`
- **Last Start Date** (coluna 14) → Define `@StartDate`
- **Actual End Date** (coluna 12) → Define `@CompletedDate`

### **3. Cards Sem Data de Conclusão:**
Cards em andamento **não terão** movimento de conclusão:
```
Backlog → Em Andamento (sem conclusão)
```

Isso é **correto**! Analytics só conta como concluído se tiver `@CompletedDate`.

---

## 📁 Arquivos Modificados

```
✅ Database/067_Create_SP_UpsertCardFromImport.sql
   - Movimento de criação
   - Movimento de início (se saiu do Backlog)
   - Movimento de conclusão (se CompletedDate)
   - Movimento de comentário
   
✅ docs/CORRECAO_ANALYTICS_KANBAN.md (NOVO)
```

---

## 🎯 Checklist

- [ ] Executar SP atualizada
- [ ] Limpar cards antigos
- [ ] Reimportar XLSX
- [ ] Verificar movimentos criados
- [ ] Testar analytics endpoint
- [ ] Validar métricas no frontend

---

**Após executar a SP atualizada e reimportar, os analytics funcionarão corretamente!** 🎉

**A chave é registrar movimentos completos: Criação → Início → Conclusão** 🔑
