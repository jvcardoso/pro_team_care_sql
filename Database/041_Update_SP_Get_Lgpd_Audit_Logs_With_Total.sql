-- =========================================================================================
-- Autor: opencode
-- Data: 2025-10-29
-- Descrição: Atualiza a Stored Procedure sp_get_lgpd_audit_logs para retornar
--            também o total de registros, permitindo paginação correta no frontend.
-- =========================================================================================

USE pro_team_care_logs;
GO

-- Garante que a procedure seja removida se já existir, para permitir recriação
IF OBJECT_ID('core.sp_get_lgpd_audit_logs', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE core.sp_get_lgpd_audit_logs;
END
GO

-- =========================================================================================
-- Criação da Stored Procedure Atualizada
-- =========================================================================================
CREATE PROCEDURE core.sp_get_lgpd_audit_logs
    -- Parâmetros de Entrada
    @requesting_user_id INT,
    @target_company_id INT,
    @page_number INT = 1,
    @page_size INT = 100
AS
BEGIN
    -- Otimização para não retornar contagem de linhas afetadas
    SET NOCOUNT ON;

    -- Variáveis para armazenar os dados do usuário que faz a requisição
    DECLARE @is_system_admin BIT;
    DECLARE @user_company_id INT;
    DECLARE @total_count INT;

    -- Busca as permissões e o company_id do usuário no banco principal
    -- Esta é uma consulta cross-database
    SELECT
        @is_system_admin = u.is_system_admin,
        @user_company_id = u.company_id
    FROM
        pro_team_care.core.users u
    WHERE
        u.id = @requesting_user_id;

    -- Calcula o total de registros baseado nas permissões do usuário
    IF @is_system_admin = 1
    BEGIN
        SELECT @total_count = COUNT(*)
        FROM core.lgpd_audit_log
        WHERE entity_type = 'companies' AND entity_id = @target_company_id;
    END
    ELSE
    BEGIN
        SELECT @total_count = COUNT(*)
        FROM core.lgpd_audit_log
        WHERE entity_type = 'companies'
            AND entity_id = @target_company_id
            AND company_id = @user_company_id; -- Filtro de segurança do tenant
    END

    -- Retorna primeiro o total de registros (result set único)
    SELECT @total_count AS total_records;

    -- Se o usuário for um administrador do sistema, ele pode ver os logs da empresa alvo
    IF @is_system_admin = 1
    BEGIN
        SELECT
            id, created_at, company_id, user_id, user_email, action_type,
            entity_type, entity_id, sensitive_fields, ip_address, endpoint
        FROM
            core.lgpd_audit_log
        WHERE
            entity_type = 'companies' AND entity_id = @target_company_id
        ORDER BY
            created_at DESC
        -- Implementação da paginação
        OFFSET (@page_number - 1) * @page_size ROWS
        FETCH NEXT @page_size ROWS ONLY;
    END
    -- Se for um usuário comum, ele só pode ver os logs da empresa alvo se for a sua própria empresa
    ELSE
    BEGIN
        SELECT
            id, created_at, company_id, user_id, user_email, action_type,
            entity_type, entity_id, sensitive_fields, ip_address, endpoint
        FROM
            core.lgpd_audit_log
        WHERE
            entity_type = 'companies'
            AND entity_id = @target_company_id
            AND company_id = @user_company_id -- Filtro de segurança do tenant
        ORDER BY
            created_at DESC
        -- Implementação da paginação
        OFFSET (@page_number - 1) * @page_size ROWS
        FETCH NEXT @page_size ROWS ONLY;
    END

    SET NOCOUNT OFF;
END
GO

PRINT 'Stored Procedure core.sp_get_lgpd_audit_logs atualizada com total de registros.';
GO