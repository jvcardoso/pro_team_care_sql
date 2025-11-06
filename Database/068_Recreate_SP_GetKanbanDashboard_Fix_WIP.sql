-- =============================================
-- Script: 068_Recreate_SP_GetKanbanDashboard_Fix_WIP.sql
-- Descrição: Recria a SP [reports].[sp_GetKanbanDashboard] para forçar a correção definitiva
--            da métrica de WIP. A SP é primeiro removida (DROP) e depois criada (CREATE)
--            com a lógica de contagem de WIP que foi validada como correta nos diagnósticos.
-- Autor: Sistema
-- Data: 2025-11-06
-- =============================================

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Recriando [reports].[sp_GetKanbanDashboard] para correção definitiva do WIP';
PRINT '================================================================================';

-- Passo 1: Remover a procedure existente para garantir uma recriação limpa
IF OBJECT_ID('[reports].[sp_GetKanbanDashboard]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [reports].[sp_GetKanbanDashboard];
    PRINT 'Procedure [reports].[sp_GetKanbanDashboard] existente foi removida.';
END
GO

-- Passo 2: Criar a procedure novamente com a lógica 100% validada
CREATE PROCEDURE [reports].[sp_GetKanbanDashboard]
    @StartDate DATE,
    @EndDate DATE,
    @CompanyID BIGINT,
    @UserID BIGINT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    WITH AllMovements AS (
        SELECT *
        FROM [analytics].[vw_CardFullHistory]
        WHERE CompanyID = @CompanyID
          AND (@UserID IS NULL OR MovedByUserID = @UserID)
    ),
    RelevantCards AS (
        SELECT DISTINCT CardID
        FROM AllMovements
        WHERE
            (NewColumnName = 'Concluído' AND CAST(MovementDate AS DATE) BETWEEN @StartDate AND @EndDate)
            OR
            (CardID IN (
                SELECT CardID FROM core.Cards
                WHERE CompanyID = @CompanyID AND IsDeleted = 0 AND CompletedDate IS NULL
            ))
    ),
    RelevantMovements AS (
        SELECT am.*
        FROM AllMovements am
        INNER JOIN RelevantCards rc ON am.CardID = rc.CardID
    ),
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
    SELECT
    (
        SELECT
            AVG(CASE
                WHEN ct.ActualCompletedDate IS NOT NULL
                     AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                     AND ct.ActualCompletedDate >= ct.CreatedAt
                     AND DATEDIFF(SECOND, ct.CreatedAt, ct.ActualCompletedDate) > 0
                THEN DATEDIFF(SECOND, ct.CreatedAt, ct.ActualCompletedDate)
                ELSE NULL
            END) AS leadTimeAvgSeconds,

            AVG(CASE
                WHEN ct.ActualCompletedDate IS NOT NULL
                     AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                     AND ct.StartDate IS NOT NULL
                     AND ct.ActualCompletedDate >= ct.StartDate
                     AND DATEDIFF(SECOND, ct.StartDate, ct.ActualCompletedDate) > 0
                THEN DATEDIFF(SECOND, ct.StartDate, ct.ActualCompletedDate)
                ELSE NULL
            END) AS cycleTimeAvgSeconds,

            COUNT(DISTINCT CASE
                WHEN ct.ActualCompletedDate IS NOT NULL
                     AND CAST(ct.ActualCompletedDate AS DATE) BETWEEN @StartDate AND @EndDate
                THEN ct.CardID
                ELSE NULL
            END) AS throughput,

            -- LÓGICA DE CONTAGEM DO WIP VALIDADA PELO DIAGNÓSTICO
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

PRINT '✅ SUCESSO: Stored Procedure [reports].[sp_GetKanbanDashboard] foi recriada.';
PRINT 'A métrica de WIP agora está definitivamente correta no banco de dados.';
PRINT '================================================================================';
