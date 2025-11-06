-- Debug do Lead Time negativo
-- Verificar dados dos cards concluídos no período

USE [pro_team_care];
GO

DECLARE @StartDate DATE = '2025-11-01';
DECLARE @EndDate DATE = '2025-11-30';
DECLARE @CompanyID BIGINT = 1;

-- 1. Verificar cards concluídos no período com datas suspeitas
SELECT TOP 10
    c.CardID,
    c.Title,
    c.CreatedAt,
    c.CompletedDate,
    DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) as LeadTimeSeconds,
    DATEDIFF(MINUTE, c.CreatedAt, c.CompletedDate) as LeadTimeMinutes,
    CASE WHEN c.CompletedDate < c.CreatedAt THEN 'PROBLEMA: Conclusão ANTES da criação!' ELSE 'OK' END as Status
FROM core.Cards c
WHERE c.CompanyID = @CompanyID
  AND c.IsDeleted = 0
  AND c.CompletedDate IS NOT NULL
  AND CAST(c.CompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
ORDER BY DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) ASC; -- Mais negativos primeiro

-- 2. Verificar se há cards com CreatedAt no futuro
SELECT TOP 5
    CardID,
    Title,
    CreatedAt,
    CompletedDate,
    GETDATE() as Now
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CreatedAt > GETDATE()
ORDER BY CreatedAt DESC;

-- 3. Verificar se há CompletedDate no passado para cards criados recentemente
SELECT TOP 5
    CardID,
    Title,
    CreatedAt,
    CompletedDate,
    GETDATE() as Now
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CreatedAt > CompletedDate
ORDER BY CreatedAt DESC;