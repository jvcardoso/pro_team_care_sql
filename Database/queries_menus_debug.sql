-- =========================================
-- QUERIES PARA DIAGNOSTICAR MENUS DINÂMICOS
-- =========================================

-- 1. VERIFICAR MENUS EXISTENTES E ATIVOS
SELECT
    mi.id,
    mi.parent_id,
    mi.name,
    mi.label,
    mi.icon,
    mi.path,
    mi.display_order,
    mi.is_active,
    mi.created_at,
    mi.updated_at
FROM [core].[menu_items] mi
WHERE mi.deleted_at IS NULL
  AND mi.is_active = 1
ORDER BY mi.display_order;

-- 2. VERIFICAR PERMISSÕES ASSOCIADAS AOS MENUS
SELECT
    mi.id AS menu_id,
    mi.name AS menu_name,
    mi.label AS menu_label,
    p.id AS permission_id,
    p.name AS permission_name,
    p.display_name AS permission_display_name,
    p.resource,
    p.action
FROM [core].[menu_items] mi
LEFT JOIN [core].[menu_item_permissions] mip ON mi.id = mip.menu_item_id
LEFT JOIN [core].[permissions] p ON mip.permission_id = p.id
WHERE mi.deleted_at IS NULL
  AND mi.is_active = 1
  AND p.deleted_at IS NULL
  AND p.is_active = 1
ORDER BY mi.display_order, p.resource, p.action;

-- 3. VERIFICAR PERMISSÕES DE UM USUÁRIO ESPECÍFICO (substitua ? pelo user_id)
-- Exemplo para user_id = 1
DECLARE @user_id BIGINT = 1; -- ALTERE PARA O ID DO USUÁRIO LOGADO

SELECT DISTINCT
    p.id,
    p.name,
    p.display_name,
    p.resource,
    p.action,
    CASE WHEN u.is_system_admin = 1 THEN 'SYSTEM_ADMIN' ELSE 'ROLE_BASED' END AS permission_source
FROM [core].[users] u
LEFT JOIN [core].[user_roles] ur ON u.id = ur.user_id AND ur.status = 'active' AND ur.deleted_at IS NULL
LEFT JOIN [core].[role_permissions] rp ON ur.role_id = rp.role_id
LEFT JOIN [core].[permissions] p ON rp.permission_id = p.id
WHERE u.id = @user_id
  AND u.deleted_at IS NULL
  AND u.is_active = 1
  AND p.is_active = 1
  AND p.deleted_at IS NULL
ORDER BY p.resource, p.action;

-- 4. VERIFICAR SE USUÁRIO É SYSTEM ADMIN
SELECT
    id,
    username,
    email,
    is_system_admin,
    is_active
FROM [core].[users]
WHERE id = @user_id; -- ALTERE PARA O ID DO USUÁRIO

-- 5. SIMULAR LÓGICA DE FILTRAGEM DE MENUS (PROCEDURE)
-- Esta procedure simula o que o backend faz para um usuário específico

CREATE OR ALTER PROCEDURE [core].[sp_get_dynamic_menus]
    @user_id BIGINT,
    @include_inactive BIT = 0
