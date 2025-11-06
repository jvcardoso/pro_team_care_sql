-- =============================================
-- Script: 051_Add_AIAnalysis_To_MovementImages_v2.sql
-- Descrição: Adiciona/Altera a coluna AIAnalysis na tabela MovementImages e exibe a estrutura final.
-- Autor: Gemini
-- Data: 2025-11-04
-- Versão: 2.0
-- =============================================

USE [pro_team_care]
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT 'Iniciando script 051_Add_AIAnalysis_To_MovementImages_v2.sql...';

    -- 1. Adicionar coluna AIAnalysis se não existir
    PRINT 'Verificando a existência da coluna [AIAnalysis]...';
    IF NOT EXISTS (
        SELECT 1
        FROM sys.columns
        WHERE object_id = OBJECT_ID('core.MovementImages')
        AND name = 'AIAnalysis'
    )
    BEGIN
        ALTER TABLE core.MovementImages
        ADD AIAnalysis NVARCHAR(2000) NULL;

        PRINT ' -> ✅ Coluna [AIAnalysis] adicionada à tabela core.MovementImages.';
    END
    ELSE
    BEGIN
        PRINT ' -> ⚠️ Coluna [AIAnalysis] já existe na tabela core.MovementImages.';
    END

    -- 2. Adicionar ou Atualizar o comentário (Extended Property) da coluna
    PRINT 'Verificando a descrição da coluna [AIAnalysis]...';
    DECLARE @description NVARCHAR(200) = N'Análise gerada pela IA sobre a imagem anexada ao movimento';
    DECLARE @prop_exists BIT = 0;

    -- Verifica se a propriedade já existe
    IF EXISTS (
        SELECT 1
        FROM sys.extended_properties
        WHERE major_id = OBJECT_ID('core.MovementImages')
          AND minor_id = (SELECT column_id FROM sys.columns WHERE object_id = OBJECT_ID('core.MovementImages') AND name = 'AIAnalysis')
          AND name = N'MS_Description'
    )
    BEGIN
        SET @prop_exists = 1;
    END

    IF @prop_exists = 1
    BEGIN
        -- Atualiza a propriedade se ela já existe
        EXEC sp_updateextendedproperty
            @name = N'MS_Description',
            @value = @description,
            @level0type = N'SCHEMA', @level0name = N'core',
            @level1type = N'TABLE',  @level1name = N'MovementImages',
            @level2type = N'COLUMN', @level2name = N'AIAnalysis';
        PRINT ' -> ✅ Descrição da coluna [AIAnalysis] atualizada.';
    END
    ELSE
    BEGIN
        -- Adiciona a propriedade se ela não existe
        EXEC sp_addextendedproperty
            @name = N'MS_Description',
            @value = @description,
            @level0type = N'SCHEMA', @level0name = N'core',
            @level1type = N'TABLE',  @level1name = N'MovementImages',
            @level2type = N'COLUMN', @level2name = N'AIAnalysis';
        PRINT ' -> ✅ Descrição da coluna [AIAnalysis] criada.';
    END

    COMMIT TRANSACTION;
    PRINT 'Script executado com sucesso e transação commitada.';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    THROW;
END CATCH
GO

-- 3. Exibir a estrutura final da tabela para verificação
PRINT '
==============================================================================';
PRINT 'Exibindo a estrutura final da tabela [core].[MovementImages]...';
PRINT '==============================================================================';
EXEC sp_help '[core].[MovementImages]';
GO
