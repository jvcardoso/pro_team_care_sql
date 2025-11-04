-- =================================================================================
-- Script:         insert_admin_user.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Claude Code
--
-- Descrição:
-- Insere usuário administrador padrão no sistema.
--
-- Email: admin@proteamcare.com.br
-- Senha: admin123
--
-- IMPORTANTE: Execute este script apenas uma vez após criar as tabelas.
-- =================================================================================

USE pro_team_care;
GO

BEGIN TRANSACTION;

BEGIN TRY
    -- =================================================================================
    -- 1. CRIAR USUÁRIO SUPER ADMIN DO SISTEMA
    -- =================================================================================
    -- Super Admin não está vinculado a nenhuma company específica.
    -- Ele tem acesso a TODAS as companies através do context_type='system'

    DECLARE @user_id BIGINT;

    -- Verificar se usuário já existe
    IF NOT EXISTS (SELECT 1 FROM [core].[users] WHERE email_address = 'admin@proteamcare.com.br')
    BEGIN
        INSERT INTO [core].[users] (
            email_address,
            password,
            person_id,
            company_id,
            establishment_id,
            is_active,
            is_system_admin,
            created_at,
            updated_at
        )
        VALUES (
            'admin@proteamcare.com.br',
            '$2b$12$s.0a0SfkOP61AI.mYS4kMOgGm4V8/aF9eCAhwDfTjx6dn0fzvcrZ.',  -- Hash de: admin123
            NULL,  -- Super Admin não vinculado a uma person
            NULL,  -- Super Admin NÃO vinculado a company (acesso a TODAS)
            NULL,  -- Não vinculado a estabelecimento
            1,     -- is_active = TRUE
            1,     -- is_system_admin = TRUE
            GETDATE(),
            GETDATE()
        );

        SET @user_id = SCOPE_IDENTITY();
        PRINT 'Usuário Super Admin criado com ID: ' + CAST(@user_id AS VARCHAR);
        PRINT 'IMPORTANTE: Super Admin tem acesso a TODAS as companies do sistema.';
    END
    ELSE
    BEGIN
        PRINT 'AVISO: Usuário admin@proteamcare.com.br já existe!';
        SELECT @user_id = id FROM [core].[users] WHERE email_address = 'admin@proteamcare.com.br';
        PRINT 'ID do usuário existente: ' + CAST(@user_id AS VARCHAR);
    END

    -- =================================================================================
    -- 2. CRIAR ROLE SUPER ADMIN (se não existir)
    -- =================================================================================
    DECLARE @role_id BIGINT;

    IF NOT EXISTS (SELECT 1 FROM [core].[roles] WHERE name = 'super_admin')
    BEGIN
        INSERT INTO [core].[roles] (
            name,
            display_name,
            level,
            context_type,
            is_system_role,
            created_at,
            updated_at
        )
        VALUES (
            'super_admin',
            'Super Administrador',
            0,  -- Nível mais alto
            'system',
            1,  -- Papel do sistema (não editável)
            GETDATE(),
            GETDATE()
        );

        SET @role_id = SCOPE_IDENTITY();
        PRINT 'Role super_admin criada com ID: ' + CAST(@role_id AS VARCHAR);
    END
    ELSE
    BEGIN
        SELECT @role_id = id FROM [core].[roles] WHERE name = 'super_admin';
        PRINT 'Role super_admin já existe com ID: ' + CAST(@role_id AS VARCHAR);
    END

    -- =================================================================================
    -- 3. ATRIBUIR ROLE AO USUÁRIO
    -- =================================================================================
    IF NOT EXISTS (
        SELECT 1 FROM [core].[user_roles]
        WHERE user_id = @user_id
          AND role_id = @role_id
          AND context_type = 'system'
    )
    BEGIN
        INSERT INTO [core].[user_roles] (
            user_id,
            role_id,
            context_type,
            context_id,
            status,
            assigned_by_user_id,
            created_at,
            updated_at
        )
        VALUES (
            @user_id,
            @role_id,
            'system',
            0,  -- Contexto de sistema usa 0 (coluna não aceita NULL)
            'active',
            @user_id,  -- Auto-atribuição na primeira vez
            GETDATE(),
            GETDATE()
        );

        PRINT 'Role atribuída ao usuário com sucesso!';
    END
    ELSE
    BEGIN
        PRINT 'Role já está atribuída ao usuário.';
    END

    -- =================================================================================
    -- COMMIT DA TRANSAÇÃO
    -- =================================================================================
    COMMIT TRANSACTION;

    PRINT '';
    PRINT '================================================================';
    PRINT 'SUPER ADMIN CRIADO COM SUCESSO!';
    PRINT '================================================================';
    PRINT '';
    PRINT 'CREDENCIAIS DE ACESSO:';
    PRINT '  Email:         admin@proteamcare.com.br';
    PRINT '  Senha:         admin123';
    PRINT '  User ID:       ' + CAST(@user_id AS VARCHAR);
    PRINT '  Role:          super_admin (ID: ' + CAST(@role_id AS VARCHAR) + ')';
    PRINT '';
    PRINT 'PERMISSÕES:';
    PRINT '  - Acesso em nível de SISTEMA (context_type = system)';
    PRINT '  - Acesso a TODAS as companies do sistema';
    PRINT '  - Sem vinculo a company específica (company_id = NULL)';
    PRINT '';
    PRINT '⚠️  IMPORTANTE: ';
    PRINT '  - Altere a senha após o primeiro login!';
    PRINT '  - Use este usuário APENAS para administração do sistema';
    PRINT '  - Crie usuários específicos para cada company';
    PRINT '================================================================';
    PRINT '';

END TRY
BEGIN CATCH
    -- Em caso de erro, desfaz toda a transação
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    -- Exibe informações do erro
    DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
    DECLARE @ErrorState INT = ERROR_STATE();

    PRINT '';
    PRINT '================================================================';
    PRINT '❌ ERRO AO CRIAR USUÁRIO ADMIN';
    PRINT '================================================================';
    PRINT 'Mensagem: ' + @ErrorMessage;
    PRINT 'Severity: ' + CAST(@ErrorSeverity AS VARCHAR);
    PRINT 'State:    ' + CAST(@ErrorState AS VARCHAR);
    PRINT '================================================================';
    PRINT '';

    -- Re-lança o erro
    RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
END CATCH;

GO