AS
BEGIN
    SET NOCOUNT ON;

    -- Verificar se usuário existe e está ativo
    IF NOT EXISTS (
        SELECT 1 FROM [core].[users]
        WHERE id = @user_id
          AND deleted_at IS NULL
          AND is_active = 1
    )
    BEGIN
        RAISERROR('Usuário não encontrado ou inativo', 16, 1);
        RETURN;
    END

    -- Obter permissões do usuário
    DECLARE @user_permissions TABLE (permission_name NVARCHAR(100));

    -- Se for system admin, incluir todas as permissões ativas
    IF EXISTS (SELECT 1 FROM [core].[users] WHERE id = @user_id AND is_system_admin = 1)
    BEGIN
        INSERT INTO @user_permissions (permission_name)
        SELECT name
        FROM [core].[permissions]
        WHERE is_active = 1
          AND deleted_at IS NULL;
    END
    ELSE
    BEGIN
        INSERT INTO @user_permissions (permission_name)
        SELECT DISTINCT p.name
        FROM [core].[permissions] p
        INNER JOIN [core].[role_permissions] rp ON rp.permission_id = p.id
        INNER JOIN [core].[user_roles] ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = @user_id
          AND ur.status = 'active'
          AND ur.deleted_at IS NULL
          AND p.is_active = 1
          AND p.deleted_at IS NULL;
    END

    -- Buscar menus visíveis
    WITH MenuHierarchy AS (
        SELECT
            mi.id,
            mi.parent_id,
            mi.name,
            mi.label,
            mi.icon,
            mi.path,
            mi.display_order,
            mi.is_active,
            mi.created_at,
            mi.updated_at,
            -- Verificar se menu é visível
            CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM [core].[menu_item_permissions] mip
                    WHERE mip.menu_item_id = mi.id
                ) THEN 1 -- Sem permissões = visível para todos
                WHEN EXISTS (
                    SELECT 1 FROM [core].[menu_item_permissions] mip
                    INNER JOIN [core].[permissions] p ON mip.permission_id = p.id
                    WHERE mip.menu_item_id = mi.id
                      AND p.name IN (SELECT permission_name FROM @user_permissions)
                ) THEN 1 -- Tem pelo menos uma permissão
                ELSE 0 -- Não tem permissões necessárias
            END AS is_visible,
            0 AS level,
            CAST(mi.id AS VARCHAR(MAX)) AS path_hierarchy
        FROM [core].[menu_items] mi
        WHERE mi.deleted_at IS NULL
          AND (mi.is_active = 1 OR @include_inactive = 1)
          AND mi.parent_id IS NULL -- Apenas raízes inicialmente

        UNION ALL

        SELECT
            mi.id,
            mi.parent_id,
            mi.name,
            mi.label,
            mi.icon,
            mi.path,
            mi.display_order,
            mi.is_active,
            mi.created_at,
            mi.updated_at,
            -- Para filhos, herdar visibilidade do pai se pai for visível
            CASE
                WHEN mh.is_visible = 1 THEN
                    CASE
                        WHEN NOT EXISTS (
                            SELECT 1 FROM [core].[menu_item_permissions] mip
                            WHERE mip.menu_item_id = mi.id
                        ) THEN 1 -- Sem permissões = visível
                        WHEN EXISTS (
                            SELECT 1 FROM [core].[menu_item_permissions] mip
                            INNER JOIN [core].[permissions] p ON mip.permission_id = p.id
                            WHERE mip.menu_item_id = mi.id
                              AND p.name IN (SELECT permission_name FROM @user_permissions)
                        ) THEN 1 -- Tem permissões
                        ELSE 0 -- Não tem permissões
                    END
                ELSE 0 -- Pai não visível
            END AS is_visible,
            mh.level + 1,
            CAST(mh.path_hierarchy + '/' + CAST(mi.id AS VARCHAR(20)) AS VARCHAR(MAX))
        FROM [core].[menu_items] mi
        INNER JOIN MenuHierarchy mh ON mi.parent_id = mh.id
        WHERE mi.deleted_at IS NULL
          AND (mi.is_active = 1 OR @include_inactive = 1)
    )
    SELECT
        id,
        parent_id,
        name,
        label,
        icon,
        path,
        display_order,
        is_active,
        created_at,
        updated_at,
        is_visible,
        level,
        path_hierarchy
    FROM MenuHierarchy
    WHERE is_visible = 1
    ORDER BY level, display_order;

    -- Retornar também as permissões do usuário para debug
    SELECT 'USER_PERMISSIONS' AS debug_info, permission_name
    FROM @user_permissions
    ORDER BY permission_name;

END
GO

-- 6. EXECUTAR A PROCEDURE PARA TESTAR (substitua o user_id)
-- EXEC [core].[sp_get_dynamic_menus] @user_id = 1, @include_inactive = 0;

-- 7. VERIFICAR SE HÁ MENUS SEM PERMISSÕES ASSOCIADAS (visíveis para todos)
SELECT
    mi.id,
    mi.name,
    mi.label,
    COUNT(mip.menu_item_id) AS permission_count
FROM [core].[menu_items] mi
LEFT JOIN [core].[menu_item_permissions] mip ON mi.id = mip.menu_item_id
WHERE mi.deleted_at IS NULL
  AND mi.is_active = 1
GROUP BY mi.id, mi.name, mi.label
HAVING COUNT(mip.menu_item_id) = 0
ORDER BY mi.display_order;

-- 8. VERIFICAR SE HÁ MENUS COM PERMISSÕES (precisam de autorização)
SELECT
    mi.id,
    mi.name,
    mi.label,
    STRING_AGG(p.name, ', ') AS required_permissions
FROM [core].[menu_items] mi
INNER JOIN [core].[menu_item_permissions] mip ON mi.id = mip.menu_item_id
INNER JOIN [core].[permissions] p ON mip.permission_id = p.id
WHERE mi.deleted_at IS NULL
  AND mi.is_active = 1
  AND p.deleted_at IS NULL
  AND p.is_active = 1
GROUP BY mi.id, mi.name, mi.label
ORDER BY mi.display_order;