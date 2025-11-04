-- =================================================================================
-- Script:         032_Set_Initial_Menu_Contexts.sql
-- Descrição:      Define o contexto inicial para os menus padrão existentes.
--                 Menus sem contexto definido (NULL) são considerados comuns.
-- =================================================================================
USE pro_team_care;
GO

BEGIN TRANSACTION;

-- Define menus de Cadastros como 'system' (ajuste se necessário)
UPDATE [core].[menu_items] SET context_type = 'system'
WHERE name IN ('cadastros', 'pessoas', 'usuarios', 'empresas', 'estabelecimentos')
  AND context_type IS NULL;

-- Define menus de Segurança como 'system'
UPDATE [core].[menu_items] SET context_type = 'system'
WHERE name IN ('seguranca', 'roles', 'permissoes', 'logs_auditoria')
  AND context_type IS NULL;

-- Garante que o Dashboard seja comum (NULL)
UPDATE [core].[menu_items] SET context_type = NULL
WHERE name = 'dashboard';

COMMIT;
GO

PRINT '✅ Contextos iniciais definidos para os menus existentes.';

-- Verifica o resultado
SELECT name, label, context_type FROM [core].[menu_items] ORDER BY display_order;