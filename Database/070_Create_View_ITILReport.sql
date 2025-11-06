USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Criando view analytics.vw_ITILReport';
PRINT '================================================================================';

-- Criar schema analytics se não existir
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'analytics')
BEGIN
    EXEC('CREATE SCHEMA analytics');
    PRINT '✅ Schema analytics criado';
END

-- Dropar view se existir
IF OBJECT_ID('analytics.vw_ITILReport', 'V') IS NOT NULL
    DROP VIEW analytics.vw_ITILReport;
GO

CREATE VIEW analytics.vw_ITILReport AS
SELECT 
    c.CardID,
    c.CompanyID,
    c.ExternalCardID,
    c.Title,
    c.Description,
    c.OriginalText,
    cc.ColumnName,
    c.ITILCategory,
    c.Priority,
    c.Size,
    c.RiskLevel,
    c.HasWindow,
    c.HasCAB,
    c.HasBackout,
    c.StartDate,
    c.CompletedDate,
    c.DueDate,
    c.CreatedAt,
    u.email_address AS OwnerEmail,
    u.id AS OwnerUserID,
    
    -- Métricas de tempo
    DATEDIFF(SECOND, c.CreatedAt, c.CompletedDate) AS LeadTimeSeconds,
    DATEDIFF(SECOND, c.StartDate, c.CompletedDate) AS CycleTimeSeconds,
    
    -- SLA Compliance
    CASE 
        WHEN c.CompletedDate IS NOT NULL AND c.DueDate IS NOT NULL 
            THEN CASE WHEN c.CompletedDate <= c.DueDate THEN 1 ELSE 0 END 
        ELSE NULL 
    END AS MetSLA,
    
    -- Dias de atraso
    CASE 
        WHEN c.CompletedDate > c.DueDate 
            THEN DATEDIFF(DAY, c.DueDate, c.CompletedDate)
        ELSE 0
    END AS DaysLate,
    
    -- Status
    CASE 
        WHEN c.CompletedDate IS NOT NULL THEN 'Concluído'
        WHEN c.StartDate IS NOT NULL THEN 'Em Andamento'
        ELSE 'Não Iniciado'
    END AS Status

FROM core.Cards c
JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
LEFT JOIN core.Users u ON c.UserID = u.id
WHERE c.IsDeleted = 0;
GO

PRINT '✅ View analytics.vw_ITILReport criada com sucesso!';
PRINT '================================================================================';
GO