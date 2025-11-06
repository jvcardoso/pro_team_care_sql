-- Descrição: Adiciona a coluna ExternalCardID na tabela [core].[Cards] para suportar a importação.
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Adicionando coluna ExternalCardID à tabela [core].[Cards]';
PRINT '================================================================================';

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name = N'ExternalCardID' AND Object_ID = Object_ID(N'[core].[Cards]'))
BEGIN
    ALTER TABLE [core].[Cards] ADD ExternalCardID VARCHAR(50) NULL;
    PRINT '✅ Coluna [ExternalCardID] adicionada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Colunm [ExternalCardID] já existe.';
END
GO

-- Adiciona um índice na nova coluna para otimizar as buscas durante a importação
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE Name = 'IX_Cards_ExternalCardID' AND object_id = OBJECT_ID('[core].[Cards]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Cards_ExternalCardID] ON [core].[Cards]([ExternalCardID], [CompanyID]) WHERE [ExternalCardID] IS NOT NULL;
    PRINT '✅ Índice [IX_Cards_ExternalCardID] criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Índice [IX_Cards_ExternalCardID] já existe.';
END
GO
