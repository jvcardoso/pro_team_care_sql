# 🗄️ Scripts SQL - Classificação ITIL

**Versão:** 1.0  
**Data:** 06/11/2025  
**Ordem de Execução:** 069 → 070 → 071

---

## 📄 Script 069: Adicionar Colunas ITIL

**Arquivo:** `Database/069_Add_ITIL_Classification_Columns.sql`

```sql
USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Adicionando colunas para classificação ITIL em core.Cards';
PRINT '================================================================================';

-- ITILCategory
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'ITILCategory')
BEGIN
    ALTER TABLE core.Cards ADD ITILCategory VARCHAR(30) NULL;
    PRINT '✅ Coluna ITILCategory adicionada';
END
ELSE
    PRINT '⚠️  Coluna ITILCategory já existe';

-- HasWindow
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'HasWindow')
BEGIN
    ALTER TABLE core.Cards ADD HasWindow BIT DEFAULT 0;
    PRINT '✅ Coluna HasWindow adicionada';
END
ELSE
    PRINT '⚠️  Coluna HasWindow já existe';

-- HasCAB
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'HasCAB')
BEGIN
    ALTER TABLE core.Cards ADD HasCAB BIT DEFAULT 0;
    PRINT '✅ Coluna HasCAB adicionada';
END
ELSE
    PRINT '⚠️  Coluna HasCAB já existe';

-- HasBackout
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'HasBackout')
BEGIN
    ALTER TABLE core.Cards ADD HasBackout BIT DEFAULT 0;
    PRINT '✅ Coluna HasBackout adicionada';
END
ELSE
    PRINT '⚠️  Coluna HasBackout já existe';

-- Size
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'Size')
BEGIN
    ALTER TABLE core.Cards ADD Size VARCHAR(20) NULL;
    PRINT '✅ Coluna Size adicionada';
END
ELSE
    PRINT '⚠️  Coluna Size já existe';

-- RiskLevel
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'RiskLevel')
BEGIN
    ALTER TABLE core.Cards ADD RiskLevel VARCHAR(20) NULL;
    PRINT '✅ Coluna RiskLevel adicionada';
END
ELSE
    PRINT '⚠️  Coluna RiskLevel já existe';

PRINT '================================================================================';
PRINT 'Colunas ITIL criadas com sucesso!';
PRINT '================================================================================';
GO
```

---

## 📄 Script 070: Criar View de Relatório

**Arquivo:** `Database/070_Create_View_ITILReport.sql`

```sql
USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Criando view analytics.vw_ITILReport';
PRINT '================================================================================';

-- Criar schema analytics se não existir
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'analytics')
BEGIN
    EXEC('CREATE SCHEMA analytics');
    PRINT '✅ Schema analytics criado';
END

-- Dropar view se existir
IF OBJECT_ID('analytics.vw_ITILReport', 'V') IS NOT NULL
    DROP VIEW analytics.vw_ITILReport;
GO

CREATE VIEW analytics.vw_ITILReport AS
SELECT 
    c.CardID,
    c.CompanyID,
    c.ExternalCardID,
    c.Title,
    c.Description,
    c.OriginalText,
    cc.ColumnName,
    c.ITILCategory,
    c.Priority,
    c.Size,
    c.RiskLevel,
    c.HasWindow,
    c.HasCAB,
    c.HasBackout,
    c.StartDate,
    c.CompletedDate,
    c.DueDate,
    c.CreatedAt,
    u.email_address AS OwnerEmail,
    u.id AS OwnerUserID,
    
    -- Métricas de tempo
    DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) AS LeadTimeSeconds,
    DATEDIFF(SECOND, c.StartDate, c.CompletedDate) AS CycleTimeSeconds,
    
    -- SLA Compliance
    CASE 
        WHEN c.CompletedDate IS NOT NULL AND c.DueDate IS NOT NULL 
            THEN CASE WHEN c.CompletedDate <= c.DueDate THEN 1 ELSE 0 END 
        ELSE NULL 
    END AS MetSLA,
    
    -- Dias de atraso
    CASE 
        WHEN c.CompletedDate > c.DueDate 
            THEN DATEDIFF(DAY, c.DueDate, c.CompletedDate)
        ELSE 0
    END AS DaysLate,
    
    -- Status
    CASE 
        WHEN c.CompletedDate IS NOT NULL THEN 'Concluído'
        WHEN c.StartDate IS NOT NULL THEN 'Em Andamento'
        ELSE 'Não Iniciado'
    END AS Status

FROM core.Cards c
JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
LEFT JOIN core.Users u ON c.UserID = u.id
WHERE c.IsDeleted = 0;
GO

PRINT '✅ View analytics.vw_ITILReport criada com sucesso!';
PRINT '================================================================================';
GO
```

