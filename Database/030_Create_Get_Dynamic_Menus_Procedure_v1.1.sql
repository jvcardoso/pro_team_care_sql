-- =================================================================================
-- Script:         030_Create_Get_Dynamic_Menus_Procedure.sql (v1.1 - Com Contexto)
-- Descrição:      v1.1 - Modifica a procedure para filtrar menus também pelo
--                 [context_type] do usuário, além das permissões.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER PROCEDURE [core].[sp_get_dynamic_menus]
    @user_id_input BIGINT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @is_system_admin BIT = 0;
    DECLARE @user_exists BIT = 0;
    DECLARE @user_context_type NVARCHAR(50); -- Variável para o contexto do usuário

    -- Verifica se o usuário existe, se é admin E pega o context_type dele
    SELECT @user_exists = 1, @is_system_admin = is_system_admin, @user_context_type = context_type
    FROM [core].[users]
    WHERE id = @user_id_input AND is_active = 1 AND deleted_at IS NULL;

    IF @user_exists = 0 BEGIN THROW 50000, 'Usuário não encontrado ou inativo.', 1; RETURN; END

    -- Tabela temporária para guardar as permissões do usuário (lógica mantida)
    DECLARE @user_permissions TABLE (permission_name NVARCHAR(100) PRIMARY KEY);
    IF @is_system_admin = 1
        INSERT INTO @user_permissions (permission_name) SELECT name FROM [core].[permissions];
    ELSE
        INSERT INTO @user_permissions (permission_name) SELECT DISTINCT p.name FROM [core].[permissions] p JOIN [core].[role_permissions] rp ON rp.permission_id = p.id JOIN [core].[user_roles] ur ON ur.role_id = rp.role_id WHERE ur.user_id = @user_id_input AND ur.status = 'active' AND ur.deleted_at IS NULL;

    -- CTE Recursiva (Modificada para incluir filtro de contexto)
    WITH MenuHierarchy AS (
        SELECT
            mi.id, mi.parent_id, mi.name, mi.label, mi.icon, mi.path, mi.display_order,
            CAST(CASE
                WHEN (mi.context_type IS NULL OR mi.context_type = @user_context_type) -- FILTRO DE CONTEXTO
                 AND (NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip WHERE mip.menu_item_id = mi.id)
                      OR EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip JOIN [core].[permissions] p ON mip.permission_id = p.id WHERE mip.menu_item_id = mi.id AND p.name IN (SELECT permission_name FROM @user_permissions)))
                THEN 1 ELSE 0
            END AS BIT) AS is_visible,
            0 AS level
        FROM [core].[menu_items] mi
        WHERE mi.parent_id IS NULL AND mi.is_active = 1
          -- FILTRO DE CONTEXTO na âncora
          AND (mi.context_type IS NULL OR mi.context_type = @user_context_type)

        UNION ALL

        SELECT
            mi.id, mi.parent_id, mi.name, mi.label, mi.icon, mi.path, mi.display_order,
            CAST(CASE
                WHEN mh.is_visible = 1 -- Se o pai é visível E...
                 AND (mi.context_type IS NULL OR mi.context_type = @user_context_type) -- FILTRO DE CONTEXTO do filho E...
                 AND (NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip WHERE mip.menu_item_id = mi.id)
                      OR EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip JOIN [core].[permissions] p ON mip.permission_id = p.id WHERE mip.menu_item_id = mi.id AND p.name IN (SELECT permission_name FROM @user_permissions)))
                THEN 1 ELSE 0
            END AS BIT) AS is_visible,
            mh.level + 1 AS level
        FROM [core].[menu_items] mi
        INNER JOIN MenuHierarchy mh ON mi.parent_id = mh.id
        WHERE mi.is_active = 1
          -- FILTRO DE CONTEXTO na parte recursiva
          AND (mi.context_type IS NULL OR mi.context_type = @user_context_type)
    )
    SELECT id, parent_id, name, label, icon, path, display_order
    FROM MenuHierarchy
    WHERE is_visible = 1
    ORDER BY level, display_order;

END;
GO

PRINT '✅ Procedure [core].[sp_get_dynamic_menus] (v1.1) atualizada para incluir filtro de contexto.';