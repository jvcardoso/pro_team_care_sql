-- =========================================================================================
-- Script:         049_Reorganize_Kanban_Menu.sql
-- Descrição:      Reorganiza os menus do Kanban sob um único menu pai "Quadro Kanban".
-- Versão:         1.1 (Correção final da cláusula INSERT)
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '1. Criando o menu pai ''Quadro Kanban''...';

    -- CORREÇÃO: Adicionada a coluna 'parent_id' na lista de colunas do INSERT
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'kanban_parent')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path, context_type) VALUES ('kanban_parent', 'Quadro Kanban', 'clipboard-check', 30, NULL, NULL, 'system');
    
    PRINT ' -> Menu pai criado ou já existente.';

    PRINT '2. Associando os menus existentes como submenus...';

    -- Declara variáveis para os IDs
    DECLARE @parent_menu_id INT = (SELECT id FROM [core].[menu_items] WHERE name = 'kanban_parent');
    DECLARE @board_menu_id INT = (SELECT id FROM [core].[menu_items] WHERE name = 'kanban_board');
    DECLARE @dashboard_menu_id INT = (SELECT id FROM [core].[menu_items] WHERE name = 'kanban_dashboard');

    -- Atualiza o menu 'Board' para ser um submenu
    IF @board_menu_id IS NOT NULL AND @parent_menu_id IS NOT NULL
    BEGIN
        UPDATE [core].[menu_items]
        SET parent_id = @parent_menu_id,
            display_order = 1,
            label = 'Board Kanban' -- Renomeia para mais clareza
        WHERE id = @board_menu_id;
        PRINT ' -> Menu ''Board Kanban'' associado ao pai.';
    END

    -- Atualiza o menu 'Dashboard' para ser um submenu
    IF @dashboard_menu_id IS NOT NULL AND @parent_menu_id IS NOT NULL
    BEGIN
        UPDATE [core].[menu_items]
        SET parent_id = @parent_menu_id,
            display_order = 2 -- Segundo submenu
        WHERE id = @dashboard_menu_id;
        PRINT ' -> Menu ''Dashboard'' associado ao pai.';
    END

    PRINT '✅ Reorganização do menu concluída com sucesso!';

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
PRINT 'Verificando a nova estrutura do menu:'
SELECT 
    p.label AS MenuPai,
    c.label AS SubMenu,
    c.path AS Path,
    c.display_order AS Ordem
FROM [core].[menu_items] c
JOIN [core].[menu_items] p ON c.parent_id = p.id
WHERE p.name = 'kanban_parent'
ORDER BY c.display_order;
GO