---

## 📄 Script 071: Atualizar SP de Importação

**Arquivo:** `Database/071_Update_SP_UpsertCardFromImport_ITIL.sql`

**Nota:** Este script é muito extenso. Veja o arquivo completo em `Database/067_Create_SP_UpsertCardFromImport.sql` e adicione as seguintes modificações:

### **Modificações Necessárias:**

1. **Adicionar parâmetro `@LastComment`:**
```sql
@LastComment NVARCHAR(MAX),
```

2. **Adicionar parâmetro `@Size`:**
```sql
@Size NVARCHAR(20) = NULL,
```

3. **Adicionar lógica de classificação ITIL após linha 30:**
```sql
-- CLASSIFICAÇÃO ITIL
DECLARE @TextBlob NVARCHAR(MAX) = CONCAT(
    ISNULL(@Title, ''), ' ',
    ISNULL(@Description, ''), ' ',
    ISNULL(@LastComment, '')
);

DECLARE @ITILCategory VARCHAR(30) = 
    CASE 
        WHEN @TextBlob LIKE '%GMUD%' OR @TextBlob LIKE '%RDM%' 
            OR @TextBlob LIKE '%CHG%' OR @TextBlob LIKE '%Deploy%' 
            OR @TextBlob LIKE '%Janela%' OR @TextBlob LIKE '%CAB%'
            THEN 'Change'
        WHEN @TextBlob LIKE '%Falha%' OR @TextBlob LIKE '%Erro%' 
            OR @TextBlob LIKE '%Incidente%' OR @TextBlob LIKE '%Indisponibilidade%'
            THEN 'Incident'
        WHEN @TextBlob LIKE '%Solicitar%' OR @TextBlob LIKE '%Criar grupo%' 
            OR @TextBlob LIKE '%Permiss%' OR @TextBlob LIKE '%Acesso%'
            THEN 'Service Request'
        ELSE 'Operation Task'
    END;

DECLARE @HasWindow BIT = 
    CASE WHEN @TextBlob LIKE '%Janela%' OR @TextBlob LIKE '%window%' 
        THEN 1 ELSE 0 END;

DECLARE @HasCAB BIT = 
    CASE WHEN @TextBlob LIKE '%CAB%' OR @TextBlob LIKE '%Comitê%' 
        THEN 1 ELSE 0 END;

DECLARE @HasBackout BIT = 
    CASE WHEN @TextBlob LIKE '%backout%' OR @TextBlob LIKE '%rollback%' 
        THEN 1 ELSE 0 END;

DECLARE @PriorityNorm VARCHAR(10) = 
    CASE LOWER(ISNULL(@Priority, ''))
        WHEN 'high' THEN 'High'
        WHEN 'average' THEN 'Medium'
        WHEN 'low' THEN 'Low'
        ELSE 'Medium'
    END;

DECLARE @RiskLevel VARCHAR(20) = 
    CASE 
        WHEN @ITILCategory = 'Change' AND @HasCAB = 1 AND @HasBackout = 1 
            THEN 'Low'
        WHEN @ITILCategory = 'Change' AND (@HasCAB = 0 OR @HasBackout = 0) 
            THEN 'High'
        WHEN @ITILCategory = 'Incident' 
            THEN 'High'
        ELSE 'Low'
    END;
```

