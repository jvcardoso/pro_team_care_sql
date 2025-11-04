-- =========================================================================================
-- Script:         050_Add_Card_Display_Order.sql
-- Descrição:      Adiciona campo DisplayOrder para ordenar cards dentro das colunas
-- Versão:         1.0
-- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    PRINT '1. Verificando se coluna DisplayOrder existe na tabela Cards...';

    IF NOT EXISTS (
        SELECT 1 
        FROM sys.columns 
        WHERE object_id = OBJECT_ID('core.Cards') 
        AND name = 'DisplayOrder'
    )
    BEGIN
        PRINT '   -> Adicionando coluna DisplayOrder...';
        
        ALTER TABLE [core].[Cards]
        ADD DisplayOrder INT NULL;
        
        PRINT '   -> Coluna DisplayOrder adicionada com sucesso!';
    END
    ELSE
    BEGIN
        PRINT '   -> Coluna DisplayOrder já existe.';
    END

    PRINT '2. Inicializando valores de DisplayOrder para cards existentes...';

    -- Atualizar cards existentes com ordem baseada na data de criação
    WITH OrderedCards AS (
        SELECT 
            CardID,
            ROW_NUMBER() OVER (PARTITION BY ColumnID ORDER BY CreatedAt) AS RowNum
        FROM [core].[Cards]
        WHERE DisplayOrder IS NULL
    )
    UPDATE c
    SET DisplayOrder = oc.RowNum
    FROM [core].[Cards] c
    INNER JOIN OrderedCards oc ON c.CardID = oc.CardID;

    PRINT '   -> Valores inicializados com sucesso!';

    PRINT '3. Tornando coluna DisplayOrder obrigatória...';

    ALTER TABLE [core].[Cards]
    ALTER COLUMN DisplayOrder INT NOT NULL;

    PRINT '   -> Coluna DisplayOrder agora é obrigatória!';

    PRINT '✅ Campo de ordenação adicionado com sucesso!';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    PRINT 'Mensagem de erro: ' + ERROR_MESSAGE();
    THROW;

END CATCH;
GO

-- Verificação final
PRINT ''
PRINT 'Verificando estrutura da tabela Cards:'
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'core' 
AND TABLE_NAME = 'Cards'
AND COLUMN_NAME = 'DisplayOrder';
GO

PRINT ''
PRINT 'Exemplo de cards ordenados por coluna:'
SELECT TOP 10
    c.CardID,
    c.Title,
    col.ColumnName,
    c.DisplayOrder,
    c.CreatedAt
FROM [core].[Cards] c
INNER JOIN [core].[CardColumns] col ON c.ColumnID = col.ColumnID
WHERE c.IsDeleted = 0
ORDER BY c.ColumnID, c.DisplayOrder;
GO
