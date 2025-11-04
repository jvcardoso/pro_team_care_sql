-- =================================================================================
-- Script:         029_Create_User_Me_Procedure_JSON.sql (v2.0)
-- Descrição:      Refatora a procedure [sp_get_user_me_data] para retornar um
--                 único objeto JSON em vez de múltiplos result sets.
--                 Isso simplifica drasticamente o consumo pela API.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER PROCEDURE [core].[sp_get_user_me_data]
    @user_id_input BIGINT
AS
BEGIN
    SET NOCOUNT ON;

    -- A lógica de auditoria continua a mesma, executada primeiro.
    DECLARE @user_id BIGINT, @company_id BIGINT, @user_email NVARCHAR(255);
    SELECT
        @user_id = u.id,
        @company_id = u.company_id,
        @user_email = u.email_address
    FROM [core].[users] u
    WHERE u.id = @user_id_input;

    IF @user_id IS NOT NULL
    BEGIN
        INSERT INTO [pro_team_care_logs].[core].[lgpd_audit_log]
            (company_id, user_id, user_email, action_type, entity_type, entity_id, endpoint)
        VALUES
            (@company_id, @user_id, @user_email, 'VIEW', 'user_profile', @user_id, '/auth/me');
    END

    -- MUDANÇA PRINCIPAL: Construção do objeto JSON
    -- A query agora retorna uma única linha e uma única coluna chamada [UserDataJson]
    SELECT
        u.id, u.email_address, u.person_id, u.company_id, u.establishment_id,
        u.is_active, u.is_system_admin, u.last_login_at, u.created_at, u.updated_at,
        p.name as full_name,
        cp.name as company_name,
        ep.name as establishment_name,
        u.context_type,
        -- MÁGICA AQUI: Uma subconsulta que busca os estabelecimentos e os transforma em um array JSON aninhado.
        (
            SELECT est.id, p_est.name
            FROM [core].[establishments] est
            JOIN [core].[people] p_est ON p_est.id = est.person_id
            WHERE est.company_id = u.company_id AND est.deleted_at IS NULL
            FOR JSON PATH
        ) AS establishments
    FROM [core].[users] u
    LEFT JOIN [core].[people] p ON p.id = u.person_id
    LEFT JOIN [core].[companies] c ON c.id = u.company_id AND c.deleted_at IS NULL
    LEFT JOIN [core].[people] cp ON cp.id = c.person_id
    LEFT JOIN [core].[establishments] e ON e.id = u.establishment_id AND e.deleted_at IS NULL
    LEFT JOIN [core].[people] ep ON ep.id = e.person_id
    WHERE u.id = @user_id_input AND u.deleted_at IS NULL
    -- Transforma o resultado da linha inteira em um único objeto JSON.
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;

END;
GO

PRINT '✅ Procedure [core].[sp_get_user_me_data] (v2.0 - JSON) criada/alterada com sucesso.';