-- =========================================================================================
-- Script:         048_Correct_Board_Menu_Path.sql
-- Descrição:      Alinha o path do menu do Board com a rota do frontend (/admin/kanban).
-- Data:           2025-11-03
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '🔧 Atualizando o path do menu ''kanban_board''...';

    UPDATE [core].[menu_items]
    SET path = '/admin/kanban'
    WHERE name = 'kanban_board';

    IF @@ROWCOUNT > 0
        PRINT '✅ Path do menu ''kanban_board'' atualizado para /admin/kanban com sucesso!';
    ELSE
        PRINT '⚠️ O menu ''kanban_board'' não foi encontrado. Nenhuma alteração feita.';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    THROW;

END CATCH;
GO

-- Verificação final
PRINT ''
PRINT 'Verificando o resultado:'
SELECT name, label, path FROM [core].[menu_items] WHERE name = 'kanban_board';
GO
