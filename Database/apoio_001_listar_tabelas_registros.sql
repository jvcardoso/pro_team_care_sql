USE pro_team_care;
GO

-- Esta consulta busca a contagem de linhas diretamente dos metadados do SQL Server.
-- É a maneira mais performática de obter essa informação.
SELECT
    s.name AS [Schema],
    t.name AS [Tabela],
    p.rows AS [Quantidade_De_Registros]
FROM
    sys.tables AS t
INNER JOIN
    sys.schemas AS s ON t.schema_id = s.schema_id
INNER JOIN
    sys.partitions AS p ON t.object_id = p.object_id
WHERE
    s.name = 'core' -- Filtra apenas pelo nosso schema
    AND p.index_id IN (0, 1) -- 0=Tabela Heap (sem índice clusterizado), 1=Índice Clusterizado (dados da tabela)
ORDER BY
    t.name;