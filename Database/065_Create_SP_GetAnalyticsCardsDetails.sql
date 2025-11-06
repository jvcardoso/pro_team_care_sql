-- =============================================
-- Script: 065_Create_SP_GetAnalyticsCardsDetails.sql
-- Descrição: Cria a SP [core].[sp_GetAnalyticsCardsDetails] para retornar a lista detalhada de cards
--            relevantes para o período de análise, utilizando a mesma lógica de filtragem da
--            [reports].[sp_GetKanbanDashboard].
-- Autor: Sistema
-- Data: 2025-11-06
-- =============================================

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando criação da Stored Procedure [core].[sp_GetAnalyticsCardsDetails]';
PRINT '================================================================================';

IF OBJECT_ID('[core].[sp_GetAnalyticsCardsDetails]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [core].[sp_GetAnalyticsCardsDetails];
    PRINT 'Stored Procedure [core].[sp_GetAnalyticsCardsDetails] existente foi removida.';
END
GO

CREATE PROCEDURE [core].[sp_GetAnalyticsCardsDetails]
    @StartDate DATE,
    @EndDate DATE,
    @CompanyID BIGINT,
    @UserID BIGINT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Replicando a lógica de identificação de cards relevantes da [reports].[sp_GetKanbanDashboard]
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
    )
    -- Selecionar os detalhes dos cards relevantes
    SELECT
        c.CardID,
        c.Title,
        c.Description,
        c.Priority,
        c.CompanyID,
        c.UserID,
        c.ColumnID,
        cc.ColumnName,
        c.CreatedAt,
        c.CompletedDate,
        c.DueDate,
        c.IsDeleted
    FROM
        [core].[Cards] c
    INNER JOIN
        RelevantCards rc ON c.CardID = rc.CardID
    INNER JOIN
        [core].[CardColumns] cc ON c.ColumnID = cc.ColumnID
    WHERE
        c.CompanyID = @CompanyID
        AND c.IsDeleted = 0; -- Garantir que apenas cards não deletados sejam retornados

END;
GO

PRINT '✅ SUCESSO: Stored Procedure [core].[sp_GetAnalyticsCardsDetails] criada.';
PRINT '';
PRINT 'Exemplo de uso:';
PRINT 'EXEC [core].[sp_GetAnalyticsCardsDetails] @StartDate = ''2025-01-01'', @EndDate = ''2025-12-31'', @CompanyID = 1;';
PRINT 'EXEC [core].[sp_GetAnalyticsCardsDetails] @StartDate = ''2025-01-01'', @EndDate = ''2025-12-31'', @CompanyID = 1, @UserID = 123;';
PRINT '================================================================================';