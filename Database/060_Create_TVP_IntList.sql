-- Descrição: Cria o tipo Table-Valued Parameter (TVP) [dbo].[IntList] para passar listas de inteiros.
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando criação do tipo Table-Valued Parameter [dbo].[IntList]';
PRINT '================================================================================';

-- Remove o tipo se ele já existir para garantir uma nova criação.
IF TYPE_ID(N'[dbo].[IntList]') IS NOT NULL
BEGIN
    DROP TYPE [dbo].[IntList];
    PRINT 'Tipo [dbo].[IntList] existente foi removido.';
END
GO

-- Cria o tipo que é, essencialmente, uma tabela com uma única coluna de inteiros.
-- Este tipo pode ser usado como parâmetro em stored procedures.
CREATE TYPE [dbo].[IntList] AS TABLE(
    [ID] INT NOT NULL PRIMARY KEY
);
GO

PRINT '================================================================================';
PRINT '✅ SUCESSO: Tipo [dbo].[IntList] criado.';
PRINT '================================================================================';
GO
