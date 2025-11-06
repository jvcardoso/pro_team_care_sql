-- Descrição: Script para criar movimentos retroativos dos cards existentes
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0
-- Motivo: Cards foram criados diretamente nas colunas finais sem registrar movimentos

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando correção: Inserção de movimentos retroativos';
PRINT '================================================================================';

BEGIN TRANSACTION FixRetroactiveMovements;

BEGIN TRY

    -- 1. Identificar cards sem movimentos
    PRINT '1. Identificando cards sem movimentos...';

    IF OBJECT_ID('tempdb..#CardsWithoutMovements') IS NOT NULL
        DROP TABLE #CardsWithoutMovements;

    SELECT
        c.CardID,
        c.CompanyID,
        c.UserID,
        c.ColumnID,
        c.CreatedAt,
        cc.ColumnName
    INTO #CardsWithoutMovements
    FROM core.Cards c
    LEFT JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
    WHERE c.IsDeleted = 0
      AND c.CompanyID = 1  -- Foco na empresa que tem dados
      AND NOT EXISTS (
          SELECT 1 FROM core.CardMovements cm
          WHERE cm.CardID = c.CardID
      );

    DECLARE @CardsToFix INT = (SELECT COUNT(*) FROM #CardsWithoutMovements);
    PRINT '   • Cards sem movimentos encontrados: ' + CAST(@CardsToFix AS VARCHAR(10));

    -- 2. Obter ID da coluna Backlog
    DECLARE @BacklogColumnID INT = (
        SELECT ColumnID FROM core.CardColumns
        WHERE CompanyID = 1 AND ColumnName = 'Backlog'
    );

    IF @BacklogColumnID IS NULL
    BEGIN
        PRINT '   ❌ ERRO: Coluna Backlog não encontrada!';
        THROW 50001, 'Coluna Backlog não existe', 1;
    END

    PRINT '   • ID da coluna Backlog: ' + CAST(@BacklogColumnID AS VARCHAR(10));

    -- 3. Inserir movimento inicial (criação no Backlog)
    PRINT '2. Inserindo movimentos iniciais (Backlog)...';

    INSERT INTO core.CardMovements (
        CardID,
        UserID,
        LogDate,
        Subject,
        Description,
        OldColumnID,
        NewColumnID
    )
    SELECT
        CardID,
        UserID,
        DATEADD(MINUTE, -5, CreatedAt), -- 5 minutos antes da criação
        'Card criado no Backlog',
        'Movimento retroativo: card criado diretamente na coluna ' + ColumnName,
        NULL, -- OldColumnID (criação)
        @BacklogColumnID -- NewColumnID (Backlog)
    FROM #CardsWithoutMovements;

    DECLARE @MovementsCreated INT = @@ROWCOUNT;
    PRINT '   • Movimentos iniciais criados: ' + CAST(@MovementsCreated AS VARCHAR(10));

    -- 4. Inserir movimento para a coluna atual (se diferente de Backlog)
    PRINT '3. Inserindo movimentos para coluna atual...';

    INSERT INTO core.CardMovements (
        CardID,
        UserID,
        LogDate,
        Subject,
        Description,
        OldColumnID,
        NewColumnID
    )
    SELECT
        CardID,
        UserID,
        CreatedAt, -- No momento da criação
        'Movido para ' + ColumnName,
        'Movimento retroativo: card movido da criação para coluna atual',
        @BacklogColumnID, -- OldColumnID (Backlog)
        ColumnID -- NewColumnID (coluna atual)
    FROM #CardsWithoutMovements
    WHERE ColumnID != @BacklogColumnID; -- Só se for diferente de Backlog

    DECLARE @CurrentMovementsCreated INT = @@ROWCOUNT;
    PRINT '   • Movimentos para coluna atual criados: ' + CAST(@CurrentMovementsCreated AS VARCHAR(10));

    -- 5. Verificar resultados
    PRINT '4. Verificando correção...';

    SELECT
        'Cards corrigidos' as Tipo,
        COUNT(*) as Quantidade
    FROM #CardsWithoutMovements

    UNION ALL

    SELECT
        'Movimentos criados' as Tipo,
        COUNT(*) as Quantidade
    FROM core.CardMovements cm
    WHERE EXISTS (
        SELECT 1 FROM #CardsWithoutMovements cwm
        WHERE cwm.CardID = cm.CardID
    )

    UNION ALL

    SELECT
        'Cards com movimentos agora' as Tipo,
        COUNT(DISTINCT c.CardID) as Quantidade
    FROM core.Cards c
    INNER JOIN core.CardMovements cm ON c.CardID = cm.CardID
    WHERE c.CompanyID = 1 AND c.IsDeleted = 0;

    -- 6. Limpar tabela temporária
    DROP TABLE #CardsWithoutMovements;

    PRINT '================================================================================';
    PRINT '✅ SUCESSO: Movimentos retroativos criados!';
    PRINT '   • Cards corrigidos: ' + CAST(@CardsToFix AS VARCHAR(10));
    PRINT '   • Movimentos criados: ' + CAST((@MovementsCreated + @CurrentMovementsCreated) AS VARCHAR(10));
    PRINT '';
    PRINT '🎯 Sistema de BI agora pode analisar todos os cards!';
    PRINT '================================================================================';

    COMMIT TRANSACTION FixRetroactiveMovements;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION FixRetroactiveMovements;

    PRINT '❌ ERRO durante a correção:';
    PRINT ERROR_MESSAGE();

    -- Limpar tabela temporária se existir
    IF OBJECT_ID('tempdb..#CardsWithoutMovements') IS NOT NULL
        DROP TABLE #CardsWithoutMovements;

    THROW;
END CATCH;

GO