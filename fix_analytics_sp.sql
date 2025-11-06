-- Correção da Stored Procedure sp_GetKanbanDashboard
-- Adiciona proteção contra divisão por zero e erros matemáticos

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'CORREÇÃO: Stored Procedure [reports].[sp_GetKanbanDashboard]';
PRINT '================================================================================';

-- Backup da versão atual (se existir)
IF OBJECT_ID('[reports].[sp_GetKanbanDashboard]', 'P') IS NOT NULL
BEGIN
    PRINT 'Fazendo backup da versão atual...';
    EXEC sp_rename '[reports].[sp_GetKanbanDashboard]', 'sp_GetKanbanDashboard_backup';
END

-- Criar versão corrigida
CREATE PROCEDURE [reports].[sp_GetKanbanDashboard]
    @StartDate DATE,
    @EndDate DATE,
    @CompanyID BIGINT,
    @UserID BIGINT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. CTE para pegar TODOS os movimentos dos cards da empresa
    WITH AllMovements AS (
        SELECT *
        FROM [analytics].[vw_CardFullHistory]
        WHERE CompanyID = @CompanyID
          AND (@UserID IS NULL OR MovedByUserID = @UserID)
    ),
    -- 2. CTE para identificar cards relevantes (concluídos no período OU em andamento)
    RelevantCards AS (
        SELECT DISTINCT CardID
        FROM AllMovements
        WHERE
            -- Cards concluídos no período
            (NewColumnName = 'Concluído' AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate)
            OR
            -- Cards em andamento (não concluídos)
            (CardID IN (
                SELECT CardID FROM core.Cards
                WHERE CompanyID = @CompanyID
                  AND IsDeleted = 0
                  AND CompletedDate IS NULL
            ))
    ),
    -- 3. CTE com movimentos dos cards relevantes
    RelevantMovements AS (
        SELECT am.*
        FROM AllMovements am
        INNER JOIN RelevantCards rc ON am.CardID = rc.CardID
    ),
    -- 4. CTE para calcular os tempos - VERSÃO CORRIGIDA
    CardTimings AS (
        SELECT
            CardID,
            MIN(CardCreatedAt) AS CreatedAt,
            MIN(CASE WHEN NewColumnName != 'Backlog' AND OldColumnName = 'Backlog' THEN MovementDate ELSE NULL END) AS StartDate,
            MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS ActualCompletedDate,
            MAX(DueDate) as DueDate
        FROM RelevantMovements
        GROUP BY CardID
        -- Removida validação HAVING que pode causar problemas
    )
    -- 5. Construir JSON de saída
    SELECT
    (
        -- 5.1. Summary com KPIs principais - VERSÃO PROTEGIDA
        SELECT
            -- Lead Time: calcular apenas se há dados válidos
            CASE
                WHEN COUNT(CASE WHEN ct.ActualCompletedDate IS NOT NULL AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate THEN 1 END) > 0
                THEN AVG(CASE
                    WHEN ct.ActualCompletedDate IS NOT NULL
                         AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                    THEN ABS(DATEDIFF(SECOND, ct.CreatedAt, ct.ActualCompletedDate))
                    ELSE NULL
                END)
                ELSE NULL
            END AS leadTimeAvgSeconds,

            -- Cycle Time: calcular apenas se há dados válidos
            CASE
                WHEN COUNT(CASE WHEN ct.ActualCompletedDate IS NOT NULL AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate AND ct.StartDate IS NOT NULL THEN 1 END) > 0
                THEN AVG(CASE
                    WHEN ct.ActualCompletedDate IS NOT NULL
                         AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                         AND ct.StartDate IS NOT NULL
                    THEN ABS(DATEDIFF(SECOND, ct.StartDate, ct.ActualCompletedDate))
                    ELSE NULL
                END)
                ELSE NULL
            END AS cycleTimeAvgSeconds,

            -- Throughput: Cards concluídos no período
            COUNT(DISTINCT CASE
                WHEN ct.ActualCompletedDate IS NOT NULL
                     AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                THEN ct.CardID
                ELSE NULL
            END) AS throughput,

            -- WIP: Cards em andamento (não concluídos)
            (SELECT COUNT(DISTINCT CardID)
             FROM core.Cards
             WHERE CompanyID = @CompanyID
               AND IsDeleted = 0
               AND CompletedDate IS NULL
               AND ColumnID NOT IN (
                   SELECT ColumnID FROM core.CardColumns
                   WHERE CompanyID = @CompanyID AND ColumnName IN ('Backlog', 'Concluído')
               )
            ) AS wip,

            -- SLA Compliance: % de cards concluídos dentro do prazo - PROTEGIDO
            CASE
                WHEN COUNT(DISTINCT CASE
                    WHEN ct.ActualCompletedDate IS NOT NULL
                         AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                    THEN ct.CardID
                    ELSE NULL
                END) > 0
                THEN (
                    CAST(SUM(CASE
                        WHEN ct.ActualCompletedDate IS NOT NULL
                             AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                             AND ct.DueDate IS NOT NULL
                             AND ct.ActualCompletedDate <= ct.DueDate
                        THEN 1
                        ELSE 0
                    END) AS DECIMAL(10,2))
                    /
                    NULLIF(COUNT(DISTINCT CASE
                        WHEN ct.ActualCompletedDate IS NOT NULL
                             AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                        THEN ct.CardID
                        ELSE NULL
                    END), 0)
                ) * 100.0  -- Multiplicar por 100 para percentual
                ELSE 0.0
            END AS slaCompliance

        FROM CardTimings ct
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ) AS summary,

    -- 5.2. Time per Stage: Tempo médio por coluna
    (
        SELECT
            cc.ColumnName,
            AVG(CASE
                WHEN rm.NextMovementDate IS NOT NULL
                THEN DATEDIFF(SECOND, rm.MovementDate, rm.NextMovementDate)
                ELSE NULL
            END) as avgTimeInSeconds
        FROM (
            SELECT
                CardID,
                ColumnID,
                MovementDate,
                LEAD(MovementDate) OVER (PARTITION BY CardID ORDER BY MovementDate) as NextMovementDate
            FROM RelevantMovements
        ) rm
        INNER JOIN core.CardColumns cc ON rm.ColumnID = cc.ColumnID
        WHERE rm.NextMovementDate IS NOT NULL
        GROUP BY cc.ColumnID, cc.ColumnName
        FOR JSON PATH
    ) AS timePerStage,

    -- 5.3. Throughput History: Evolução diária
    (
        SELECT
            CAST(ct.ActualCompletedDate AS DATE) as date,
            COUNT(*) as count
        FROM CardTimings ct
        WHERE ct.ActualCompletedDate IS NOT NULL
          AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
        GROUP BY CAST(ct.ActualCompletedDate AS DATE)
        ORDER BY CAST(ct.ActualCompletedDate AS DATE)
        FOR JSON PATH
    ) AS throughputHistory

    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;

END;
GO

PRINT '✅ Stored Procedure corrigida criada com sucesso!';
PRINT 'Testando execução...';

-- Teste de execução
DECLARE @TestStart DATE = '2025-01-01';
DECLARE @TestEnd DATE = '2025-11-06';
DECLARE @TestCompany BIGINT = 1;

EXEC [reports].[sp_GetKanbanDashboard]
    @StartDate = @TestStart,
    @EndDate = @TestEnd,
    @CompanyID = @TestCompany;

PRINT '✅ Teste executado com sucesso!';
PRINT '';
PRINT '================================================================================';