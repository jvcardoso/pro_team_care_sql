-- =============================================
-- Script: 061_Fix_Movement_Dates.sql
-- Descrição: Corrige as datas dos movimentos para usar CompletedDate real dos cards
-- Autor: Sistema
-- Data: 2025-11-05
-- Versão: 1.0
-- Problema: Movimentos retroativos criados com data atual ao invés da data real de conclusão
-- =============================================

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Corrigindo datas dos movimentos retroativos';
PRINT '================================================================================';

BEGIN TRANSACTION;

BEGIN TRY

    -- 1. Identificar movimentos com data incorreta (todos criados em 2025-11-05)
    PRINT '1. Identificando movimentos com data incorreta...';
    
    DECLARE @MovementsToFix INT = (
        SELECT COUNT(*)
        FROM core.CardMovements cm
        INNER JOIN core.Cards c ON cm.CardID = c.CardID
        WHERE c.CompanyID = 1
          AND CAST(cm.LogDate AS DATE) = '2025-11-05'
          AND c.CompletedDate IS NOT NULL
          AND CAST(c.CompletedDate AS DATE) != '2025-11-05'
    );
    
    PRINT '   • Movimentos a corrigir: ' + CAST(@MovementsToFix AS VARCHAR(10));

    -- 2. Atualizar movimentos de conclusão para usar a data real
    PRINT '2. Atualizando movimentos de conclusão...';
    
    UPDATE cm
    SET cm.LogDate = c.CompletedDate
    FROM core.CardMovements cm
    INNER JOIN core.Cards c ON cm.CardID = c.CardID
    WHERE c.CompanyID = 1
      AND cm.NewColumnID = 5  -- Coluna "Concluído"
      AND c.CompletedDate IS NOT NULL
      AND cm.LogDate != c.CompletedDate;
    
    DECLARE @MovementsUpdated INT = @@ROWCOUNT;
    PRINT '   • Movimentos de conclusão atualizados: ' + CAST(@MovementsUpdated AS VARCHAR(10));

    -- 3. Atualizar movimentos iniciais (Backlog) para usar CreatedAt
    PRINT '3. Atualizando movimentos iniciais (Backlog)...';
    
    UPDATE cm
    SET cm.LogDate = DATEADD(MINUTE, -5, c.CreatedAt)
    FROM core.CardMovements cm
    INNER JOIN core.Cards c ON cm.CardID = c.CardID
    WHERE c.CompanyID = 1
      AND cm.NewColumnID = 1  -- Coluna "Backlog"
      AND cm.OldColumnID IS NULL  -- Movimento de criação
      AND cm.LogDate != DATEADD(MINUTE, -5, c.CreatedAt);
    
    DECLARE @InitialMovementsUpdated INT = @@ROWCOUNT;
    PRINT '   • Movimentos iniciais atualizados: ' + CAST(@InitialMovementsUpdated AS VARCHAR(10));

    -- 4. Verificar resultado
    PRINT '4. Verificando correção...';
    
    SELECT 
        'Cards concluídos por mês' AS Tipo,
        YEAR(CompletedDate) AS Ano,
        MONTH(CompletedDate) AS Mes,
        COUNT(*) AS Quantidade
    FROM core.Cards
    WHERE CompanyID = 1
      AND IsDeleted = 0
      AND CompletedDate IS NOT NULL
    GROUP BY YEAR(CompletedDate), MONTH(CompletedDate)
    ORDER BY Ano DESC, Mes DESC;

    COMMIT TRANSACTION;
    
    PRINT '';
    PRINT '================================================================================';
    PRINT '✅ SUCESSO: Datas dos movimentos corrigidas!';
    PRINT '   • Movimentos de conclusão: ' + CAST(@MovementsUpdated AS VARCHAR(10));
    PRINT '   • Movimentos iniciais: ' + CAST(@InitialMovementsUpdated AS VARCHAR(10));
    PRINT '';
    PRINT '📊 Agora o dashboard mostrará as datas reais de conclusão!';
    PRINT '================================================================================';

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
