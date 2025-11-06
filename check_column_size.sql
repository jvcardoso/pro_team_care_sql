-- Verificar o tamanho da coluna AIAnalysis na tabela MovementImages
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    TABLE_NAME = 'MovementImages'
    AND COLUMN_NAME = 'AIAnalysis'
    AND TABLE_SCHEMA = 'core';