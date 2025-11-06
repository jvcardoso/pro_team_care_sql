 -- =========================================================================================
 -- Script:         050_Add_Card_Display_Order.sql
 -- Descrição:      Adiciona campo DisplayOrder para ordenar cards dentro das colunas
 -- Versão:         1.3 (Correção final com SQL Dinâmico para garantir a execução)
 -- =========================================================================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY

    -- Passo 1: Adicionar a coluna como NULA.
    PRINT '1. Verificando e adicionando a coluna DisplayOrder como NULLABLE...';
    IF NOT EXISTS (
        SELECT 1
        FROM sys.columns
        WHERE object_id = OBJECT_ID('core.Cards')
        AND name = 'DisplayOrder'
    )
    BEGIN
        ALTER TABLE [core].[Cards]
        ADD DisplayOrder INT NULL;
        PRINT '   -> Coluna DisplayOrder adicionada com sucesso!';
    END
    ELSE
    BEGIN
        PRINT '   -> Coluna DisplayOrder já existe.';
    END

    -- Passo 2: Preencher os valores usando SQL Dinâmico.
    PRINT '2. Inicializando valores de DisplayOrder para cards existentes...';

    DECLARE @SqlUpdate NVARCHAR(MAX);
    SET @SqlUpdate = N'
    WITH OrderedCards AS (
        SELECT
            CardID,
            ROW_NUMBER() OVER (PARTITION BY ColumnID ORDER BY CreatedAt) AS RowNum
        FROM [core].[Cards]
    )
    UPDATE c
    SET DisplayOrder = oc.RowNum
    FROM [core].[Cards] c
    INNER JOIN OrderedCards oc ON c.CardID = oc.CardID
    WHERE c.DisplayOrder IS NULL;';

    EXEC sp_executesql @SqlUpdate;

    PRINT '   -> Valores inicializados com sucesso!';

    -- Passo 3: Tornar a coluna obrigatória (NOT NULL) usando SQL Dinâmico.
    PRINT '3. Tornando coluna DisplayOrder obrigatória...';

    DECLARE @SqlAlter NVARCHAR(MAX);
    SET @SqlAlter = N'
    ALTER TABLE [core].[Cards]
    ALTER COLUMN DisplayOrder INT NOT NULL;';

    EXEC sp_executesql @SqlAlter;

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
