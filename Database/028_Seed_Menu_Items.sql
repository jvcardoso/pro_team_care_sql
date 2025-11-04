-- =================================================================================
-- Script:         028_Seed_Menu_Items.sql (v1.2 - Sintaxe Corrigida)
-- Descrição:      v1.2 - Corrige um erro grave de sintaxe na associação de
--                 permissões, substituindo a lógica inválida por um padrão
--                 padrão com tabela temporária e loop WHILE.
-- =================================================================================

USE pro_team_care;
GO

BEGIN TRANSACTION;
BEGIN TRY

    PRINT '🚀 Iniciando população dos menus padrão...';
    PRINT '';

    -- PARTE 0: GARANTIR A EXISTÊNCIA DAS PERMISSÕES NECESSÁRIAS
    PRINT '🔗 Verificando e criando permissões faltantes...';
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'people.view') INSERT INTO [core].[permissions] (name, display_name, resource, action) VALUES ('people.view', 'Visualizar Pessoas', 'people', 'view');
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'establishments.view') INSERT INTO [core].[permissions] (name, display_name, resource, action) VALUES ('establishments.view', 'Visualizar Estabelecimentos', 'establishments', 'view');
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'roles.view') INSERT INTO [core].[permissions] (name, display_name, resource, action) VALUES ('roles.view', 'Visualizar Papéis', 'roles', 'view');
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'permissions.view') INSERT INTO [core].[permissions] (name, display_name, resource, action) VALUES ('permissions.view', 'Visualizar Permissões', 'permissions', 'view');
    IF NOT EXISTS (SELECT 1 FROM [core].[permissions] WHERE name = 'audit.view') INSERT INTO [core].[permissions] (name, display_name, resource, action) VALUES ('audit.view', 'Visualizar Auditoria', 'audit', 'view');
    PRINT '✅ Permissões verificadas/criadas.';
    PRINT '';

    -- PARTE 1 & 2: CRIAR MENUS E SUBMENUS (Lógica original mantida)
    PRINT 'NAV Criando menus e submenus...';
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'dashboard') INSERT INTO [core].[menu_items] (name, label, icon, path, display_order, is_active) VALUES ('dashboard', 'Dashboard', 'home', '/dashboard', 1, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'cadastros') INSERT INTO [core].[menu_items] (name, label, icon, path, display_order, is_active) VALUES ('cadastros', 'Cadastros', 'database', NULL, 2, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'seguranca') INSERT INTO [core].[menu_items] (name, label, icon, path, display_order, is_active) VALUES ('seguranca', 'Segurança', 'shield', NULL, 3, 1);

    DECLARE @cadastros_id BIGINT = (SELECT id FROM [core].[menu_items] WHERE name = 'cadastros');
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'pessoas') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@cadastros_id, 'pessoas', 'Pessoas', 'user', '/people', 1, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'usuarios') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@cadastros_id, 'usuarios', 'Usuários', 'users', '/users', 2, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'empresas') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@cadastros_id, 'empresas', 'Empresas', 'building', '/companies', 3, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'estabelecimentos') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@cadastros_id, 'estabelecimentos', 'Estabelecimentos', 'map-pin', '/establishments', 4, 1);

    DECLARE @seguranca_id BIGINT = (SELECT id FROM [core].[menu_items] WHERE name = 'seguranca');
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'roles') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@seguranca_id, 'roles', 'Roles', 'shield-check', '/roles', 1, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'permissoes') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@seguranca_id, 'permissoes', 'Permissões', 'key', '/permissions', 2, 1);
    IF NOT EXISTS (SELECT 1 FROM [core].[menu_items] WHERE name = 'logs_auditoria') INSERT INTO [core].[menu_items] (parent_id, name, label, icon, path, display_order, is_active) VALUES (@seguranca_id, 'logs_auditoria', 'Logs de Auditoria', 'file-text', '/audit-logs', 3, 1);
    PRINT '✅ Menus criados.';
    PRINT '';


    -- =============================================================================
    -- PARTE 3: ASSOCIAR PERMISSÕES AOS MENUS (Lógica Corrigida)
    -- =============================================================================
    PRINT '🔗 Associando permissões aos menus...';
    
    -- Declara uma tabela na memória para guardar os mapeamentos
    DECLARE @mappings TABLE (menu_name NVARCHAR(100), permission_name NVARCHAR(100));

    -- Insere todos os mapeamentos desejados na tabela temporária
    INSERT INTO @mappings (menu_name, permission_name) VALUES
    ('pessoas', 'people.view'),
    ('usuarios', 'users.view'),
    ('empresas', 'companies.view'),
    ('estabelecimentos', 'establishments.view'),
    ('roles', 'roles.view'),
    ('permissoes', 'permissions.view'),
    ('logs_auditoria', 'audit.view');

    -- Declara variáveis para o loop
    DECLARE @menuName NVARCHAR(100), @permissionName NVARCHAR(100);
    DECLARE @menuId BIGINT, @permissionId BIGINT;

    -- Loop para processar cada mapeamento da tabela temporária
    WHILE (SELECT COUNT(*) FROM @mappings) > 0
    BEGIN
        -- Pega o primeiro mapeamento da lista
        SELECT TOP 1 @menuName = menu_name, @permissionName = permission_name FROM @mappings;

        -- Busca os IDs correspondentes
        SET @menuId = (SELECT id FROM [core].[menu_items] WHERE name = @menuName);
        SET @permissionId = (SELECT id FROM [core].[permissions] WHERE name = @permissionName);

        -- Insere a associação se ela for válida e ainda não existir
        IF @menuId IS NOT NULL AND @permissionId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] WHERE menu_item_id = @menuId AND permission_id = @permissionId)
        BEGIN
            INSERT INTO [core].[menu_item_permissions] (menu_item_id, permission_id) VALUES (@menuId, @permissionId);
            PRINT '  -> Permissão "' + @permissionName + '" associada ao menu "' + @menuName + '".';
        END

        -- Remove o mapeamento processado da lista para o loop continuar
        DELETE FROM @mappings WHERE menu_name = @menuName;
    END

    COMMIT TRANSACTION;
    PRINT '✅ Script 028 (v1.2) executado com SUCESSO!';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    THROW;
END CATCH;
GO