-- =============================================
-- Script: 064_Debug_Lead_Time.sql
-- Descrição: Versão de debug da SP para testar Lead Time sem validações
-- Problema: Lead Time ainda N/A mesmo com cards concluídos
-- Solução: Remover validações para testar se cálculo funciona
-- Autor: Sistema
-- Data: 2025-11-05
-- =============================================

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'DEBUG: Stored Procedure sem validações para testar Lead Time';
PRINT '================================================================================';

IF OBJECT_ID('[reports].[sp_GetKanbanDashboard]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [reports].[sp_GetKanbanDashboard];
    PRINT 'SP existente removida.';
END
GO

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
    -- 4. CTE para calcular os tempos - VERSÃO DEBUG (sem validações)
    CardTimings AS (
        SELECT
            CardID,
            MIN(CardCreatedAt) AS CreatedAt,
            MIN(CASE WHEN NewColumnName != 'Backlog' AND OldColumnName = 'Backlog' THEN MovementDate ELSE NULL END) AS StartDate,
            MAX(CASE WHEN NewColumnName = 'Concluído' THEN MovementDate ELSE NULL END) AS ActualCompletedDate,
            MAX(DueDate) as DueDate
        FROM RelevantMovements
        GROUP BY CardID
    )
    -- 5. Construir JSON de saída
    SELECT
    (
        -- 5.1. Summary com KPIs principais
        SELECT
            -- Lead Time: DEBUG - calcular SEM validações
            AVG(CASE
                WHEN ct.ActualCompletedDate IS NOT NULL
                     AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                THEN ABS(DATEDIFF(SECOND, ct.CreatedAt, ct.ActualCompletedDate))  -- ABS para evitar negativos
                ELSE NULL
            END) AS leadTimeAvgSeconds,

            -- Cycle Time: DEBUG - calcular SEM validações
            AVG(CASE
                WHEN ct.ActualCompletedDate IS NOT NULL
                     AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                     AND ct.StartDate IS NOT NULL
                THEN ABS(DATEDIFF(SECOND, ct.StartDate, ct.ActualCompletedDate))  -- ABS para evitar negativos
                ELSE NULL
            END) AS cycleTimeAvgSeconds,

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

            -- SLA Compliance: % de cards concluídos dentro do prazo
            CASE
                WHEN COUNT(DISTINCT CASE
                    WHEN ct.ActualCompletedDate IS NOT NULL
                         AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                    THEN ct.CardID
                    ELSE NULL
                END) > 0
                THEN (
                    SUM(CASE
                        WHEN ct.ActualCompletedDate IS NOT NULL
                             AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                             AND ct.DueDate IS NOT NULL
                             AND ct.ActualCompletedDate <= ct.DueDate
                        THEN 1
                        ELSE 0
                    END) * 1.0
                ) / COUNT(DISTINCT CASE
                    WHEN ct.ActualCompletedDate IS NOT NULL
                         AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                    THEN ct.CardID
                    ELSE NULL
                END)
                ELSE 0
            END AS slaCompliance
        FROM CardTimings ct
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ) AS summary,
    (
        -- 5.2. Time per Stage: Tempo médio por coluna
        SELECT
            OldColumnName AS columnName,
            AVG(TimeInStageSeconds) AS avgSeconds
        FROM RelevantMovements
        WHERE OldColumnName IS NOT NULL
          AND TimeInStageSeconds IS NOT NULL
          AND TimeInStageSeconds > 0
        GROUP BY OldColumnName
        FOR JSON PATH
    ) AS timePerStage,
    (
        -- 5.3. Throughput History: Conclusões por dia no período
        SELECT
            CAST(MovementDate AS DATE) AS [date],
            COUNT(DISTINCT CardID) AS [count]
        FROM RelevantMovements
        WHERE NewColumnName = 'Concluído'
          AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate
        GROUP BY CAST(MovementDate AS DATE)
        ORDER BY [date]
        FOR JSON PATH
    ) AS throughputHistory

    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;

END;
GO

PRINT '✅ SP de DEBUG criada - sem validações para testar cálculo!';
PRINT '';
PRINT 'Esta versão:';
PRINT '• Remove validações de datas';
PRINT '• Usa ABS() para evitar valores negativos';
PRINT '• Deve mostrar algum valor no Lead Time';
PRINT '';
PRINT 'Teste:';
PRINT 'EXEC [reports].[sp_GetKanbanDashboard] @StartDate=''2025-11-01'', @EndDate=''2025-11-05'', @CompanyID=1';
PRINT '';
PRINT 'IMPORTANTE: Após testar, voltar para versão 063!';
GO