# 🔧 Correção - Cards nas Colunas Corretas

## 🎯 Problema Identificado

**Cards importados ficam todos em "Backlog"** ao invés de irem para suas colunas corretas.

### **Causa:**
A SP `sp_UpsertCardFromImport` estava fixando `@ColumnID = 1` (Backlog) e **ignorando** o parâmetro `@ColumnName`.

---

## ✅ Correção Implementada

### **1. Mapeamento de Coluna (NOVO):**
```sql
-- 2. MAPEAR NOME DA COLUNA PARA ColumnID
IF @ColumnName IS NOT NULL AND LTRIM(RTRIM(@ColumnName)) <> ''
BEGIN
    SELECT @ColumnID = ColumnID 
    FROM [core].[CardColumns]
    WHERE CompanyID = @CompanyID 
      AND ColumnName = @ColumnName
      AND IsActive = 1;
    
    -- Se não encontrar, manter Backlog como padrão
    IF @ColumnID IS NULL
        SET @ColumnID = 1;
END
```

### **2. UPDATE Também Move Card:**
```sql
UPDATE [core].[Cards]
SET Title = @Title,
    Description = @Description,
    Priority = @Priority,
    ColumnID = @ColumnID,  -- ← NOVO: atualiza coluna também
    DueDate = @Deadline,
    CompletedDate = @CompletedDate,
    StartDate = @StartDate
WHERE CardID = @CardID;
```

### **3. Parâmetros OUTPUT:**
```sql
CREATE PROCEDURE [core].[sp_UpsertCardFromImport]
    ...
    @NewCardID INT OUTPUT,
    @ActionTaken NVARCHAR(10) OUTPUT
AS
```

---

## 🚀 Como Aplicar

### **Passo 1: Executar SP Atualizada**
```bash
# Conectar ao SQL Server
sqlcmd -S 192.168.11.84 -U sa -P Jvc@1702 -d pro_team_care -i Database/067_Create_SP_UpsertCardFromImport.sql
```

**OU via Azure Data Studio / SSMS:**
1. Abrir `Database/067_Create_SP_UpsertCardFromImport.sql`
2. Executar script completo
3. Verificar mensagem: `✅ SUCESSO: Stored Procedure [core].[sp_UpsertCardFromImport] criada.`

### **Passo 2: Limpar Cards Antigos (Opcional)**
```sql
-- Ver cards importados
SELECT CardID, ExternalCardID, Title, ColumnID 
FROM core.Cards 
WHERE ExternalCardID IS NOT NULL;

-- Deletar cards de teste (se necessário)
DELETE FROM core.CardMovements WHERE CardID IN (
    SELECT CardID FROM core.Cards WHERE ExternalCardID IS NOT NULL
);
DELETE FROM core.Cards WHERE ExternalCardID IS NOT NULL;
```

### **Passo 3: Verificar Colunas Existentes**
```sql
-- Listar colunas da empresa
SELECT ColumnID, ColumnName, DisplayOrder, IsActive
FROM core.CardColumns
WHERE CompanyID = 1
ORDER BY DisplayOrder;
```

**Resultado esperado:**
```
ColumnID  ColumnName        DisplayOrder  IsActive
1         Backlog           1             1
2         Em Andamento      2             1
3         Em Revisão        3             1
4         Concluído         4             1
5         Cancelado         5             1
```

### **Passo 4: Reimportar XLSX**
1. Acessar: `http://192.168.11.83:3000/admin/kanban`
2. Clicar "Importar BM"
3. Selecionar: `dasa-20251105161442-BPX.xlsx`
4. Clicar "Importar"

---

## 📊 Resultado Esperado

### **Antes (ERRADO):**
```
Backlog: 99 cards ❌
Em Andamento: 0 cards
Em Revisão: 0 cards
Concluído: 0 cards
```

### **Depois (CORRETO):**
```
Backlog: 10 cards ✅
Em Andamento: 25 cards ✅
Em Revisão: 15 cards ✅
Concluído: 49 cards ✅
```

---

## 🔍 Validação

### **1. Verificar Distribuição:**
```sql
-- Contar cards por coluna
SELECT 
    cc.ColumnName,
    COUNT(c.CardID) as TotalCards
FROM core.CardColumns cc
LEFT JOIN core.Cards c ON c.ColumnID = cc.ColumnID 
    AND c.ExternalCardID IS NOT NULL
    AND c.IsDeleted = 0
WHERE cc.CompanyID = 1
GROUP BY cc.ColumnName, cc.DisplayOrder
ORDER BY cc.DisplayOrder;
```

### **2. Ver Exemplos de Cada Coluna:**
```sql
-- Ver 3 cards de cada coluna
SELECT TOP 3
    c.ExternalCardID,
    c.Title,
    cc.ColumnName
FROM core.Cards c
JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
WHERE c.ExternalCardID IS NOT NULL
  AND cc.ColumnName = 'Em Andamento'
ORDER BY c.CreatedAt DESC;
```

### **3. Verificar Mapeamento:**
```sql
-- Ver se nomes do CSV batem com nomes das colunas
SELECT DISTINCT 
    c.ColumnID,
    cc.ColumnName
FROM core.Cards c
JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
WHERE c.ExternalCardID IS NOT NULL
ORDER BY c.ColumnID;
```

---

## ⚠️ Possíveis Problemas

### **Problema 1: Nomes não batem**

**Sintoma:** Cards continuam indo para Backlog

**Causa:** Nome da coluna no CSV diferente do nome no banco

**Solução:**
```sql
-- Ver nomes exatos no CSV (coluna 7)
-- Exemplo: "Em Andamento" vs "Em andamento"

-- Opção A: Ajustar nomes no banco
UPDATE core.CardColumns 
SET ColumnName = 'Em Andamento'  -- Nome exato do CSV
WHERE ColumnID = 2;

-- Opção B: Fazer mapeamento case-insensitive na SP
SELECT @ColumnID = ColumnID 
FROM [core].[CardColumns]
WHERE CompanyID = @CompanyID 
  AND UPPER(ColumnName) = UPPER(@ColumnName)  -- ← Case insensitive
  AND IsActive = 1;
```

### **Problema 2: Coluna não existe**

**Sintoma:** Cards vão para Backlog mesmo com nome correto

**Causa:** Coluna não cadastrada no banco

**Solução:**
```sql
-- Criar coluna faltante
INSERT INTO core.CardColumns (CompanyID, ColumnName, DisplayOrder, Color, IsActive, CreatedAt)
VALUES (1, 'Nome da Coluna', 6, '#808080', 1, GETUTCDATE());
```

---

## 📁 Arquivos Modificados

```
✅ Database/067_Create_SP_UpsertCardFromImport.sql
   - Mapeamento ColumnName → ColumnID
   - UPDATE também move card
   - Parâmetros OUTPUT
   
✅ docs/CORRECAO_COLUNAS_KANBAN.md (NOVO)
```

---

## 🎯 Checklist

- [ ] Executar SP atualizada no banco
- [ ] Verificar colunas existentes
- [ ] Limpar cards de teste (opcional)
- [ ] Reimportar XLSX
- [ ] Validar distribuição por coluna
- [ ] Verificar cards em cada coluna

---

**Após executar a SP atualizada, os cards serão importados para as colunas corretas!** 🎉
