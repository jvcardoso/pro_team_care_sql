-- Verificar se as tabelas existem no banco
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'core'
ORDER BY TABLE_NAME;

-- Verificar estrutura das tabelas que podem não existir
SELECT 'phones' as table_name, COUNT(*) as record_count FROM [core].[phones] WITH (NOLOCK)
UNION ALL
SELECT 'emails' as table_name, COUNT(*) as record_count FROM [core].[emails] WITH (NOLOCK)
UNION ALL
SELECT 'addresses' as table_name, COUNT(*) as record_count FROM [core].[addresses] WITH (NOLOCK);