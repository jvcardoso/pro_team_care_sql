-- =========================================================================================
-- Autor: Gemini (baseado na especificação de Juliano)
-- Data: 2025-11-03
-- Descrição: Cadastra o Módulo de Atividades, suas permissões e itens de menu no sistema.
-- Versão: 1.4 (Correção final da action 'edit' para 'update')
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    -- Declaração de variáveis para IDs
    DECLARE @superuser_role_id INT;
    DECLARE @perm_activities_view INT, @perm_activities_create INT, @perm_activities_update INT;
    DECLARE @perm_pendencies_view INT, @perm_pendencies_manage INT;
    DECLARE @menu_atividades INT, @menu_minhas_atividades INT, @menu_nova_atividade INT, @menu_board_pendencias INT;

    -- Obter ID do Role Superuser
    SELECT @superuser_role_id = id FROM [core].[roles] WHERE name = 'superuser';

    -- 1. Cria Permissões (se não existirem)
    PRINT '1. Verificando e criando permissões...';
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'activities.view')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('activities.view', 'Visualizar Atividades', 'Permite visualizar a lista de atividades', 'activities', 'view');
    
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'activities.create')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('activities.create', 'Criar Atividades', 'Permite criar novas atividades', 'activities', 'create');

    -- CORREÇÃO: Usando 'update' em vez de 'edit'
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'activities.update')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('activities.update', 'Editar Atividades', 'Permite editar atividades existentes', 'activities', 'update');
    
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'pendencies.view')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('pendencies.view', 'Visualizar Pendências', 'Permite visualizar o board de pendências', 'pendencies', 'view');
    
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'pendencies.manage')
        INSERT INTO [core].[permissions] (name, display_name, description, resource, action) VALUES ('pendencies.manage', 'Gerenciar Pendências', 'Permite gerenciar (criar, editar, mover) pendências', 'pendencies', 'manage');

    -- Seleciona os IDs das permissões para uso posterior
    SELECT @perm_activities_view = id FROM [core].[permissions] WHERE name = 'activities.view';
    SELECT @perm_activities_create = id FROM [core].[permissions] WHERE name = 'activities.create';
    SELECT @perm_activities_update = id FROM [core].[permissions] WHERE name = 'activities.update';
    SELECT @perm_pendencies_view = id FROM [core].[permissions] WHERE name = 'pendencies.view';
    SELECT @perm_pendencies_manage = id FROM [core].[permissions] WHERE name = 'pendencies.manage';

    -- 2. Cria Estrutura de Menu (se não existir)
    PRINT '2. Verificando e criando itens de menu...';
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'atividades')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path) VALUES ('atividades', 'Atividades', 'clipboard', 30, NULL, NULL);
    SELECT @menu_atividades = id FROM [core].[menu_items] WHERE name = 'atividades';

    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'minhas_atividades')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path) VALUES ('minhas_atividades', 'Minhas Atividades', 'list', 1, @menu_atividades, '/admin/activities');
    SELECT @menu_minhas_atividades = id FROM [core].[menu_items] WHERE name = 'minhas_atividades';

    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'nova_atividade')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path) VALUES ('nova_atividade', 'Nova Atividade', 'plus-circle', 2, @menu_atividades, '/admin/activities/new');
    SELECT @menu_nova_atividade = id FROM [core].[menu_items] WHERE name = 'nova_atividade';

    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'board_pendencias')
        INSERT INTO [core].[menu_items] (name, label, icon, display_order, parent_id, path) VALUES ('board_pendencias', 'Board de Pendências', 'layout-grid', 3, @menu_atividades, '/admin/pendencies');
    SELECT @menu_board_pendencias = id FROM [core].[menu_items] WHERE name = 'board_pendencias';

    -- 3. Associa Permissões aos Menus (se não existir)
    PRINT '3. Verificando e associando permissões aos menus...';
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] WHERE menu_item_id = @menu_minhas_atividades AND permission_id = @perm_activities_view)
        INSERT INTO [core].[menu_item_permissions] (menu_item_id, permission_id) VALUES (@menu_minhas_atividades, @perm_activities_view);

    IF NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] WHERE menu_item_id = @menu_nova_atividade AND permission_id = @perm_activities_create)
        INSERT INTO [core].[menu_item_permissions] (menu_item_id, permission_id) VALUES (@menu_nova_atividade, @perm_activities_create);

    IF NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] WHERE menu_item_id = @menu_board_pendencias AND permission_id = @perm_pendencies_view)
        INSERT INTO [core].[menu_item_permissions] (menu_item_id, permission_id) VALUES (@menu_board_pendencias, @perm_pendencies_view);

    -- 4. Associa Permissões ao Role Superuser (se não existir)
    PRINT '4. Verificando e associando permissões ao role Superuser...';
    IF @superuser_role_id IS NOT NULL
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_activities_view)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_activities_view);
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_activities_create)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_activities_create);
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_activities_update)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_activities_update);
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_pendencies_view)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_pendencies_view);
        IF NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @superuser_role_id AND permission_id = @perm_pendencies_manage)
            INSERT INTO [core].[role_permissions] (role_id, permission_id) VALUES (@superuser_role_id, @perm_pendencies_manage);
    END

    PRINT 'Script concluído com sucesso.';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    -- Lança o erro original
    DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
    DECLARE @ErrorState INT = ERROR_STATE();
    RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);

    PRINT 'Ocorreu um erro. A transação foi revertida.';
END CATCH;
GO
