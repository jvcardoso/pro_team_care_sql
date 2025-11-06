-- ==============================================================================
-- Script: test_kanban_stats.sql
-- Descrição: Testa a stored procedure de estatísticas do Kanban
-- Autor: Sistema
-- Data: 2025-11-04
-- ==============================================================================

USE [pro_team_care];
GO

PRINT '==============================================================================';
PRINT 'TESTE DAS ESTATÍSTICAS DO KANBAN BOARD';
PRINT '==============================================================================';
GO

-- 1. VERIFICAR SE A STORED PROCEDURE EXISTE
IF OBJECT_ID('[core].[sp_get_kanban_statistics]', 'P') IS NOT NULL
BEGIN
    PRINT '✅ Stored Procedure [core].[sp_get_kanban_statistics] existe.';
END
ELSE
BEGIN
    PRINT '❌ Stored Procedure [core].[sp_get_kanban_statistics] NÃO existe!';
    RETURN;
END
GO

-- 2. VERIFICAR DADOS DIRETAMENTE NAS TABELAS
PRINT '';
PRINT '==============================================================================';
PRINT 'VERIFICAÇÃO DIRETA DOS DADOS NAS TABELAS';
PRINT '==============================================================================';

-- Total de cards não deletados
SELECT
    COUNT(c.CardID) AS TotalCards_Diretamente
FROM
    [core].[Cards] c
WHERE
    c.IsDeleted = 0;
-- AND c.CompanyID = 1; -- Descomente se quiser filtrar por empresa específica

-- Cards por coluna
SELECT
    cc.ColumnName,
    COUNT(c.CardID) AS Quantidade
FROM
    [core].[Cards] c
INNER JOIN
    [core].[CardColumns] cc ON c.ColumnID = cc.ColumnID AND c.CompanyID = cc.CompanyID
WHERE
    c.IsDeleted = 0
    -- AND c.CompanyID = 1; -- Descomente se quiser filtrar por empresa específica
GROUP BY
    cc.ColumnName
ORDER BY
    cc.DisplayOrder;

-- 3. EXECUTAR A STORED PROCEDURE
PRINT '';
PRINT '==============================================================================';
PRINT 'EXECUÇÃO DA STORED PROCEDURE';
PRINT '==============================================================================';

-- IMPORTANTE: Substitua o CompanyID pelo ID da empresa que você quer testar
DECLARE @TestCompanyID BIGINT = 1; -- Ajuste este valor conforme necessário

PRINT 'Executando sp_get_kanban_statistics para CompanyID = ' + CAST(@TestCompanyID AS VARCHAR(10));
PRINT '';

EXEC [core].[sp_get_kanban_statistics] @CompanyID = @TestCompanyID;
GO

-- 4. VERIFICAÇÃO DETALHADA POR EMPRESA
PRINT '';
PRINT '==============================================================================';
PRINT 'VERIFICAÇÃO DETALHADA POR EMPRESA';
PRINT '==============================================================================';

-- Listar todas as empresas com dados no kanban
SELECT DISTINCT
    c.CompanyID,
    comp.CompanyName,
    COUNT(c.CardID) AS TotalCards
FROM
    [core].[Cards] c
LEFT JOIN
    [dbo].[Companies] comp ON c.CompanyID = comp.CompanyID
WHERE
    c.IsDeleted = 0
GROUP BY
    c.CompanyID, comp.CompanyName
ORDER BY
    c.CompanyID;

-- 5. VERIFICAR COLUNAS DISPONÍVEIS
PRINT '';
PRINT '==============================================================================';
PRINT 'COLUNAS DISPONÍVEIS NO SISTEMA';
PRINT '==============================================================================';

SELECT
    ColumnID,
    ColumnName,
    DisplayOrder,
    IsActive,
    CompanyID
FROM
    [core].[CardColumns]
WHERE
    IsActive = 1
ORDER BY
    CompanyID, DisplayOrder;

PRINT '';
PRINT '==============================================================================';
PRINT 'TESTE CONCLUÍDO';
PRINT '==============================================================================';
GO