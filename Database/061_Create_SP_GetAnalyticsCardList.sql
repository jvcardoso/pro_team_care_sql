-- Descrição: Cria a SP [reports].[sp_GetAnalyticsCardList] para buscar a lista de cards para o dashboard.
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando criação da Stored Procedure [reports].[sp_GetAnalyticsCardList]';
PRINT '================================================================================';

IF OBJECT_ID('[reports].[sp_GetAnalyticsCardList]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [reports].[sp_GetAnalyticsCardList];
    PRINT 'Stored Procedure [reports].[sp_GetAnalyticsCardList] existente foi removida.';
END
GO

CREATE PROCEDURE [reports].[sp_GetAnalyticsCardList]
    @CompanyID BIGINT,
    @CompletedFrom DATE,
    @CompletedTo DATE,
    @ColumnIDs [dbo].[IntList] READONLY -- Nosso TVP para a lista de colunas
AS
BEGIN
    SET NOCOUNT ON;

    -- Declara uma variável para verificar se o filtro de colunas foi passado
    DECLARE @HasColumnFilter BIT;
    IF EXISTS (SELECT 1 FROM @ColumnIDs)
        SET @HasColumnFilter = 1;
    ELSE
        SET @HasColumnFilter = 0;

    -- A consulta principal busca os cards, aplicando os filtros de forma condicional.
    SELECT
        c.CardID,
        c.Title,
        c.Priority,
        c.CompletedDate,
        c.ColumnID,
        cc.ColumnName
    FROM
        [core].[Cards] c
    INNER JOIN
        [core].[CardColumns] cc ON c.ColumnID = cc.ColumnID
    WHERE
        c.CompanyID = @CompanyID
        AND c.IsDeleted = 0
        -- 1. Aplica o filtro por data de conclusão
        AND c.CompletedDate BETWEEN @CompletedFrom AND @CompletedTo
        -- 2. Aplica o filtro por colunas (se houver)
        AND (
            @HasColumnFilter = 0 OR -- Se não houver filtro de coluna, retorna tudo
            c.ColumnID IN (SELECT ID FROM @ColumnIDs) -- Se houver, filtra pela lista de IDs
        )
    ORDER BY
        c.CompletedDate DESC;

END;
GO

PRINT '================================================================================';
PRINT '✅ SUCESSO: Stored Procedure [reports].[sp_GetAnalyticsCardList] criada.';
PRINT '================================================================================';
GO

-- Exemplo de como executar a Stored Procedure
/*
-- 1. Declarar e popular o TVP com as colunas desejadas
DECLARE @MyColumns AS [dbo].[IntList];
INSERT INTO @MyColumns (ID) VALUES (4), (5); -- Ex: Filtrar por Revisão (ID 4) e Concluído (ID 5)

-- 2. Executar a SP com o filtro de colunas
EXEC [reports].[sp_GetAnalyticsCardList]
    @CompanyID = 1,
    @CompletedFrom = '2025-11-01',
    @CompletedTo = '2025-11-30',
    @ColumnIDs = @MyColumns;

-- 3. Executar a SP sem o filtro de colunas (passando uma tabela vazia)
DECLARE @EmptyColumns AS [dbo].[IntList];
EXEC [reports].[sp_GetAnalyticsCardList]
    @CompanyID = 1,
    @CompletedFrom = '2025-11-01',
    @CompletedTo = '2025-11-30',
    @ColumnIDs = @EmptyColumns;
*/
