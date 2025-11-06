-- Verificar dados dos cards para entender por que Lead Time é N/A

USE [pro_team_care];
GO

DECLARE @StartDate DATE = '2025-11-01';
DECLARE @EndDate DATE = '2025-11-30';
DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'VERIFICAÇÃO: Dados dos Cards para Analytics';
PRINT 'Período: ' + CAST(@StartDate AS VARCHAR) + ' até ' + CAST(@EndDate AS VARCHAR);
PRINT '================================================================================';

-- 1. Total de cards da empresa
SELECT
    'Total de cards da empresa' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0;

-- 2. Cards concluídos (qualquer período)
SELECT
    'Cards concluídos (todos)' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND CompletedDate IS NOT NULL;

-- 3. Cards concluídos no período especificado
SELECT
    'Cards concluídos no período' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate;

-- 4. Cards em andamento
SELECT
    'Cards em andamento' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NULL;

-- 5. Detalhes dos cards concluídos no período
SELECT TOP 5
    CardID,
    Title,
    CreatedAt,
    CompletedDate,
    DATEDIFF(DAY, CreatedAt, CompletedDate) as DiasLeadTime
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
ORDER BY CompletedDate DESC;

-- 6. Verificar se há movimentos de conclusão no período
SELECT
    'Movimentos de conclusão no período' AS Tipo,
    COUNT(*) AS Quantidade
FROM [analytics].[vw_CardFullHistory]
WHERE CompanyID = @CompanyID
  AND NewColumnName = 'Concluído'
  AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate;

-- 7. Verificar período atual vs período do dashboard
SELECT
    'Data atual do sistema' AS Tipo,
    GETDATE() AS Data
UNION ALL
SELECT
    'Período do dashboard' AS Tipo,
    CAST(@StartDate AS VARCHAR) + ' até ' + CAST(@EndDate AS VARCHAR) AS Data;

PRINT '';
PRINT '================================================================================';
PRINT 'DIAGNÓSTICO:';
PRINT '- Se "Cards concluídos no período" = 0, então N/A é CORRETO';
PRINT '- Se > 0, há problema na SP ou no frontend';
PRINT '- Verifique se o período do dashboard corresponde aos dados';
PRINT '================================================================================';