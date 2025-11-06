-- Script temporário para corrigir DisplayOrder
-- Permitir NULL temporariamente para testar

ALTER TABLE core.Cards ALTER COLUMN DisplayOrder INT NULL;

-- Adicionar valor padrão para registros existentes
UPDATE core.Cards SET DisplayOrder = 1 WHERE DisplayOrder IS NULL;

-- Voltar a não permitir NULL
ALTER TABLE core.Cards ALTER COLUMN DisplayOrder INT NOT NULL;