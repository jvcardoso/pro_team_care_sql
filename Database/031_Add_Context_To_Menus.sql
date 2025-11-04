-- =================================================================================
-- Script:         031_Add_Context_To_Menus.sql
-- Descrição:      Adiciona a coluna [context_type] à tabela [menu_items] para
--                 permitir a exibição de menus específicos por contexto de usuário.
-- =================================================================================
USE pro_team_care;
GO

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name = N'context_type' AND Object_ID = Object_ID(N'core.menu_items'))
BEGIN
    ALTER TABLE [core].[menu_items]
    ADD context_type NVARCHAR(50) NULL; -- Permite NULL para menus comuns

    -- Opcional: Adicionar uma CHECK constraint para valores válidos
    -- ALTER TABLE [core].[menu_items]
    -- ADD CONSTRAINT CHK_menu_items_context CHECK (context_type IN ('system', 'company', 'establishment', 'professional', 'patient', 'client'));

    PRINT '✅ Coluna [context_type] adicionada à tabela [core].[menu_items].';
END
ELSE
BEGIN
    PRINT 'ℹ️ Coluna [context_type] já existe em [core].[menu_items].';
END
GO