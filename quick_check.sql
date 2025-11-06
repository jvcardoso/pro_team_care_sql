-- Verificação rápida: há cards concluídos no banco?

USE [pro_team_care];
GO

-- 1. Cards concluídos hoje
SELECT COUNT(*) as CardsConcluidosHoje
FROM core.Cards
WHERE CompanyID = 1
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) = CAST(GETDATE() AS DATE);

-- 2. Últimos 5 cards concluídos
SELECT TOP 5
    CardID,
    Title,
    CompletedDate,
    DATEDIFF(HOUR, CreatedAt, CompletedDate) as HorasLeadTime
FROM core.Cards
WHERE CompanyID = 1
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
ORDER BY CompletedDate DESC;

-- 3. Teste da SP com período de hoje
DECLARE @Hoje DATE = CAST(GETDATE() AS DATE);
EXEC [reports].[sp_GetKanbanDashboard]
    @StartDate = @Hoje,
    @EndDate = @Hoje,
    @CompanyID = 1;