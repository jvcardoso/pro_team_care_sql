-- Consulta para validar a estrutura do schema [core]
USE pro_team_care;
GO

SELECT
    t.name AS Tabela,
    c.name AS Coluna,
    UPPER(ty.name) +
        CASE
            WHEN ty.name IN ('nvarchar', 'varchar', 'char', 'nchar') THEN '(' + IIF(c.max_length = -1, 'MAX', CAST(c.max_length AS VARCHAR(10))) + ')'
            WHEN ty.name IN ('decimal', 'numeric') THEN '(' + CAST(c.precision AS VARCHAR(10)) + ',' + CAST(c.scale AS VARCHAR(10)) + ')'
            ELSE ''
        END AS Tipo_De_Dado,
    CASE WHEN c.is_nullable = 1 THEN 'Sim' ELSE 'Não' END AS Aceita_Nulo,
    ISNULL(ep.value, '') AS Descricao
FROM
    sys.schemas s
JOIN
    sys.tables t ON s.schema_id = t.schema_id
JOIN
    sys.columns c ON t.object_id = c.object_id
JOIN
    sys.types ty ON c.user_type_id = ty.user_type_id
LEFT JOIN
    sys.extended_properties ep ON t.object_id = ep.major_id AND c.column_id = ep.minor_id AND ep.name = 'MS_Description'
WHERE
    s.name = 'core'
ORDER BY
    t.name,
    c.column_id;