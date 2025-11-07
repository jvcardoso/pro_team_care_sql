-- Verificar quais stored procedures existem
SELECT
    SCHEMA_NAME(schema_id) + '.' + name as FullName,
    name,
    type_desc
FROM sys.objects
WHERE type = 'P'
    AND name LIKE '%UpsertCardFromImport%'
ORDER BY name;