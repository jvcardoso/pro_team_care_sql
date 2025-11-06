-- Debug: Verificar exatamente quais cards são retornados pelo endpoint

USE [pro_team_care];
GO

DECLARE @CompanyID BIGINT = 1;
DECLARE @CompletedFrom DATE = '2025-01-01';
DECLARE @CompletedTo DATE = '2025-11-05';

PRINT '================================================================================';
PRINT 'DEBUG: Cards retornados pelo endpoint /api/v1/kanban/cards';
PRINT 'Período: 2025-01-01 até 2025-11-05';
PRINT '================================================================================';

-- 1. Query exata do endpoint (simulando o filtro)
SELECT
    'Endpoint retorna' AS Origem,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CompletedDate >= @CompletedFrom
  AND CompletedDate <= @CompletedTo
  AND ColumnID IN (1,2,3,4,5);

-- 2. Detalhes dos cards retornados
SELECT TOP 10
    CardID,
    Title,
    ColumnID,
    CompletedDate,
    'Endpoint' AS Origem
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CompletedDate >= @CompletedFrom
  AND CompletedDate <= @CompletedTo
  AND ColumnID IN (1,2,3,4,5)
ORDER BY CompletedDate DESC;

-- 3. Verificar se há cards com CompletedDate NULL
SELECT
    'Cards com CompletedDate NULL' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NULL;

-- 4. Verificar distribuição por coluna dos cards concluídos
SELECT
    cc.ColumnName,
    COUNT(*) as Quantidade
FROM core.Cards c
INNER JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
WHERE c.CompanyID = @CompanyID
  AND c.IsDeleted = 0
  AND c.CompletedDate IS NOT NULL
  AND c.CompletedDate >= @CompletedFrom
  AND c.CompletedDate <= @CompletedTo
GROUP BY cc.ColumnName, cc.ColumnID
ORDER BY cc.ColumnID;

-- 5. Verificar se há cards fora do período
SELECT
    'Cards concluídos FORA do período' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND (CompletedDate < @CompletedFrom OR CompletedDate > @CompletedTo);

-- 6. Verificar se há cards em colunas não incluídas no filtro
SELECT
    'Cards em colunas NÃO filtradas' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CompletedDate >= @CompletedFrom
  AND CompletedDate <= @CompletedTo
  AND ColumnID NOT IN (1,2,3,4,5);

PRINT '';
PRINT '================================================================================';
PRINT 'ANÁLISE:';
PRINT '- Se "Endpoint retorna" = 1, confirma o comportamento observado';
PRINT '- Verificar se os cards estão nas colunas corretas';
PRINT '- Verificar se as datas estão no formato correto';
PRINT '================================================================================';