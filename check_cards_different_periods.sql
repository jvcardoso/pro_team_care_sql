-- Verificar cards concluídos em diferentes períodos

USE [pro_team_care];
GO

DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'VERIFICAÇÃO: Cards concluídos em diferentes períodos';
PRINT '================================================================================';

-- 1. Últimos 30 dias (período atual do frontend)
DECLARE @Last30Days_Start DATE = DATEADD(DAY, -30, CAST(GETDATE() AS DATE));
DECLARE @Last30Days_End DATE = CAST(GETDATE() AS DATE);

SELECT
    'Últimos 30 dias' AS Periodo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @Last30Days_Start AND @Last30Days_End;

-- 2. Últimos 90 dias
DECLARE @Last90Days_Start DATE = DATEADD(DAY, -90, CAST(GETDATE() AS DATE));
DECLARE @Last90Days_End DATE = CAST(GETDATE() AS DATE);

SELECT
    'Últimos 90 dias' AS Periodo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @Last90Days_Start AND @Last90Days_End;

-- 3. Últimos 365 dias
DECLARE @Last365Days_Start DATE = DATEADD(DAY, -365, CAST(GETDATE() AS DATE));
DECLARE @Last365Days_End DATE = CAST(GETDATE() AS DATE);

SELECT
    'Últimos 365 dias' AS Periodo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @Last365Days_Start AND @Last365Days_End;

-- 4. Todos os cards concluídos (sempre)
SELECT
    'Todos os tempos' AS Periodo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL;

-- 5. Detalhes dos cards concluídos recentemente (TOP 5)
SELECT TOP 5
    CardID,
    Title,
    ColumnID,
    CreatedAt,
    CompletedDate,
    DATEDIFF(DAY, CreatedAt, CompletedDate) as DiasParaConcluir
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
ORDER BY CompletedDate DESC;

-- 6. Verificar período exato do frontend
SELECT
    'Período exato do frontend (2025-10-06 até 2025-11-05)' AS Periodo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) >= '2025-10-06'
  AND CAST(CompletedDate AS DATE) <= '2025-11-05';

PRINT '';
PRINT '================================================================================';
PRINT 'CONCLUSÃO:';
PRINT '- Se "Últimos 30 dias" = 0, o frontend está correto em mostrar Array(0)';
PRINT '- Se outros períodos têm dados, o problema é o filtro de período';
PRINT '- Verificar se o frontend está usando o período correto';
PRINT '================================================================================';