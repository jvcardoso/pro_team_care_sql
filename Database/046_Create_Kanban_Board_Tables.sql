/*
==============================================================================
Script: 046_Create_Kanban_Board_Tables.sql
Descrição: Cria estrutura completa do sistema Kanban Board
Autor: Cascade AI + Juliano (Revisado e Corrigido por Gemini)
Data: 2025-11-03
Versão: 1.2 (Correção final: Remoção de GO de dentro do TRY/CATCH)
==============================================================================
*/

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '========================================';
    PRINT 'Iniciando criação das tabelas Kanban Board';
    PRINT '========================================';

    -- Tabela 1: [core].CardColumns
    PRINT '1. Criando tabela [core].CardColumns...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'CardColumns' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[CardColumns] (
            [ColumnID] INT IDENTITY(1,1) NOT NULL,
            [CompanyID] BIGINT NOT NULL,
            [ColumnName] NVARCHAR(100) NOT NULL,
            [DisplayOrder] INT NOT NULL DEFAULT 0,
            [Color] NVARCHAR(20) NULL,
            [IsActive] BIT NOT NULL DEFAULT 1,
            [CreatedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            CONSTRAINT [PK_CardColumns] PRIMARY KEY CLUSTERED ([ColumnID] ASC),
            CONSTRAINT [FK_CardColumns_Companies] FOREIGN KEY ([CompanyID]) REFERENCES [core].[companies]([id])
        );
        CREATE NONCLUSTERED INDEX [IX_CardColumns_CompanyID] ON [core].[CardColumns] ([CompanyID], [DisplayOrder]);
        PRINT ' -> Tabela [core].CardColumns criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].CardColumns já existe.';

    -- Tabela 2: [core].Cards
    PRINT '2. Criando tabela [core].Cards...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Cards' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[Cards] (
            [CardID] INT IDENTITY(1,1) NOT NULL,
            [CompanyID] BIGINT NOT NULL,
            [UserID] BIGINT NOT NULL,
            [ColumnID] INT NOT NULL,
            [Title] NVARCHAR(255) NOT NULL,
            [Description] NVARCHAR(MAX) NULL,
            [OriginalText] NVARCHAR(MAX) NULL,
            [SubStatus] NVARCHAR(50) NULL,
            [Priority] NVARCHAR(20) NULL DEFAULT 'Média',
            [StartDate] DATETIME2(7) NULL,
            [DueDate] DATETIME2(7) NULL,
            [CompletedDate] DATETIME2(7) NULL,
            [CreatedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            [IsDeleted] BIT NOT NULL DEFAULT 0,
            [DeletedAt] DATETIME2(7) NULL,
            CONSTRAINT [PK_Cards] PRIMARY KEY CLUSTERED ([CardID] ASC),
            CONSTRAINT [FK_Cards_Companies] FOREIGN KEY ([CompanyID]) REFERENCES [core].[companies]([id]),
            CONSTRAINT [FK_Cards_Users] FOREIGN KEY ([UserID]) REFERENCES [core].[users]([id]),
            CONSTRAINT [FK_Cards_CardColumns] FOREIGN KEY ([ColumnID]) REFERENCES [core].[CardColumns]([ColumnID])
        );
        CREATE NONCLUSTERED INDEX [IX_Cards_CompanyID_ColumnID] ON [core].[Cards] ([CompanyID], [ColumnID]) WHERE [IsDeleted] = 0;
        CREATE NONCLUSTERED INDEX [IX_Cards_UserID] ON [core].[Cards] ([UserID]);
        PRINT ' -> Tabela [core].Cards criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].Cards já existe.';

    -- Tabela 3: [core].CardMovements
    PRINT '3. Criando tabela [core].CardMovements...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'CardMovements' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[CardMovements] (
            [MovementID] INT IDENTITY(1,1) NOT NULL,
            [CardID] INT NOT NULL,
            [UserID] BIGINT NOT NULL,
            [LogDate] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            [Subject] NVARCHAR(255) NOT NULL,
            [Description] NVARCHAR(MAX) NULL,
            [TimeSpent] INT NULL,
            [MovementType] NVARCHAR(50) NULL,
            [OldColumnID] INT NULL,
            [NewColumnID] INT NULL,
            [OldSubStatus] NVARCHAR(50) NULL,
            [NewSubStatus] NVARCHAR(50) NULL,
            CONSTRAINT [PK_CardMovements] PRIMARY KEY CLUSTERED ([MovementID] ASC),
            CONSTRAINT [FK_CardMovements_Cards] FOREIGN KEY ([CardID]) REFERENCES [core].[Cards]([CardID]) ON DELETE CASCADE,
            CONSTRAINT [FK_CardMovements_Users] FOREIGN KEY ([UserID]) REFERENCES [core].[users]([id])
        );
        CREATE NONCLUSTERED INDEX [IX_CardMovements_CardID] ON [core].[CardMovements] ([CardID], [LogDate] DESC);
        PRINT ' -> Tabela [core].CardMovements criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].CardMovements já existe.';

    -- Tabela 4: [core].CardAssignees
    PRINT '4. Criando tabela [core].CardAssignees...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'CardAssignees' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[CardAssignees] (
            [AssigneeID] INT IDENTITY(1,1) NOT NULL,
            [CardID] INT NOT NULL,
            [PersonName] NVARCHAR(255) NOT NULL,
            [PersonID] BIGINT NULL,
            [AssignedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            CONSTRAINT [PK_CardAssignees] PRIMARY KEY CLUSTERED ([AssigneeID] ASC),
            CONSTRAINT [FK_CardAssignees_Cards] FOREIGN KEY ([CardID]) REFERENCES [core].[Cards]([CardID]) ON DELETE CASCADE,
            CONSTRAINT [FK_CardAssignees_Persons] FOREIGN KEY ([PersonID]) REFERENCES [core].[people]([id])
        );
        CREATE NONCLUSTERED INDEX [IX_CardAssignees_CardID] ON [core].[CardAssignees] ([CardID]);
        PRINT ' -> Tabela [core].CardAssignees criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].CardAssignees já existe.';

    -- Tabela 5: [core].CardTags
    PRINT '5. Criando tabela [core].CardTags...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'CardTags' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[CardTags] (
            [CardTagID] INT IDENTITY(1,1) NOT NULL,
            [CardID] INT NOT NULL,
            [TagName] NVARCHAR(100) NOT NULL,
            [TagColor] NVARCHAR(20) NULL,
            [CreatedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            CONSTRAINT [PK_CardTags] PRIMARY KEY CLUSTERED ([CardTagID] ASC),
            CONSTRAINT [FK_CardTags_Cards] FOREIGN KEY ([CardID]) REFERENCES [core].[Cards]([CardID]) ON DELETE CASCADE
        );
        CREATE NONCLUSTERED INDEX [IX_CardTags_CardID] ON [core].[CardTags] ([CardID]);
        CREATE NONCLUSTERED INDEX [IX_CardTags_TagName] ON [core].[CardTags] ([TagName]);
        PRINT ' -> Tabela [core].CardTags criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].CardTags já existe.';

    -- Tabela 6: [core].CardImages
    PRINT '6. Criando tabela [core].CardImages...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'CardImages' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[CardImages] (
            [CardImageID] INT IDENTITY(1,1) NOT NULL,
            [CardID] INT NOT NULL,
            [ImagePath] NVARCHAR(512) NOT NULL,
            [ImageType] NVARCHAR(50) NULL,
            [Description] NVARCHAR(500) NULL,
            [UploadedBy] BIGINT NOT NULL,
            [UploadedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            CONSTRAINT [PK_CardImages] PRIMARY KEY CLUSTERED ([CardImageID] ASC),
            CONSTRAINT [FK_CardImages_Cards] FOREIGN KEY ([CardID]) REFERENCES [core].[Cards]([CardID]) ON DELETE CASCADE,
            CONSTRAINT [FK_CardImages_Users] FOREIGN KEY ([UploadedBy]) REFERENCES [core].[users]([id])
        );
        CREATE NONCLUSTERED INDEX [IX_CardImages_CardID] ON [core].[CardImages] ([CardID]);
        PRINT ' -> Tabela [core].CardImages criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].CardImages já existe.';

    -- Tabela 7: [core].MovementImages
    PRINT '7. Criando tabela [core].MovementImages...';
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'MovementImages' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        CREATE TABLE [core].[MovementImages] (
            [MovementImageID] INT IDENTITY(1,1) NOT NULL,
            [MovementID] INT NOT NULL,
            [ImagePath] NVARCHAR(512) NOT NULL,
            [ImageType] NVARCHAR(50) NULL,
            [Description] NVARCHAR(500) NULL,
            [UploadedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
            CONSTRAINT [PK_MovementImages] PRIMARY KEY CLUSTERED ([MovementImageID] ASC),
            CONSTRAINT [FK_MovementImages_CardMovements] FOREIGN KEY ([MovementID]) REFERENCES [core].[CardMovements]([MovementID]) ON DELETE CASCADE
        );
        CREATE NONCLUSTERED INDEX [IX_MovementImages_MovementID] ON [core].[MovementImages] ([MovementID]);
        PRINT ' -> Tabela [core].MovementImages criada.';
    END
    ELSE
        PRINT ' -> Tabela [core].MovementImages já existe.';

    -- VIEW: Tempo Total por Card
    PRINT '8. Criando view [core].[vw_CardTotalTime]...';
    IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_CardTotalTime' AND schema_id = SCHEMA_ID('core'))
    BEGIN
        EXEC('CREATE VIEW [core].[vw_CardTotalTime]
        AS
        SELECT 
            c.CardID,
            c.Title,
            c.CompanyID,
            ISNULL(SUM(cm.TimeSpent), 0) AS TotalTimeSpentMinutes,
            ISNULL(SUM(cm.TimeSpent), 0) / 60 AS TotalTimeSpentHours,
            COUNT(cm.MovementID) AS TotalMovements
        FROM [core].[Cards] c
        LEFT JOIN [core].[CardMovements] cm ON c.CardID = cm.CardID
        WHERE c.IsDeleted = 0
        GROUP BY c.CardID, c.Title, c.CompanyID;');
        PRINT ' -> View [core].[vw_CardTotalTime] criada.';
    END
    ELSE
        PRINT ' -> View [core].[vw_CardTotalTime] já existe.';

    -- Dados Iniciais: Colunas Padrão
    PRINT '9. Inserindo colunas padrão do board...';
    DECLARE @SystemCompanyID BIGINT = 1;
    IF NOT EXISTS (SELECT 1 FROM [core].[CardColumns] WHERE CompanyID = @SystemCompanyID)
    BEGIN
        INSERT INTO [core].[CardColumns] ([CompanyID], [ColumnName], [DisplayOrder], [Color])
        VALUES 
            (@SystemCompanyID, 'Backlog', 1, '#6B7280'),
            (@SystemCompanyID, 'A Fazer', 2, '#3B82F6'),
            (@SystemCompanyID, 'Em Andamento', 3, '#F59E0B'),
            (@SystemCompanyID, 'Revisão', 4, '#8B5CF6'),
            (@SystemCompanyID, 'Concluído', 5, '#10B981');
        PRINT ' -> Colunas padrão inseridas.';
    END
    ELSE
        PRINT ' -> Colunas padrão já existem para a CompanyID 1.';

    PRINT '========================================';
    PRINT '✅ SUCESSO: Estrutura Kanban Board criada!';
    PRINT '========================================';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    
    -- Lança o erro original para cima para que você possa ver a causa
    THROW;

END CATCH;
GO