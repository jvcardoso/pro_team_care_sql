-- Teste direto da Stored Procedure

USE [pro_team_care];
GO

-- 1. Verificar se SP existe
IF OBJECT_ID('[core].[sp_UpsertCardFromImport]', 'P') IS NOT NULL
    PRINT '✅ SP existe'
ELSE
    PRINT '❌ SP NÃO existe'

-- 2. Teste simples da SP
DECLARE @Result TABLE (CardID BIGINT, Action VARCHAR(10));

INSERT INTO @Result
EXEC [core].[sp_UpsertCardFromImport]
    @ExternalCardID = 'TEST-SP-001',
    @Title = 'Teste SP Direto',
    @CompanyID = 1,
    @DefaultUserID = 1;

SELECT * FROM @Result;

-- 3. Verificar se card foi criado
SELECT CardID, Title, ExternalCardID, CreatedAt
FROM core.Cards
WHERE ExternalCardID = 'TEST-SP-001';

PRINT '✅ Teste concluído';