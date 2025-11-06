-- Descrição: Cria a view [analytics].[vw_CardFullHistory] para consolidar o histórico dos cards.
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando criação da View [analytics].[vw_CardFullHistory]';
PRINT '================================================================================';

-- Drop a view se ela já existir, para garantir que a nova versão seja criada.
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_CardFullHistory' AND schema_id = SCHEMA_ID('analytics'))
BEGIN
    DROP VIEW [analytics].[vw_CardFullHistory];
    PRINT 'View [analytics].[vw_CardFullHistory] existente foi removida.';
END
GO

CREATE VIEW [analytics].[vw_CardFullHistory]
AS
WITH CardMovementHistory AS (
     -- O CTE (Common Table Expression) abaixo é o coração da análise.
     -- Ele ordena todos os movimentos de cada card no tempo.
     SELECT
         m.MovementID,
         m.CardID,
         m.UserID AS MovedByUserID,
         m.LogDate AS MovementDate,
         m.OldColumnID,
         m.NewColumnID,
         -- A função LEAD() busca o valor da próxima linha dentro da partição do card.
         -- Isso nos permite saber quando o próximo movimento ocorreu.
         LEAD(m.LogDate, 1) OVER (PARTITION BY m.CardID ORDER BY m.LogDate) AS NextMovementDate
     FROM
         [core].[CardMovements] m
 )
 -- A consulta final junta os dados do card com o histórico de movimentos calculado.
 SELECT
     c.CardID,
     c.CompanyID,
     c.Title,
     c.Priority,
     c.DueDate,
     c.CreatedAt AS CardCreatedAt,
     c.IsDeleted,
     h.MovementID,
     h.MovedByUserID,
     h.MovementDate,
     h.NextMovementDate,
     h.OldColumnID,
     ISNULL(oc.ColumnName, 'Desconhecido') AS OldColumnName,
     h.NewColumnID,
     ISNULL(nc.ColumnName, 'Desconhecido') AS NewColumnName,
     -- Calcula a diferença em segundos entre o movimento atual e o próximo.
     -- Se for o último movimento (NextMovementDate IS NULL), o tempo gasto é 0.
     ISNULL(DATEDIFF(SECOND, h.MovementDate, h.NextMovementDate), 0) AS TimeInStageSeconds
 FROM
     [core].[Cards] c
 JOIN
     CardMovementHistory h ON c.CardID = h.CardID
 LEFT JOIN
     [core].[CardColumns] oc ON h.OldColumnID = oc.ColumnID
 LEFT JOIN
     [core].[CardColumns] nc ON h.NewColumnID = nc.ColumnID
 WHERE
     c.IsDeleted = 0;

GO

PRINT '================================================================================';
PRINT '✅ SUCESSO: View [analytics].[vw_CardFullHistory] criada.';
PRINT '================================================================================';
GO

-- Exemplo de como consultar a view para um card específico
/*
SELECT 
    CardID,
    MovementDate,
    OldColumnName,
    NewColumnName,
    TimeInStageSeconds,
    (TimeInStageSeconds / 60) AS TimeInStageMinutes,
    (TimeInStageSeconds / 3600) AS TimeInStageHours
FROM 
    [analytics].[vw_CardFullHistory]
WHERE 
    CardID = 123 -- Substitua pelo ID de um card existente
ORDER BY 
    MovementDate;
*/
