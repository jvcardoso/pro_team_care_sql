-- =================================================================================
-- Script:         026_Create_Phase2_Tables.sql
-- Descrição:      Cria as tabelas necessárias para as funcionalidades da Fase 2:
--                 - Sessões Seguras (user_sessions)
--                 - Notificações (notifications)
--                 - Menus Dinâmicos (menu_items, menu_item_permissions)
-- Autor:          DBA
-- Data:           22/10/2025
-- Banco:          pro_team_care
-- Schema:         core
-- =================================================================================

USE pro_team_care;
GO

BEGIN TRANSACTION;
BEGIN TRY

    PRINT '🚀 Iniciando criação das tabelas da Fase 2...';
    PRINT '';

    -- =============================================================================
    -- TABELA: user_sessions
    -- Descrição: Rastreia sessões ativas de usuários via JTI (JWT ID)
    --            Permite invalidação de tokens e auditoria de personificação
    -- =============================================================================
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'user_sessions' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[user_sessions] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [user_id] BIGINT NOT NULL,
            [jti] NVARCHAR(255) NOT NULL, -- 'JWT ID', o identificador único do token
            [impersonator_user_id] BIGINT NULL, -- Se houver, quem está personificando este usuário
            [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
            [expires_at] DATETIME2 NOT NULL,
            CONSTRAINT FK_user_sessions_user FOREIGN KEY (user_id) REFERENCES [core].[users](id) ON DELETE CASCADE,
            CONSTRAINT FK_user_sessions_impersonator FOREIGN KEY (impersonator_user_id) REFERENCES [core].[users](id)
        );
        
        -- Índices para performance
        CREATE INDEX IX_user_sessions_jti ON [core].[user_sessions](jti);
        CREATE INDEX IX_user_sessions_user_id ON [core].[user_sessions](user_id);
        CREATE INDEX IX_user_sessions_expires_at ON [core].[user_sessions](expires_at);
        
        PRINT '✅ Tabela [core].[user_sessions] criada com sucesso.';
    END
    ELSE
    BEGIN
        PRINT '⚠️  Tabela [core].[user_sessions] já existe.';
    END

    PRINT '';

    -- =============================================================================
    -- TABELA: notifications
    -- Descrição: Sistema de notificações in-app para usuários
    --            Suporta tipos (info, warning, success, error) e soft delete
    -- =============================================================================
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'notifications' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[notifications] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [user_id] BIGINT NOT NULL, -- O destinatário da notificação
            [type] NVARCHAR(20) NOT NULL, -- 'info', 'warning', 'success', 'error'
            [title] NVARCHAR(200) NOT NULL,
            [message] NVARCHAR(MAX) NOT NULL,
            [link] NVARCHAR(500) NULL, -- Link para a entidade relacionada (ex: /patients/123)
            [is_read] BIT NOT NULL DEFAULT 0,
            [read_at] DATETIME2 NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
            [deleted_at] DATETIME2 NULL,
            CONSTRAINT FK_notifications_user FOREIGN KEY (user_id) REFERENCES [core].[users](id) ON DELETE CASCADE,
            CONSTRAINT CHK_notifications_type CHECK (type IN ('info', 'warning', 'success', 'error'))
        );
        
        -- Índices para performance (filtrado por deleted_at)
        CREATE INDEX IX_notifications_user_id ON [core].[notifications](user_id) WHERE deleted_at IS NULL;
        CREATE INDEX IX_notifications_is_read ON [core].[notifications](is_read) WHERE deleted_at IS NULL;
        CREATE INDEX IX_notifications_created_at ON [core].[notifications](created_at DESC) WHERE deleted_at IS NULL;
        
        PRINT '✅ Tabela [core].[notifications] criada com sucesso.';
    END
    ELSE
    BEGIN
        PRINT '⚠️  Tabela [core].[notifications] já existe.';
    END

    PRINT '';

    -- =============================================================================
    -- TABELA: menu_items
    -- Descrição: Itens de menu dinâmicos com suporte a hierarquia (parent_id)
    --            Integra com sistema de permissões via menu_item_permissions
    -- =============================================================================
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'menu_items' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[menu_items] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [parent_id] BIGINT NULL, -- Para criar hierarquia (submenus)
            [name] NVARCHAR(100) NOT NULL UNIQUE,
            [label] NVARCHAR(200) NOT NULL,
            [icon] NVARCHAR(50) NULL,
            [path] NVARCHAR(500) NULL,
            [display_order] INT NOT NULL DEFAULT 0,
            [is_active] BIT NOT NULL DEFAULT 1,
            [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
            [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
            [deleted_at] DATETIME2 NULL,
            CONSTRAINT FK_menu_items_parent FOREIGN KEY (parent_id) REFERENCES [core].[menu_items](id)
        );
        
        -- Índices para performance
        CREATE INDEX IX_menu_items_parent_id ON [core].[menu_items](parent_id) WHERE deleted_at IS NULL;
        CREATE INDEX IX_menu_items_display_order ON [core].[menu_items](display_order) WHERE deleted_at IS NULL;
        CREATE INDEX IX_menu_items_is_active ON [core].[menu_items](is_active) WHERE deleted_at IS NULL;
        
        PRINT '✅ Tabela [core].[menu_items] criada com sucesso.';
    END
    ELSE
    BEGIN
        PRINT '⚠️  Tabela [core].[menu_items] já existe.';
    END

    PRINT '';

    -- =============================================================================
    -- TABELA: menu_item_permissions
    -- Descrição: Relacionamento N:N entre menu_items e permissions
    --            Define quais permissões são necessárias para ver cada menu
    -- =============================================================================
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'menu_item_permissions' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[menu_item_permissions] (
            [menu_item_id] BIGINT NOT NULL,
            [permission_id] BIGINT NOT NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
            CONSTRAINT PK_menu_item_permissions PRIMARY KEY (menu_item_id, permission_id),
            CONSTRAINT FK_menu_item_permissions_menu FOREIGN KEY (menu_item_id) REFERENCES [core].[menu_items](id) ON DELETE CASCADE,
            CONSTRAINT FK_menu_item_permissions_permission FOREIGN KEY (permission_id) REFERENCES [core].[permissions](id) ON DELETE CASCADE
        );
        
        -- Índices para queries reversas
        CREATE INDEX IX_menu_item_permissions_permission_id ON [core].[menu_item_permissions](permission_id);
        
        PRINT '✅ Tabela [core].[menu_item_permissions] criada com sucesso.';
    END
    ELSE
    BEGIN
        PRINT '⚠️  Tabela [core].[menu_item_permissions] já existe.';
    END

    PRINT '';
    PRINT '═══════════════════════════════════════════════════════════════════════════';
    PRINT '✅ Script 026_Create_Phase2_Tables.sql executado com SUCESSO!';
    PRINT '═══════════════════════════════════════════════════════════════════════════';
    PRINT '';
    PRINT '📊 Tabelas criadas:';
    PRINT '   1. [core].[user_sessions] - Sessões ativas e personificação';
    PRINT '   2. [core].[notifications] - Notificações in-app';
    PRINT '   3. [core].[menu_items] - Menus dinâmicos com hierarquia';
    PRINT '   4. [core].[menu_item_permissions] - Permissões de menus';
    PRINT '';
    PRINT '🚀 Próximo passo: Inserir menus padrão do sistema';
    PRINT '';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    
    PRINT '';
    PRINT '═══════════════════════════════════════════════════════════════════════════';
    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    PRINT '═══════════════════════════════════════════════════════════════════════════';
    PRINT '';
    PRINT 'Detalhes do erro:';
    PRINT '   Mensagem: ' + ERROR_MESSAGE();
    PRINT '   Linha: ' + CAST(ERROR_LINE() AS NVARCHAR(10));
    PRINT '   Procedure: ' + ISNULL(ERROR_PROCEDURE(), 'N/A');
    PRINT '';
    
    THROW;
END CATCH
GO
