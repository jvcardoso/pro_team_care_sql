-- Debug dos dados do Analytics
-- Verificar quantos cards estão sendo considerados nos cálculos

USE [pro_team_care];
GO

DECLARE @StartDate DATE = '2025-11-01';
DECLARE @EndDate DATE = '2025-11-30';
DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'DEBUG: Dados do Analytics Kanban';
PRINT 'Período: ' + CAST(@StartDate AS VARCHAR) + ' até ' + CAST(@EndDate AS VARCHAR);
PRINT '================================================================================';

-- 1. Cards concluídos no período (usando a lógica da SP)
SELECT
    'Cards concluídos no período' AS Tipo,
    COUNT(*) AS Quantidade
FROM (
    SELECT DISTINCT CardID
    FROM [analytics].[vw_CardFullHistory]
    WHERE CompanyID = @CompanyID
      AND NewColumnName = 'Concluído'
      AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate
) AS ConcluidosPeriodo;

-- 2. Cards em andamento
SELECT
    'Cards em andamento (WIP)' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NULL
  AND ColumnID NOT IN (
      SELECT ColumnID FROM core.CardColumns
      WHERE CompanyID = @CompanyID AND ColumnName IN ('Backlog', 'Concluído')
  );

-- 3. Verificar se há cards na CTE CardTimings (após filtro)
WITH AllMovements AS (
    SELECT *
    FROM [analytics].[vw_CardFullHistory]
    WHERE CompanyID = @CompanyID
),
RelevantCards AS (
    SELECT DISTINCT CardID
    FROM AllMovements
    WHERE
        (NewColumnName = 'Concluído' AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate)
        OR
        (CardID IN (
            SELECT CardID FROM core.Cards
            WHERE CompanyID = @CompanyID
              AND IsDeleted = 0
              AND CompletedDate IS NULL
        ))
),
RelevantMovements AS (
    SELECT am.*
    FROM AllMovements am
    INNER JOIN RelevantCards rc ON am.CardID = rc.CardID
),
CardTimings AS (
    SELECT
        CardID,
        MIN(CardCreatedAt) AS CreatedAt,
        MIN(CASE WHEN NewColumnName != 'Backlog' AND OldColumnName = 'Backlog' THEN MovementDate ELSE NULL END) AS StartDate,
        MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS ActualCompletedDate,
        MAX(DueDate) as DueDate
    FROM RelevantMovements
    GROUP BY CardID
    HAVING MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) >= MIN(CardCreatedAt)
)
SELECT
    'Cards na CTE CardTimings (após filtro)' AS Tipo,
    COUNT(*) AS Quantidade
FROM CardTimings;

-- 4. Verificar cards excluídos pelo filtro HAVING
WITH AllMovements AS (
    SELECT *
    FROM [analytics].[vw_CardFullHistory]
    WHERE CompanyID = @CompanyID
),
RelevantCards AS (
    SELECT DISTINCT CardID
    FROM AllMovements
    WHERE
        (NewColumnName = 'Concluído' AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate)
        OR
        (CardID IN (
            SELECT CardID FROM core.Cards
            WHERE CompanyID = @CompanyID
              AND IsDeleted = 0
              AND CompletedDate IS NULL
        ))
),
RelevantMovements AS (
    SELECT am.*
    FROM AllMovements am
    INNER JOIN RelevantCards rc ON am.CardID = rc.CardID
),
CardTimingsAll AS (
    SELECT
        CardID,
        MIN(CardCreatedAt) AS CreatedAt,
        MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS ActualCompletedDate
    FROM RelevantMovements
    GROUP BY CardID
)
SELECT
    'Cards excluídos pelo filtro (CompletedDate < CreatedAt)' AS Tipo,
    COUNT(*) AS Quantidade
FROM CardTimingsAll
WHERE ActualCompletedDate < CreatedAt;

-- 5. Cards válidos para cálculo de Lead Time
WITH AllMovements AS (
    SELECT *
    FROM [analytics].[vw_CardFullHistory]
    WHERE CompanyID = @CompanyID
),
RelevantCards AS (
    SELECT DISTINCT CardID
    FROM AllMovements
    WHERE
        (NewColumnName = 'Concluído' AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate)
        OR
        (CardID IN (
            SELECT CardID FROM core.Cards
            WHERE CompanyID = @CompanyID
              AND IsDeleted = 0
              AND CompletedDate IS NULL
        ))
),
RelevantMovements AS (
    SELECT am.*
    FROM AllMovements am
    INNER JOIN RelevantCards rc ON am.CardID = rc.CardID
),
CardTimings AS (
    SELECT
        CardID,
        MIN(CardCreatedAt) AS CreatedAt,
        MIN(CASE WHEN NewColumnName != 'Backlog' AND OldColumnName = 'Backlog' THEN MovementDate ELSE NULL END) AS StartDate,
        MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS ActualCompletedDate,
        MAX(DueDate) as DueDate
    FROM RelevantMovements
    GROUP BY CardID
    HAVING MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) >= MIN(CardCreatedAt)
)
SELECT
    'Cards válidos para Lead Time (concluídos no período)' AS Tipo,
    COUNT(*) AS Quantidade
FROM CardTimings
WHERE ActualCompletedDate IS NOT NULL
  AND CAST(ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate;

-- 6. Detalhes dos cards válidos
WITH AllMovements AS (
    SELECT *
    FROM [analytics].[vw_CardFullHistory]
    WHERE CompanyID = @CompanyID
),
RelevantCards AS (
    SELECT DISTINCT CardID
    FROM AllMovements
    WHERE
        (NewColumnName = 'Concluído' AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate)
        OR
        (CardID IN (
            SELECT CardID FROM core.Cards
            WHERE CompanyID = @CompanyID
              AND IsDeleted = 0
              AND CompletedDate IS NULL
        ))
),
RelevantMovements AS (
    SELECT am.*
    FROM AllMovements am
    INNER JOIN RelevantCards rc ON am.CardID = rc.CardID
),
CardTimings AS (
    SELECT
        CardID,
        MIN(CardCreatedAt) AS CreatedAt,
        MIN(CASE WHEN NewColumnName != 'Backlog' AND OldColumnName = 'Backlog' THEN MovementDate ELSE NULL END) AS StartDate,
        MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS ActualCompletedDate,
        MAX(DueDate) as DueDate
    FROM RelevantMovements
    GROUP BY CardID
    HAVING MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) >= MIN(CardCreatedAt)
)
SELECT TOP 5
    ct.CardID,
    c.Title,
    ct.CreatedAt,
    ct.ActualCompletedDate,
    DATEDIFF(SECOND, ct.CreatedAt, ct.ActualCompletedDate) as LeadTimeSeconds,
    DATEDIFF(MINUTE, ct.CreatedAt, ct.ActualCompletedDate) as LeadTimeMinutes
FROM CardTimings ct
INNER JOIN core.Cards c ON ct.CardID = c.CardID
WHERE ct.ActualCompletedDate IS NOT NULL
  AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
ORDER BY ct.ActualCompletedDate DESC;

PRINT '';
PRINT '================================================================================';
PRINT 'RESUMO:';
PRINT '- Se "Cards válidos para Lead Time" = 0, então N/A é correto';
PRINT '- Se > 0, deve haver média calculada';
PRINT '- Verifique se o período tem cards concluídos';
PRINT '================================================================================';