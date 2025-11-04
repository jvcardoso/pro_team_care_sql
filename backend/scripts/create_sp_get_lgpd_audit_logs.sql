-- Stored Procedure: core.sp_get_lgpd_audit_logs
-- Retorna logs de auditoria LGPD para uma empresa específica com paginação
-- Autorização: Admins do sistema veem todos os logs; usuários normais veem apenas da própria empresa

USE [pro_team_care];
GO

IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[core].[sp_get_lgpd_audit_logs]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [core].[sp_get_lgpd_audit_logs];
GO

CREATE PROCEDURE [core].[sp_get_lgpd_audit_logs]
    @requesting_user_id INT,
    @target_company_id INT,
    @page_number INT = 1,
    @page_size INT = 50
AS
BEGIN
    SET NOCOUNT ON;

    -- Verificar se o usuário é admin do sistema
    DECLARE @is_system_admin BIT = 0;
    DECLARE @user_company_id INT;

    SELECT @is_system_admin = ISNULL(is_system_admin, 0),
           @user_company_id = company_id
    FROM core.users
    WHERE id = @requesting_user_id;

    -- Se não for admin, verificar se pode acessar a empresa alvo
    IF @is_system_admin = 0 AND (@user_company_id IS NULL OR @user_company_id <> @target_company_id)
    BEGIN
        -- Usuário não autorizado
        SELECT
            CAST(0 AS BIGINT) AS id,
            CAST(NULL AS DATETIME2) AS created_at,
            CAST(NULL AS NVARCHAR(255)) AS company_id,
            CAST(NULL AS BIGINT) AS user_id,
            CAST(NULL AS NVARCHAR(510)) AS user_email,
            CAST(NULL AS NVARCHAR(50)) AS action_type,
            CAST(NULL AS NVARCHAR(50)) AS entity_type,
            CAST(NULL AS BIGINT) AS entity_id,
            CAST(NULL AS NVARCHAR(MAX)) AS sensitive_fields,
            CAST(NULL AS NVARCHAR(45)) AS ip_address,
            CAST(NULL AS NVARCHAR(1000)) AS endpoint
        WHERE 1 = 0; -- Retorna conjunto vazio

        RETURN;
    END

    -- Calcular offset para paginação
    DECLARE @offset INT = (@page_number - 1) * @page_size;

    -- Retornar logs filtrados e paginados
    SELECT
        id,
        created_at,
        company_id,
        user_id,
        user_email,
        action_type,
        entity_type,
        entity_id,
        sensitive_fields,
        ip_address,
        endpoint
    FROM pro_team_care_logs.core.lgpd_audit_log
    WHERE entity_type = 'companies'
      AND entity_id = @target_company_id
    ORDER BY created_at DESC
    OFFSET @offset ROWS
    FETCH NEXT @page_size ROWS ONLY;

END
GO

-- Teste da procedure
-- EXEC core.sp_get_lgpd_audit_logs @requesting_user_id=1, @target_company_id=164, @page_number=1, @page_size=10;