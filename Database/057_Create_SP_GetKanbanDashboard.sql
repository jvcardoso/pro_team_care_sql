-- Descrição: Cria a SP [reports].[sp_GetKanbanDashboard] para gerar dados consolidados do painel de BI.
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando criação da Stored Procedure [reports].[sp_GetKanbanDashboard]';
PRINT '================================================================================';

IF OBJECT_ID('[reports].[sp_GetKanbanDashboard]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [reports].[sp_GetKanbanDashboard];
    PRINT 'Stored Procedure [reports].[sp_GetKanbanDashboard] existente foi removida.';
END
GO

CREATE PROCEDURE [reports].[sp_GetKanbanDashboard]
    @StartDate DATE,
    @EndDate DATE,
    @CompanyID BIGINT, -- CompanyID é mais apropriado que BoardID para multitenancy
    @UserID BIGINT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. CTE para filtrar o range de dados relevante na view
    WITH RelevantMovements AS (
        SELECT *
        FROM [analytics].[vw_CardFullHistory]
        WHERE CompanyID = @CompanyID
          AND MovementDate BETWEEN @StartDate AND @EndDate
          AND (@UserID IS NULL OR MovedByUserID = @UserID)
    ),
    -- 2. CTE para calcular os tempos de Lead e Cycle
    CardTimings AS (
        SELECT
            CardID,
            MIN(CardCreatedAt) AS CreatedAt,
            MIN(CASE WHEN OldColumnName = 'Backlog' THEN MovementDate ELSE NULL END) AS StartDate, -- Data que saiu do backlog
            MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS CompletedDate,
            MAX(DueDate) as DueDate
        FROM RelevantMovements
        GROUP BY CardID
    )
    -- 3. Calcular métricas do summary
    DECLARE @leadTimeAvgSeconds BIGINT = (
        SELECT AVG(CASE WHEN ct.CompletedDate IS NOT NULL THEN DATEDIFF(SECOND, ct.CreatedAt, ct.CompletedDate) ELSE NULL END)
        FROM RelevantMovements rm
        LEFT JOIN CardTimings ct ON rm.CardID = ct.CardID
    );

    DECLARE @cycleTimeAvgSeconds BIGINT = (
        SELECT AVG(CASE WHEN ct.CompletedDate IS NOT NULL AND ct.StartDate IS NOT NULL THEN DATEDIFF(SECOND, ct.StartDate, ct.CompletedDate) ELSE NULL END)
        FROM RelevantMovements rm
        LEFT JOIN CardTimings ct ON rm.CardID = ct.CardID
    );

    DECLARE @throughput INT = (
        SELECT COUNT(DISTINCT CASE WHEN rm.NewColumnName = 'Concluído' THEN rm.CardID ELSE NULL END)
        FROM RelevantMovements rm
    );

    DECLARE @wip INT = (
        SELECT COUNT(DISTINCT CASE WHEN rm.OldColumnName NOT IN ('Backlog', 'Concluído') THEN rm.CardID ELSE NULL END)
        FROM RelevantMovements rm
    );

    DECLARE @slaCompliance DECIMAL(5,4) = (
        SELECT CASE
            WHEN COUNT(DISTINCT CASE WHEN ct.CompletedDate IS NOT NULL THEN ct.CardID ELSE NULL END) > 0
            THEN (SUM(CASE WHEN ct.CompletedDate IS NOT NULL AND ct.CompletedDate <= ct.DueDate THEN 1 ELSE 0 END) * 1.0) / COUNT(DISTINCT CASE WHEN ct.CompletedDate IS NOT NULL THEN ct.CardID ELSE NULL END)
            ELSE 0
        END
        FROM RelevantMovements rm
        LEFT JOIN CardTimings ct ON rm.CardID = ct.CardID
    );

    -- 4. Construir JSON final
    SELECT
        JSON_QUERY('{"leadTimeAvgSeconds":' + ISNULL(CAST(@leadTimeAvgSeconds AS VARCHAR), 'null') +
                   ',"cycleTimeAvgSeconds":' + ISNULL(CAST(@cycleTimeAvgSeconds AS VARCHAR), 'null') +
                   ',"throughput":' + CAST(@throughput AS VARCHAR) +
                   ',"wip":' + CAST(@wip AS VARCHAR) +
                   ',"slaCompliance":' + CAST(@slaCompliance AS VARCHAR) + '}') AS summary,
        (
            SELECT
                OldColumnName AS columnName,
                AVG(TimeInStageSeconds) AS avgSeconds
            FROM RelevantMovements
            WHERE OldColumnName IS NOT NULL
            GROUP BY OldColumnName
            FOR JSON PATH
        ) AS timePerStage,
        (
            SELECT
                CAST(MovementDate AS DATE) AS [date],
                COUNT(DISTINCT rm.CardID) AS [count]
            FROM RelevantMovements rm
            WHERE NewColumnName = 'Concluído'
            GROUP BY CAST(MovementDate AS DATE)
            ORDER BY [date]
            FOR JSON PATH
        ) AS throughputHistory
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;

END;
GO

PRINT '================================================================================';
PRINT '✅ SUCESSO: Stored Procedure [reports].[sp_GetKanbanDashboard] criada.';
PRINT '================================================================================';
GO

-- Exemplo de como executar a Stored Procedure
/*
EXEC [reports].[sp_GetKanbanDashboard]
    @StartDate = '2025-01-01',
    @EndDate = '2025-12-31',
    @CompanyID = 1; -- Substitua pelo ID da empresa
*/
