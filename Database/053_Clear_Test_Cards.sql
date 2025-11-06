-- =============================================
-- Script: 053_Clear_Test_Cards.sql
-- Descrição: Exclui (hard-delete) todos os cards, movimentos e imagens associadas para uma CompanyID específica.
--            A exclusão em cascata (ON DELETE CASCADE) removerá os dados relacionados.
-- Autor: Gemini
-- Data: 2025-11-05
-- =============================================

USE [pro_team_care];
GO

DECLARE @TargetCompanyID BIGINT = 1; -- Defina a CompanyID alvo aqui

BEGIN TRANSACTION;

BEGIN TRY

    PRINT 'Iniciando exclusão (hard-delete) dos cards para a CompanyID: ' + CAST(@TargetCompanyID AS VARCHAR) + '...';

    -- A exclusão de cards irá acionar o ON DELETE CASCADE para CardMovements, que por sua vez acionará para MovementImages.
    DELETE FROM [core].[Cards]
    WHERE
        CompanyID = @TargetCompanyID;

    PRINT CAST(@@ROWCOUNT AS VARCHAR) + ' cards (e seus dados associados em cascata) foram excluídos.';

    COMMIT TRANSACTION;
    PRINT '✅ SUCESSO: Limpeza concluída e transação commitada.';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação de limpeza falhou e a transação foi revertida.';
    THROW;
END CATCH
GO
