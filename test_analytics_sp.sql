-- Teste direto da Stored Procedure para verificar o cálculo

USE [pro_team_care];
GO

-- Teste com o período que está sendo usado no frontend
DECLARE @StartDate DATE = '2025-11-01';
DECLARE @EndDate DATE = '2025-11-05';
DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'TESTE DIRETO: Stored Procedure sp_GetKanbanDashboard';
PRINT 'Período: ' + CAST(@StartDate AS VARCHAR) + ' até ' + CAST(@EndDate AS VARCHAR);
PRINT '================================================================================';

-- Executar a SP diretamente
EXEC [reports].[sp_GetKanbanDashboard]
    @StartDate = @StartDate,
    @EndDate = @EndDate,
    @CompanyID = @CompanyID;

-- Verificar dados brutos para debug
PRINT '';
PRINT '================================================================================';
PRINT 'DEBUG: Dados brutos dos cards no período';
PRINT '================================================================================';

SELECT TOP 5
    c.CardID,
    c.Title,
    c.CreatedAt,
    c.CompletedDate,
    DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) as LeadTimeSeconds,
    DATEDIFF(MINUTE, c.CreatedAt, c.CompletedDate) as LeadTimeMinutes
FROM core.Cards c
WHERE c.CompanyID = @CompanyID
  AND c.IsDeleted = 0
  AND c.CompletedDate IS NOT NULL
  AND CAST(c.CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
ORDER BY c.CompletedDate DESC;