-- Teste dos dados ITIL implementados
USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'TESTE: Classificação ITIL - Status Atual';
PRINT '================================================================================';

-- 1. Verificar se as colunas ITIL existem na tabela Cards
PRINT '';
PRINT '1. Verificando colunas ITIL na tabela core.Cards:';
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'core'
    AND TABLE_NAME = 'Cards'
    AND COLUMN_NAME IN ('ITILCategory', 'HasWindow', 'HasCAB', 'HasBackout', 'Size', 'RiskLevel')
ORDER BY COLUMN_NAME;

-- 2. Verificar se a view vw_ITILReport existe
PRINT '';
PRINT '2. Verificando se a view analytics.vw_ITILReport existe:';
IF OBJECT_ID('analytics.vw_ITILReport', 'V') IS NOT NULL
    PRINT '✅ View analytics.vw_ITILReport existe'
ELSE
    PRINT '❌ View analytics.vw_ITILReport NÃO existe';

-- 3. Contar cards com classificação ITIL
PRINT '';
PRINT '3. Cards com classificação ITIL:';
SELECT
    COUNT(*) as TotalCardsClassificados
FROM core.Cards
WHERE ITILCategory IS NOT NULL AND IsDeleted = 0;

-- 4. Distribuição por categoria ITIL
PRINT '';
PRINT '4. Distribuição por categoria ITIL:';
SELECT
    ITILCategory,
    COUNT(*) as Quantidade,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as Percentual
FROM core.Cards
WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
GROUP BY ITILCategory
ORDER BY Quantidade DESC;

-- 5. Verificar metadados ITIL
PRINT '';
PRINT '5. Metadados ITIL (Window/CAB/Backout):';
SELECT
    SUM(CASE WHEN HasWindow = 1 THEN 1 ELSE 0 END) as ComJanela,
    SUM(CASE WHEN HasCAB = 1 THEN 1 ELSE 0 END) as ComCAB,
    SUM(CASE WHEN HasBackout = 1 THEN 1 ELSE 0 END) as ComBackout,
    SUM(CASE WHEN RiskLevel = 'High' THEN 1 ELSE 0 END) as AltoRisco
FROM core.Cards
WHERE ITILCategory IS NOT NULL AND IsDeleted = 0;

-- 6. Testar a view vw_ITILReport
PRINT '';
PRINT '6. Testando view analytics.vw_ITILReport:';
SELECT TOP 5
    CardID,
    ExternalCardID,
    Title,
    ITILCategory,
    RiskLevel,
    HasWindow,
    HasCAB,
    HasBackout,
    CompletedDate
FROM analytics.vw_ITILReport
WHERE CompletedDate >= '2025-01-01'
ORDER BY CompletedDate DESC;

PRINT '';
PRINT '================================================================================';
PRINT 'TESTE CONCLUÍDO';
PRINT '================================================================================';