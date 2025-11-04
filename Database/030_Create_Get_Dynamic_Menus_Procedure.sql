-- =================================================================================
-- Script:         030_Create_Get_Dynamic_Menus_Procedure.sql
-- Descrição:      Cria a procedure [sp_get_dynamic_menus] que retorna a lista
--                 hierárquica de menus visíveis para um usuário específico,
--                 baseado em suas permissões.
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

    -- Verifica se o usuário existe e se é admin
    SELECT @user_exists = 1, @is_system_admin = is_system_admin
    FROM [core].[users]
    WHERE id = @user_id_input AND is_active = 1 AND deleted_at IS NULL;

    IF @user_exists = 0
    BEGIN
        THROW 50000, 'Usuário não encontrado ou inativo.', 1;
        RETURN;
    END

    -- Tabela temporária para guardar as permissões do usuário
    DECLARE @user_permissions TABLE (permission_name NVARCHAR(100) PRIMARY KEY);

    -- Se for admin, carrega todas as permissões ativas
    IF @is_system_admin = 1
    BEGIN
        INSERT INTO @user_permissions (permission_name)
        SELECT name FROM [core].[permissions]; -- Admins veem todas
    END
    ELSE
    BEGIN
        -- Senão, carrega apenas as permissões associadas aos roles ativos do usuário
        INSERT INTO @user_permissions (permission_name)
        SELECT DISTINCT p.name
        FROM [core].[permissions] p
        INNER JOIN [core].[role_permissions] rp ON rp.permission_id = p.id
        INNER JOIN [core].[user_roles] ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = @user_id_input AND ur.status = 'active' AND ur.deleted_at IS NULL;
    END;

    -- CTE Recursiva para montar a hierarquia e verificar permissões
    WITH MenuHierarchy AS (
        -- Âncora: Menus raiz (sem pai)
        SELECT
            mi.id, mi.parent_id, mi.name, mi.label, mi.icon, mi.path, mi.display_order,
            -- Lógica de Visibilidade
            CAST(CASE
                -- Se o menu NÃO requer permissão OU o usuário TEM a permissão necessária
                WHEN NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip WHERE mip.menu_item_id = mi.id)
                  OR EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip
                             JOIN [core].[permissions] p ON mip.permission_id = p.id
                             WHERE mip.menu_item_id = mi.id AND p.name IN (SELECT permission_name FROM @user_permissions))
                THEN 1
                ELSE 0
            END AS BIT) AS is_visible,
            0 AS level -- Nível da hierarquia
        FROM [core].[menu_items] mi
        WHERE mi.parent_id IS NULL AND mi.is_active = 1

        UNION ALL

        -- Parte Recursiva: Busca os filhos dos menus já processados
        SELECT
            mi.id, mi.parent_id, mi.name, mi.label, mi.icon, mi.path, mi.display_order,
            -- Lógica de Visibilidade (Filho só é visível se o Pai for visível E ele mesmo for permitido)
            CAST(CASE
                WHEN mh.is_visible = 1 AND -- Se o pai é visível E...
                     (NOT EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip WHERE mip.menu_item_id = mi.id)
                      OR EXISTS (SELECT 1 FROM [core].[menu_item_permissions] mip
                                 JOIN [core].[permissions] p ON mip.permission_id = p.id
                                 WHERE mip.menu_item_id = mi.id AND p.name IN (SELECT permission_name FROM @user_permissions)))
                THEN 1
                ELSE 0
            END AS BIT) AS is_visible,
            mh.level + 1 AS level
        FROM [core].[menu_items] mi
        INNER JOIN MenuHierarchy mh ON mi.parent_id = mh.id -- Junta com o pai
        WHERE mi.is_active = 1
    )
    -- Seleciona o resultado final, apenas os menus visíveis, ordenados corretamente
    SELECT
        id, parent_id, name, label, icon, path, display_order
    FROM MenuHierarchy
    WHERE is_visible = 1
    ORDER BY level, display_order;

    -- Opcional: Retornar as permissões do usuário para debug na API, se necessário
    -- SELECT permission_name FROM @user_permissions ORDER BY permission_name;

END;
GO

PRINT '✅ Procedure [core].[sp_get_dynamic_menus] criada/alterada com sucesso.';