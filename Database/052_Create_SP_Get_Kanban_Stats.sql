/*
==============================================================================
Script: 052_Create_SP_Get_Kanban_Stats.sql
Descrição: Cria a Stored Procedure para buscar estatísticas do Kanban Board.
Autor: Gemini
Data: 2025-11-04
Versão: 1.0
==============================================================================
*/

USE [pro_team_care];
GO

PRINT '==============================================================================';
PRINT 'Criando Stored Procedure [core].[sp_get_kanban_statistics]...';
PRINT '==============================================================================';
GO

IF OBJECT_ID('[core].[sp_get_kanban_statistics]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [core].[sp_get_kanban_statistics];
    PRINT ' -> Stored Procedure [core].[sp_get_kanban_statistics] existente removida.';
END
GO

CREATE PROCEDURE [core].[sp_get_kanban_statistics]
    @CompanyID BIGINT
AS
BEGIN
    -- Impede a contagem de linhas e mensagens "done" para não interferir com o resultado
    SET NOCOUNT ON;

    -- Validação de Parâmetros
    IF @CompanyID IS NULL
    BEGIN
        PRINT 'Erro: O parâmetro @CompanyID não pode ser nulo.';
        THROW 50001, 'O CompanyID é obrigatório.', 1;
        RETURN;
    END

    -- Lógica principal usando contagem condicional para eficiência
    SELECT
        -- 1. Total de Cards: Conta todos os cards não deletados da empresa
        COUNT(c.CardID) AS TotalCards,

        -- 2. Em Andamento: Conta cards na coluna "Em Andamento"
        COUNT(CASE WHEN cc.ColumnName = 'Em Andamento' THEN c.CardID END) AS InProgressCards,

        -- 3. Concluídos: Conta cards na coluna "Concluído"
        COUNT(CASE WHEN cc.ColumnName = 'Concluído' THEN c.CardID END) AS CompletedCards

    FROM
        [core].[Cards] c
    INNER JOIN
        [core].[CardColumns] cc ON c.ColumnID = cc.ColumnID AND c.CompanyID = cc.CompanyID
    WHERE
        c.CompanyID = @CompanyID
        AND c.IsDeleted = 0;

END
GO

PRINT '✅ SUCESSO: Stored Procedure [core].[sp_get_kanban_statistics] criada.';
GO
