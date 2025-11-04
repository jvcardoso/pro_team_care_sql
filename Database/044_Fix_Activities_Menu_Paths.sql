-- =========================================================================================
-- Script:         044_Fix_Activities_Menu_Paths.sql
-- Descrição:      Corrige os paths dos menus de Atividades para incluir /admin
--                 e ajusta os ícones para o padrão do sistema
-- Data:           2025-11-03
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '🔧 Corrigindo paths e ícones dos menus de Atividades...';
    PRINT '';

    -- Atualizar menu principal: Atividades
    UPDATE [core].[menu_items]
    SET icon = 'clipboard'
    WHERE name = 'atividades';
    
    IF @@ROWCOUNT > 0
        PRINT '✅ Ícone do menu principal atualizado: clipboard';

    -- Atualizar submenu: Minhas Atividades
    UPDATE [core].[menu_items]
    SET path = '/admin/activities',
        icon = 'list'
    WHERE name = 'minhas_atividades';
    
    IF @@ROWCOUNT > 0
        PRINT '✅ Path "Minhas Atividades" corrigido: /admin/activities';

    -- Atualizar submenu: Nova Atividade
    UPDATE [core].[menu_items]
    SET path = '/admin/activities/new',
        icon = 'plus-circle'
    WHERE name = 'nova_atividade';
    
    IF @@ROWCOUNT > 0
        PRINT '✅ Path "Nova Atividade" corrigido: /admin/activities/new';

    -- Atualizar submenu: Board de Pendências
    UPDATE [core].[menu_items]
    SET path = '/admin/pendencies',
        icon = 'layout-grid'
    WHERE name = 'board_pendencias';
    
    IF @@ROWCOUNT > 0
        PRINT '✅ Path "Board de Pendências" corrigido: /admin/pendencies';

    PRINT '';
    PRINT '✅ Correção concluída com sucesso!';
    PRINT '';
    PRINT '🎯 Agora acesse:';
    PRINT '   - http://192.168.11.83:3000/admin/activities';
    PRINT '   - http://192.168.11.83:3000/admin/activities/new';
    PRINT '   - http://192.168.11.83:3000/admin/pendencies';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
    DECLARE @ErrorState INT = ERROR_STATE();
    RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);

    PRINT 'Ocorreu um erro. A transação foi revertida.';
END CATCH;
GO

-- Verificar resultado
SELECT 
    name AS Nome,
    label AS Label,
    icon AS Icone,
    path AS Path,
    display_order AS Ordem
FROM [core].[menu_items]
WHERE name IN ('atividades', 'minhas_atividades', 'nova_atividade', 'board_pendencias')
ORDER BY parent_id, display_order;
GO
