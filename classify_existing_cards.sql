-- Classificar cards existentes com ITIL para teste
USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'CLASSIFICAÇÃO ITIL: Atualizando cards existentes para teste';
PRINT '================================================================================';

-- Atualizar alguns cards de exemplo com classificação ITIL
-- Baseado na lógica implementada na stored procedure

-- 1. Cards que parecem ser Changes (GMUD, RDM, Deploy)
UPDATE core.Cards
SET ITILCategory = 'Change',
    HasWindow = CASE WHEN Title LIKE '%Janela%' OR Title LIKE '%Window%' THEN 1 ELSE 0 END,
    HasCAB = CASE WHEN Title LIKE '%CAB%' OR Title LIKE '%Comit%' THEN 1 ELSE 0 END,
    HasBackout = CASE WHEN Title LIKE '%backout%' OR Title LIKE '%rollback%' THEN 1 ELSE 0 END,
    RiskLevel = CASE
        WHEN Title LIKE '%GMUD%' OR Title LIKE '%RDM%' OR Title LIKE '%Deploy%' THEN
            CASE
                WHEN (Title LIKE '%CAB%' OR Title LIKE '%Comit%') AND (Title LIKE '%backout%' OR Title LIKE '%rollback%') THEN 'Low'
                ELSE 'High'
            END
        ELSE 'Low'
    END,
    Size = 'M'
WHERE CardID IN (
    SELECT TOP 5 CardID
    FROM core.Cards
    WHERE (Title LIKE '%GMUD%' OR Title LIKE '%RDM%' OR Title LIKE '%Deploy%' OR Title LIKE '%CHG%')
    AND IsDeleted = 0
    AND ITILCategory IS NULL
);

PRINT '✅ 5 cards classificados como Change';

-- 2. Cards que parecem ser Incidents (Falha, Erro)
UPDATE core.Cards
SET ITILCategory = 'Incident',
    HasWindow = 0,
    HasCAB = 0,
    HasBackout = 0,
    RiskLevel = 'High',
    Size = 'S'
WHERE CardID IN (
    SELECT TOP 3 CardID
    FROM core.Cards
    WHERE (Title LIKE '%Falha%' OR Title LIKE '%Erro%' OR Title LIKE '%Incident%' OR Title LIKE '%Indispon%')
    AND IsDeleted = 0
    AND ITILCategory IS NULL
);

PRINT '✅ 3 cards classificados como Incident';

-- 3. Cards que parecem ser Service Requests (Solicitar, Criar, Acesso)
UPDATE core.Cards
SET ITILCategory = 'Service Request',
    HasWindow = 0,
    HasCAB = 0,
    HasBackout = 0,
    RiskLevel = 'Low',
    Size = 'S'
WHERE CardID IN (
    SELECT TOP 3 CardID
    FROM core.Cards
    WHERE (Title LIKE '%Solicit%' OR Title LIKE '%Criar%' OR Title LIKE '%Acesso%' OR Title LIKE '%Permiss%')
    AND IsDeleted = 0
    AND ITILCategory IS NULL
);

PRINT '✅ 3 cards classificados como Service Request';

-- 4. Resto como Operation Task
UPDATE core.Cards
SET ITILCategory = 'Operation Task',
    HasWindow = 0,
    HasCAB = 0,
    HasBackout = 0,
    RiskLevel = 'Low',
    Size = 'S'
WHERE ITILCategory IS NULL
AND IsDeleted = 0;

PRINT '✅ Cards restantes classificados como Operation Task';

-- Verificar resultado
SELECT
    ITILCategory,
    COUNT(*) as Quantidade,
    SUM(CASE WHEN RiskLevel = 'High' THEN 1 ELSE 0 END) as AltoRisco,
    SUM(CASE WHEN HasWindow = 1 THEN 1 ELSE 0 END) as ComJanela,
    SUM(CASE WHEN HasCAB = 1 THEN 1 ELSE 0 END) as ComCAB,
    SUM(CASE WHEN HasBackout = 1 THEN 1 ELSE 0 END) as ComBackout
FROM core.Cards
WHERE ITILCategory IS NOT NULL AND IsDeleted = 0
GROUP BY ITILCategory
ORDER BY Quantidade DESC;

PRINT '';
PRINT '================================================================================';
PRINT 'CLASSIFICAÇÃO CONCLUÍDA - Agora teste os endpoints!';
PRINT '================================================================================';