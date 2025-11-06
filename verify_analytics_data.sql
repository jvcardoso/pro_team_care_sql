-- Verificação completa dos dados do Analytics Kanban

USE [pro_team_care];
GO

DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'VERIFICAÇÃO COMPLETA: Dados do Analytics Kanban';
PRINT '================================================================================';

-- 1. Status geral dos cards
SELECT
    'Total de cards' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0

UNION ALL

SELECT
    'Cards concluídos (todos)' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND CompletedDate IS NOT NULL

UNION ALL

SELECT
    'Cards em andamento' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND CompletedDate IS NULL;

-- 2. Cards concluídos por período
SELECT
    CASE
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -7, GETDATE()) THEN 'Últimos 7 dias'
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -30, GETDATE()) THEN 'Últimos 30 dias'
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -90, GETDATE()) THEN 'Últimos 90 dias'
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -365, GETDATE()) THEN 'Últimos 365 dias'
        ELSE 'Mais antigo'
    END as Periodo,
    COUNT(*) as Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND CompletedDate IS NOT NULL
GROUP BY
    CASE
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -7, GETDATE()) THEN 'Últimos 7 dias'
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -30, GETDATE()) THEN 'Últimos 30 dias'
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -90, GETDATE()) THEN 'Últimos 90 dias'
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -365, GETDATE()) THEN 'Últimos 365 dias'
        ELSE 'Mais antigo'
    END
ORDER BY
    CASE
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -7, GETDATE()) THEN 1
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -30, GETDATE()) THEN 2
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -90, GETDATE()) THEN 3
        WHEN CAST(CompletedDate AS DATE) >= DATEADD(DAY, -365, GETDATE()) THEN 4
        ELSE 5
    END;

-- 3. Últimos 10 cards concluídos
SELECT TOP 10
    CardID,
    Title,
    ColumnID,
    CreatedAt,
    CompletedDate,
    DATEDIFF(DAY, CreatedAt, CompletedDate) as LeadTimeDias
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND CompletedDate IS NOT NULL
ORDER BY CompletedDate DESC;

-- 4. Verificar período exato do frontend (2025-10-06 até 2025-11-05)
SELECT
    'Período exato do frontend (2025-10-06 até 2025-11-05)' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) >= '2025-10-06'
  AND CAST(CompletedDate AS DATE) <= '2025-11-05';

-- 5. Teste do filtro do endpoint (simulando a query exata)
SELECT
    'Teste filtro endpoint (últimos 30 dias)' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID
  AND IsDeleted = 0
  AND CompletedDate IS NOT NULL
  AND CAST(CompletedDate AS DATE) >= DATEADD(DAY, -30, CAST(GETDATE() AS DATE))
  AND CAST(CompletedDate AS DATE) <= CAST(GETDATE() AS DATE)
  AND ColumnID IN (1,2,3,4,5);

-- 6. Verificar se há cards na coluna "Concluído" (ID=5)
SELECT
    'Cards na coluna Concluído (ID=5)' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND ColumnID = 5;

-- 7. Cards na coluna "Concluído" com CompletedDate
SELECT
    'Cards na coluna Concluído com CompletedDate' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND ColumnID = 5 AND CompletedDate IS NOT NULL;

PRINT '';
PRINT '================================================================================';
PRINT 'ANÁLISE:';
PRINT '- Se "Teste filtro endpoint" = 0, então Array(0) é CORRETO';
PRINT '- Se > 0, há problema no endpoint';
PRINT '- Verificar se o período do frontend corresponde aos dados reais';
PRINT '================================================================================';