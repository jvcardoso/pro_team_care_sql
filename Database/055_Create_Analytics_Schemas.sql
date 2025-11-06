-- Descrição: Cria os schemas [analytics] e [reports] para organizar os objetos de BI.
-- Data: 2025-11-05
-- Autor: Gemini

-- O uso de schemas é uma boa prática para separar logicamente os objetos do banco de dados,
-- facilitando a gestão de permissões e a organização do projeto.

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'analytics')
BEGIN
    EXEC('CREATE SCHEMA [analytics]');
    PRINT 'Schema [analytics] criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Schema [analytics] já existe.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'reports')
BEGIN
    EXEC('CREATE SCHEMA [reports]');
    PRINT 'Schema [reports] criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Schema [reports] já existe.';
END
GO
