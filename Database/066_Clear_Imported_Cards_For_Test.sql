-- Descrição: Limpa TODOS os cards e movimentos de uma CompanyID específica para testes de importação.
-- ATENÇÃO: ESTE SCRIPT APAGA DADOS. USE APENAS EM AMBIENTE DE DESENVOLVIMENTO.
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'ATENÇÃO: Iniciando limpeza de dados de teste para a CompanyID = 1';
PRINT '================================================================================';

-- Defina a CompanyID que terá os dados apagados
DECLARE @CompanyToClear BIGINT = 1;

BEGIN TRANSACTION;

BEGIN TRY

    -- Apaga primeiro os movimentos, que têm a chave estrangeira para os cards
    DELETE FROM [core].[CardMovements]
    WHERE CardID IN (SELECT CardID FROM [core].[Cards] WHERE CompanyID = @CompanyToClear);

    PRINT '- Movimentos da CompanyID ' + CAST(@CompanyToClear AS VARCHAR) + ' foram apagados.';

    -- Apaga os cards
    DELETE FROM [core].[Cards]
    WHERE CompanyID = @CompanyToClear;

    PRINT '- Cards da CompanyID ' + CAST(@CompanyToClear AS VARCHAR) + ' foram apagados.';

    COMMIT TRANSACTION;

    PRINT ''
    PRINT '✅ SUCESSO: Dados de teste para a CompanyID ' + CAST(@CompanyToClear AS VARCHAR) + ' foram limpos.';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação de limpeza falhou e a transação foi revertida.';
    THROW;
END CATCH
GO
