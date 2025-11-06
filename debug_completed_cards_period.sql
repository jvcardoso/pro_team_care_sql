-- Debug: Verificar cards concluídos no período específico
-- Período: 2025-10-06 até 2025-11-05

USE [pro_team_care];
GO

DECLARE @StartDate DATE = '2025-10-06';
DECLARE @EndDate DATE = '2025-11-05';
DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'DEBUG: Cards concluídos no período 2025-10-06 até 2025-11-05';
PRINT '================================================================================';

-- 1. Verificar se há cards com CompletedDate no período
SELECT
    'Cards com CompletedDate no período' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate;

-- 2. Detalhes dos cards no período
SELECT TOP 10
    CardID,
    Title,
    ColumnID,
    CreatedAt,
    CompletedDate,
    CAST(CompletedDate AS DATE) as CompletedDateOnly
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
ORDER BY CompletedDate DESC;

-- 3. Verificar distribuição por coluna
SELECT
    c.ColumnID,
    col.ColumnName,
    COUNT(*) as Quantidade
FROM core.Cards c
INNER JOIN core.CardColumns col ON c.ColumnID = col.ColumnID
WHERE c.CompanyID = @CompanyID
  AND c.IsDeleted = 0
  AND c.CompletedDate IS NOT NULL
  AND CAST(c.CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
GROUP BY c.ColumnID, col.ColumnName
ORDER BY c.ColumnID;

-- 4. Verificar se há cards na coluna "Concluído" (ID=5) com CompletedDate no período
SELECT
    'Cards na coluna Concluído (ID=5) com CompletedDate no período' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND ColumnID = 5  -- Concluído
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate;

-- 5. Verificar período atual vs período solicitado
SELECT
    'Data atual do sistema' AS Info,
    GETDATE() AS Valor
UNION ALL
SELECT
    'Período solicitado' AS Info,
    CAST(@StartDate AS VARCHAR) + ' até ' + CAST(@EndDate AS VARCHAR) AS Valor;

PRINT '';
PRINT '================================================================================';
PRINT 'ANÁLISE:';
PRINT '- Se "Cards com CompletedDate no período" = 0, então Array(0) é CORRETO';
PRINT '- Se > 0, há problema no filtro do endpoint';
PRINT '- Verificar se os IDs das colunas estão corretos';
PRINT '================================================================================';