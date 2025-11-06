-- =============================================
-- Script: 053_Alter_AIAnalysis_Column_Size.sql
-- Descrição: Aumenta o tamanho da coluna AIAnalysis de NVARCHAR(2000) para NVARCHAR(MAX)
-- Autor: Sistema
-- Data: 2025-11-04
-- Versão: 1.0
-- =============================================

USE [pro_team_care]
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT 'Iniciando script 053_Alter_AIAnalysis_Column_Size.sql...';

    -- 1. Verificar tamanho atual da coluna
    PRINT 'Verificando tamanho atual da coluna [AIAnalysis]...';
    
    DECLARE @current_size INT;
    
    SELECT @current_size = CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'core'
      AND TABLE_NAME = 'MovementImages'
      AND COLUMN_NAME = 'AIAnalysis';
    
    PRINT ' -> Tamanho atual: ' + ISNULL(CAST(@current_size AS NVARCHAR(10)), 'MAX');

    -- 2. Alterar coluna para NVARCHAR(MAX)
    IF @current_size IS NOT NULL AND @current_size < 4000
    BEGIN
        PRINT 'Alterando coluna [AIAnalysis] para NVARCHAR(MAX)...';
        
        ALTER TABLE core.MovementImages
        ALTER COLUMN AIAnalysis NVARCHAR(MAX) NULL;
        
        PRINT ' -> ✅ Coluna [AIAnalysis] alterada para NVARCHAR(MAX).';
        PRINT ' -> ✅ Agora suporta análises de IA com até 2GB de texto.';
    END
    ELSE IF @current_size IS NULL
    BEGIN
        PRINT ' -> ⚠️ Coluna [AIAnalysis] já é NVARCHAR(MAX).';
    END
    ELSE
    BEGIN
        PRINT ' -> ⚠️ Coluna [AIAnalysis] já tem tamanho adequado (' + CAST(@current_size AS NVARCHAR(10)) + ').';
    END

    -- 3. Verificar tamanho após alteração
    PRINT '';
    PRINT 'Verificando tamanho após alteração...';
    
    SELECT @current_size = CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'core'
      AND TABLE_NAME = 'MovementImages'
      AND COLUMN_NAME = 'AIAnalysis';
    
    PRINT ' -> Tamanho final: ' + ISNULL(CAST(@current_size AS NVARCHAR(10)), 'MAX');

    COMMIT TRANSACTION;
    PRINT '';
    PRINT '✅ Script executado com sucesso e transação commitada.';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '';
    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    PRINT 'Mensagem: ' + ERROR_MESSAGE();
    THROW;
END CATCH
GO

-- 4. Exibir informações da coluna
PRINT '';
PRINT '==============================================================================';
PRINT 'Informações da coluna [AIAnalysis]:';
PRINT '==============================================================================';

SELECT 
    COLUMN_NAME AS 'Coluna',
    DATA_TYPE AS 'Tipo',
    CASE 
        WHEN CHARACTER_MAXIMUM_LENGTH = -1 THEN 'MAX'
        ELSE CAST(CHARACTER_MAXIMUM_LENGTH AS NVARCHAR(10))
    END AS 'Tamanho',
    IS_NULLABLE AS 'Permite NULL'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'core'
  AND TABLE_NAME = 'MovementImages'
  AND COLUMN_NAME = 'AIAnalysis';
GO
