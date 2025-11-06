USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Adicionando colunas para classificação ITIL em core.Cards';
PRINT '================================================================================';

-- ITILCategory
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'ITILCategory')
BEGIN
    ALTER TABLE core.Cards ADD ITILCategory VARCHAR(30) NULL;
    PRINT '✅ Coluna ITILCategory adicionada';
END
ELSE
    PRINT '⚠️  Coluna ITILCategory já existe';

-- HasWindow
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'HasWindow')
BEGIN
    ALTER TABLE core.Cards ADD HasWindow BIT DEFAULT 0;
    PRINT '✅ Coluna HasWindow adicionada';
END
ELSE
    PRINT '⚠️  Coluna HasWindow já existe';

-- HasCAB
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'HasCAB')
BEGIN
    ALTER TABLE core.Cards ADD HasCAB BIT DEFAULT 0;
    PRINT '✅ Coluna HasCAB adicionada';
END
ELSE
    PRINT '⚠️  Coluna HasCAB já existe';

-- HasBackout
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'HasBackout')
BEGIN
    ALTER TABLE core.Cards ADD HasBackout BIT DEFAULT 0;
    PRINT '✅ Coluna HasBackout adicionada';
END
ELSE
    PRINT '⚠️  Coluna HasBackout já existe';

-- Size
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'Size')
BEGIN
    ALTER TABLE core.Cards ADD Size VARCHAR(20) NULL;
    PRINT '✅ Coluna Size adicionada';
END
ELSE
    PRINT '⚠️  Coluna Size já existe';

-- RiskLevel
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('core.Cards') AND name = 'RiskLevel')
BEGIN
    ALTER TABLE core.Cards ADD RiskLevel VARCHAR(20) NULL;
    PRINT '✅ Coluna RiskLevel adicionada';
END
ELSE
    PRINT '⚠️  Coluna RiskLevel já existe';

PRINT '================================================================================';
PRINT 'Colunas ITIL criadas com sucesso!';
PRINT '================================================================================';
GO