-- =========================================================================================
-- Script:         047_Refactor_Kanban_Menu.sql
-- Descrição:      Refatora o menu de Atividades para o novo modelo Kanban simplificado.
-- Versão:         1.1 (Correção da cláusula INSERT)
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '1. Removendo menus antigos de Atividades...';

    -- Remove associações de permissões dos submenus antigos
    DELETE FROM [core].[menu_item_permissions]
    WHERE menu_item_id IN (SELECT id FROM [core].[menu_items] WHERE name IN ('minhas_atividades', 'nova_atividade', 'board_pendencias'));

    -- Remove os submenus antigos
    DELETE FROM [core].[menu_items] WHERE name IN ('minhas_atividades', 'nova_atividade', 'board_pendencias');

    -- Remove o menu pai antigo
    DELETE FROM [core].[menu_items] WHERE name = 'atividades';

    PRINT ' -> Menus antigos removidos com sucesso.';

    PRINT '2. Criando novas permissões para Board e Dashboard...';

    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'board.view')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('board.view', 'Visualizar Board Kanban', 'Permite visualizar o quadro Kanban completo', 'board', 'view');
    
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'dashboard.view')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('dashboard.view', 'Visualizar Dashboard', 'Permite visualizar o dashboard de atividades', 'dashboard', 'view');

    PRINT ' -> Novas permissões criadas.';

    PRINT '3. Criando novos itens de menu de nível superior...';

    -- CORREÇÃO: Adicionada a coluna 'parent_id' na lista de colunas do INSERT
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'kanban_board')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path, context_type) VALUES ('kanban_board', 'Board', 'layout-grid', 30, NULL, '/admin/board', 'system');

    -- CORREÇÃO: Adicionada a coluna 'parent_id' na lista de colunas do INSERT
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'kanban_dashboard')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path, context_type) VALUES ('kanban_dashboard', 'Dashboard', 'bar-chart-2', 40, NULL, '/admin/dashboard', 'system');

    PRINT ' -> Novos menus criados.';

    PRINT '4. Associando permissões...';

    -- Declara variáveis para os novos IDs
    DECLARE @perm_board_view INT = (SELECT id FROM [core].[permissions] WHERE name = 'board.view');
    DECLARE @perm_dashboard_view INT = (SELECT id FROM [core].[permissions] WHERE name = 'dashboard.view');
    DECLARE @menu_board INT = (SELECT id FROM [core].[menu_items] WHERE name = 'kanban_board');
    DECLARE @menu_dashboard INT = (SELECT id FROM [core].[menu_items] WHERE name = 'kanban_dashboard');
    DECLARE @superuser_role_id INT = (SELECT id FROM [core].[roles] WHERE name = 'superuser');

    -- Associa permissão ao menu Board
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] WHERE menu_item_id = @menu_board AND permission_id = @perm_board_view)
        INSERT INTO [core].[menu_item_permissions] (menu_item_id, permission_id) VALUES (@menu_board, @perm_board_view);

    -- Associa permissão ao menu Dashboard
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] WHERE menu_item_id = @menu_dashboard AND permission_id = @perm_dashboard_view)
        INSERT INTO [core].[menu_item_permissions] (menu_item_id, permission_id) VALUES (@menu_dashboard, @perm_dashboard_view);

    -- Associa novas permissões ao Superuser
    IF @superuser_role_id IS NOT NULL
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_board_view)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_board_view);
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_dashboard_view)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_dashboard_view);
    END

    PRINT ' -> Associações concluídas.';

    PRINT '✅ Refatoração do menu concluída com sucesso!';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    THROW;

END CATCH;
GO