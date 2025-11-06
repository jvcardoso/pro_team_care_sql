-- Debug simples: verificar se há cards concluídos no período

USE [pro_team_care];
GO

DECLARE @StartDate DATE = '2025-11-01';
DECLARE @EndDate DATE = '2025-11-30';
DECLARE @CompanyID BIGINT = 1;

-- 1. Cards concluídos no período
SELECT
    COUNT(*) as CardsConcluidosPeriodo
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate;

-- 2. Cards com CompletedDate válido (>= CreatedAt)
SELECT
    COUNT(*) as CardsValidos
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
  AND CompletedDate >= CreatedAt;

-- 3. Cards com problema (CompletedDate < CreatedAt)
SELECT
    COUNT(*) as CardsInvalidos
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CompletedDate < CreatedAt;

-- 4. Executar a SP diretamente para ver resultado
EXEC [reports].[sp_GetKanbanDashboard]
    @StartDate = @StartDate,
    @EndDate = @EndDate,
    @CompanyID = @CompanyID;