-- =============================================
-- Script: 051_Add_AIAnalysis_To_MovementImages.sql
-- Descrição: Adiciona coluna AIAnalysis à tabela MovementImages
-- Data: 2025-01-04
-- =============================================

USE [pro_team_care]
GO

-- Adicionar coluna AIAnalysis
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('core.MovementImages')
    AND name = 'AIAnalysis'
)
BEGIN
    ALTER TABLE core.MovementImages
    ADD AIAnalysis NVARCHAR(2000) NULL;

    PRINT '✅ Coluna AIAnalysis adicionada à tabela core.MovementImages';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna AIAnalysis já existe na tabela core.MovementImages';
END

-- Adicionar comentário à coluna
IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('core.MovementImages')
    AND name = 'AIAnalysis'
)
BEGIN
    EXEC sp_addextendedproperty
        @name = N'MS_Description',
        @value = N'Análise gerada pela IA sobre a imagem anexada ao movimento',
        @level0type = N'SCHEMA',
        @level0name = N'core',
        @level1type = N'TABLE',
        @level1name = N'MovementImages',
        @level2type = N'COLUMN',
        @level2name = N'AIAnalysis';
END

PRINT '✅ Script 051_Add_AIAnalysis_To_MovementImages.sql executado com sucesso';