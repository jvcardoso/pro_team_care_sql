-- Script para verificar quais tabelas existem antes da limpeza
-- Execute este script para ver quais tabelas estão disponíveis

SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'core'
  AND TABLE_NAME IN (
    'lgpd_audit_log',
    'login_logs',
    'users',
    'phones',
    'emails',
    'addresses',
    'establishments',
    'pj_profiles',
    'pf_profiles',
    'people',
    'companies'
  )
ORDER BY TABLE_NAME;

-- Verificar constraints de chave estrangeira
SELECT
    fk.name AS FK_Name,
    tp.name AS Parent_Table,
    tr.name AS Referenced_Table,
    cp.name AS Parent_Column,
    cr.name AS Referenced_Column
FROM sys.foreign_keys fk
INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
INNER JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
WHERE tp.name IN ('companies', 'people', 'pj_profiles', 'pf_profiles', 'establishments', 'users')
   OR tr.name = 'companies'
ORDER BY tp.name, tr.name;