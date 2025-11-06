-- Teste direto da Stored Procedure sp_GetKanbanDashboard

USE [pro_team_care];
GO

DECLARE @StartDate DATE = '2025-01-01';
DECLARE @EndDate DATE = '2025-11-06';
DECLARE @CompanyID BIGINT = 1;

PRINT '================================================================================';
PRINT 'TESTE DIRETO: sp_GetKanbanDashboard';
PRINT '================================================================================';

-- Verificar se a SP existe
IF OBJECT_ID('[reports].[sp_GetKanbanDashboard]', 'P') IS NULL
BEGIN
    PRINT '❌ ERRO: Stored Procedure [reports].[sp_GetKanbanDashboard] não existe!';
    RETURN;
END
ELSE
BEGIN
    PRINT '✅ Stored Procedure existe.';
END

-- Testar execução da SP
BEGIN TRY
    PRINT 'Executando SP...';
    EXEC [reports].[sp_GetKanbanDashboard]
        @StartDate = @StartDate,
        @EndDate = @EndDate,
        @CompanyID = @CompanyID;

    PRINT '✅ SP executada com sucesso!';
END TRY
BEGIN CATCH
    PRINT '❌ ERRO na execução da SP:';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT 'Error Procedure: ' + ISNULL(ERROR_PROCEDURE(), 'N/A');
END CATCH;

PRINT '';
PRINT '================================================================================';