4. **Modificar UPDATE (linha ~80):**
```sql
UPDATE [core].[Cards]
SET Title = @Title,
    Description = @Description,
    OriginalText = @TextBlob,  -- MODIFICADO
    Priority = @PriorityNorm,  -- MODIFICADO
    ColumnID = @ColumnID,
    DueDate = @Deadline,
    CompletedDate = ISNULL(@CompletedDate, CompletedDate),
    StartDate = ISNULL(@StartDate, StartDate),
    ITILCategory = @ITILCategory,  -- NOVO
    HasWindow = @HasWindow,  -- NOVO
    HasCAB = @HasCAB,  -- NOVO
    HasBackout = @HasBackout,  -- NOVO
    Size = @Size,  -- NOVO
    RiskLevel = @RiskLevel,  -- NOVO
    UpdatedAt = GETUTCDATE()
WHERE CardID = @CardID;
```

5. **Modificar INSERT (linha ~100):**
```sql
INSERT INTO [core].[Cards] (
    CompanyID, UserID, ColumnID, Title, Description, OriginalText,
    Priority, DueDate, StartDate, CompletedDate, ExternalCardID,
    ITILCategory, HasWindow, HasCAB, HasBackout, Size, RiskLevel,
    IsDeleted, CreatedAt, DisplayOrder
)
VALUES (
    @CompanyID, @UserID, @ColumnID, @Title, @Description, @TextBlob,
    @PriorityNorm, @Deadline, @StartDate, @CompletedDate, @ExternalCardID,
    @ITILCategory, @HasWindow, @HasCAB, @HasBackout, @Size, @RiskLevel,
    0, ISNULL(@StartDate, GETUTCDATE()), 0
);
```

---

## ✅ Checklist de Execução

- [ ] Backup do banco antes de executar
- [ ] Executar Script 069 (colunas)
- [ ] Verificar colunas criadas: `SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name LIKE '%ITIL%'`
- [ ] Executar Script 070 (view)
- [ ] Testar view: `SELECT TOP 10 * FROM analytics.vw_ITILReport`
- [ ] Executar Script 071 (SP)
- [ ] Testar SP com card de teste
- [ ] Reimportar planilha Businessmap
- [ ] Verificar classificação: `SELECT ITILCategory, COUNT(*) FROM core.Cards GROUP BY ITILCategory`

---

## 🧪 Testes de Validação

### **1. Verificar Colunas**
```sql
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('core.Cards')
AND c.name IN ('ITILCategory', 'HasWindow', 'HasCAB', 'HasBackout', 'Size', 'RiskLevel');
```

### **2. Testar View**
```sql
SELECT 
    ITILCategory,
    COUNT(*) AS Total,
    AVG(CycleTimeSeconds) AS AvgCycle,
    SUM(MetSLA) * 100.0 / COUNT(*) AS SLAPercent
FROM analytics.vw_ITILReport
WHERE CompletedDate >= '2025-01-01'
GROUP BY ITILCategory;
```

### **3. Testar Classificação**
```sql
-- Verificar distribuição por categoria
SELECT 
    ITILCategory,
    COUNT(*) AS Total,
    SUM(CASE WHEN HasWindow = 1 THEN 1 ELSE 0 END) AS ComJanela,
    SUM(CASE WHEN HasCAB = 1 THEN 1 ELSE 0 END) AS ComCAB,
    SUM(CASE WHEN RiskLevel = 'High' THEN 1 ELSE 0 END) AS AltoRisco
FROM core.Cards
WHERE IsDeleted = 0
GROUP BY ITILCategory;
```

---

## 📝 Notas Importantes

1. **Backup:** Sempre fazer backup antes de executar scripts DDL
2. **Ordem:** Executar na ordem 069 → 070 → 071
3. **Validação:** Testar cada script antes de prosseguir
4. **Rollback:** Se algo falhar, restaurar backup
5. **Performance:** View não impacta performance (sem índices necessários)

---

**Documentos Relacionados:**
- `docs/CLASSIFICACAO_ITIL_KANBAN.md` - Documentação principal
- `Database/067_Create_SP_UpsertCardFromImport.sql` - SP original
