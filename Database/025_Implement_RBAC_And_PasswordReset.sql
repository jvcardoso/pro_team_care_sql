-- =================================================================================
-- Script:         025_Implement_RBAC_And_PasswordReset.sql (v1.1 - Corrigido)
-- Descrição:      v1.1 - Corrige erros de sintaxe (remoção do GO dentro do TRY/CATCH)
--                 e de lógica (referência a coluna inexistente na VIEW).
-- =================================================================================
USE pro_team_care;
GO

-- A transação e o TRY/CATCH começam aqui e só terminam no final do script.
BEGIN TRANSACTION;
BEGIN TRY

    -- PARTE 1: ADICIONAR CAMPOS DE PASSWORD RESET NA TABELA USERS
    PRINT '1. Adicionando campos de Password Reset à tabela [users]...';
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[core].[users]') AND name = 'password_reset_token')
    BEGIN
        ALTER TABLE [core].[users] ADD
            password_reset_token NVARCHAR(255) NULL,
            password_reset_expires_at DATETIME2 NULL;
    END;

    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[core].[users]') AND name = 'password_changed_at')
    BEGIN
        ALTER TABLE [core].[users] ADD password_changed_at DATETIME2 NULL;
    END;

    -- PARTE 2: CRIAR TABELAS DE PERMISSÕES (RBAC)
    PRINT '2. Criando as tabelas para o sistema de Permissões (RBAC)...';
    -- Tabela: permissions
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'permissions' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[permissions] (
            id BIGINT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(100) NOT NULL UNIQUE, display_name NVARCHAR(100) NOT NULL,
            description NVARCHAR(500) NULL, resource NVARCHAR(50) NOT NULL, action NVARCHAR(50) NOT NULL,
            created_at DATETIME2 NOT NULL DEFAULT GETDATE()
        );
        PRINT '  -> Tabela [core].[permissions] criada.';
    END;

    -- Tabela: role_permissions (relacionamento N:N)
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'role_permissions' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[role_permissions] (
            id BIGINT IDENTITY(1,1) PRIMARY KEY, role_id BIGINT NOT NULL, permission_id BIGINT NOT NULL,
            created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
            CONSTRAINT FK_role_permissions_role FOREIGN KEY (role_id) REFERENCES [core].[roles](id) ON DELETE CASCADE,
            CONSTRAINT FK_role_permissions_permission FOREIGN KEY (permission_id) REFERENCES [core].[permissions](id) ON DELETE CASCADE,
            CONSTRAINT UQ_role_permissions UNIQUE (role_id, permission_id)
        );
        PRINT '  -> Tabela [core].[role_permissions] criada.';
    END;

    -- PARTE 3: ATUALIZAR TABELAS EXISTENTES DE ROLES
    PRINT '3. Adicionando coluna [deleted_at] às tabelas de roles...';
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[core].[user_roles]') AND name = 'deleted_at')
        ALTER TABLE [core].[user_roles] ADD deleted_at DATETIME2 NULL;
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[core].[roles]') AND name = 'deleted_at')
        ALTER TABLE [core].[roles] ADD deleted_at DATETIME2 NULL;

    -- PARTE 4: INSERIR DADOS INICIAIS DE PERMISSÕES E ASSOCIAR
    PRINT '4. Inserindo permissões básicas e associando ao papel [system_admin]...';
    MERGE INTO [core].[permissions] AS Target
    USING (VALUES
        ('users.view', 'Visualizar Usuários', 'users', 'view'), ('users.create', 'Criar Usuários', 'users', 'create'), ('users.update', 'Atualizar Usuários', 'users', 'update'), ('users.delete', 'Deletar Usuários', 'users', 'delete'),
        ('companies.view', 'Visualizar Empresas', 'companies', 'view'), ('companies.create', 'Criar Empresas', 'companies', 'create'), ('companies.update', 'Atualizar Empresas', 'companies', 'update'), ('companies.delete', 'Deletar Empresas', 'companies', 'delete')
    ) AS Source (name, display_name, resource, action)
    ON Target.name = Source.name
    WHEN NOT MATCHED THEN
        INSERT (name, display_name, description, resource, action)
        VALUES (Source.name, Source.display_name, 'Permissão para ' + Source.display_name, Source.resource, Source.action);

    DECLARE @system_admin_role_id BIGINT = (SELECT id FROM [core].[roles] WHERE name = 'system_admin');
    IF @system_admin_role_id IS NOT NULL
    BEGIN
        INSERT INTO [core].[role_permissions] (role_id, permission_id)
        SELECT @system_admin_role_id, p.id
        FROM [core].[permissions] p
        WHERE NOT EXISTS (SELECT 1 FROM [core].[role_permissions] WHERE role_id = @system_admin_role_id AND permission_id = p.id);
    END;

    -- PARTE 5: CRIAR VIEW AUXILIAR
    PRINT '5. Criando view auxiliar [vw_users_with_roles]...';
    -- A view é criada com CREATE OR ALTER, então é seguro executá-la
    -- Primeiro, o DROP para garantir que a recriação funcione em um lote
    IF OBJECT_ID('[core].[vw_users_with_roles]', 'V') IS NOT NULL
        DROP VIEW [core].[vw_users_with_roles];

    -- A recriação da view deve estar em seu próprio comando após o DROP
    EXEC('
    CREATE VIEW [core].[vw_users_with_roles] AS
    SELECT
        u.id as user_id, u.email_address, u.is_active, u.is_system_admin,
        p.name as full_name,
        r.id as role_id, r.name as role_name, r.display_name as role_display_name, r.level as role_level,
        ur.context_type, ur.context_id, ur.status as role_status, ur.expires_at as role_expires_at
    FROM [core].[users] u
    LEFT JOIN [core].[people] p ON p.id = u.person_id -- CORREÇÃO: Removido "AND p.deleted_at IS NULL"
    LEFT JOIN [core].[user_roles] ur ON ur.user_id = u.id AND ur.deleted_at IS NULL
    LEFT JOIN [core].[roles] r ON r.id = ur.role_id AND r.deleted_at IS NULL
    WHERE u.deleted_at IS NULL;
    ');

    COMMIT TRANSACTION;
    PRINT '✅ Script de implementação da Fase 1 (v1.1) concluído com sucesso!';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    -- Lança o erro original para cima para que você possa ver a causa
    THROW;
END CATCH;
-- CORREÇÃO: O GO final fica FORA do bloco TRY/CATCH
GO