-- Teste da importação BusinessMap

USE [pro_team_care];
GO

-- 1. Verificar se a SP existe
IF OBJECT_ID('[core].[sp_UpsertCardFromImport]', 'P') IS NOT NULL
    PRINT '✅ SP [core].[sp_UpsertCardFromImport] existe'
ELSE
    PRINT '❌ SP [core].[sp_UpsertCardFromImport] NÃO existe'

-- 2. Teste da SP com dados de exemplo
DECLARE @CardID BIGINT;
DECLARE @Action VARCHAR(10);

EXEC [core].[sp_UpsertCardFromImport]
    @ExternalCardID = 'TEST-001',
    @Title = '[TESTE] Card de Importação',
    @OwnerName = 'admin',
    @Deadline = '2025-12-01',
    @Priority = 'High',
    @ColumnName = 'Backlog',
    @Description = 'Card criado para teste de importação',
    @ActualEndDate = NULL,
    @LastEndDate = NULL,
    @LastStartDate = NULL,
    @PlannedStart = NULL,
    @CardURL = 'https://businessmap.com/test',
    @LastComment = 'Teste de importação realizado',
    @CompanyID = 1,
    @DefaultUserID = 1;

PRINT '✅ Teste da SP executado'

-- 3. Verificar se o card foi criado
SELECT TOP 1
    CardID,
    Title,
    ExternalCardID,
    CreatedAt
FROM core.Cards
WHERE ExternalCardID = 'TEST-001'
ORDER BY CreatedAt DESC;

-- 4. Verificar estatísticas atuais
SELECT
    'Total de cards' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = 1 AND IsDeleted = 0
UNION ALL
SELECT
    'Cards com ExternalCardID' AS Tipo,
    COUNT(*) AS Quantidade
FROM core.Cards
WHERE CompanyID = 1 AND IsDeleted = 0 AND ExternalCardID IS NOT NULL;