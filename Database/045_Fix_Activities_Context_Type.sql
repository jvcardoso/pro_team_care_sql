-- =========================================================================================
-- Script:         045_Fix_Activities_Context_Type.sql
-- Descrição:      Adiciona context_type='system' aos menus de atividades
--                 para que apareçam apenas para usuários administrativos
-- Data:           2025-11-03
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '🔧 Corrigindo context_type dos menus de Atividades...';
    PRINT '';

    -- Adicionar context_type='system' aos menus de atividades
    UPDATE [core].[menu_items]
    SET context_type = 'system'
    WHERE name IN ('atividades', 'minhas_atividades', 'nova_atividade', 'board_pendencias');

    IF @@ROWCOUNT > 0
        PRINT '✅ Context_type adicionado aos menus de atividades';

    PRINT '';
    PRINT '💡 Resultado:';
    PRINT '   - Menus de atividades agora aparecem apenas para usuários com context_type=''system''';
    PRINT '   - Usuários ''professional'' não verão mais os menus de atividades';
    PRINT '   - Resolve o problema de 404 para usuários não-admin';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
    DECLARE @ErrorState INT = ERROR_STATE();
    RAISERROR ( @ErrorMessage, @ErrorSeverity, @ErrorState);

    PRINT 'Ocorreu um erro. A transação foi revertida.';
END CATCH;
GO

-- Verificar resultado
SELECT
    name AS Nome,
    label AS Label,
    context_type AS Contexto,
    path AS Path
FROM [core].[menu_items]
WHERE name IN ('atividades', 'minhas_atividades', 'nova_atividade', 'board_pendencias')
ORDER BY display_order;
GO
