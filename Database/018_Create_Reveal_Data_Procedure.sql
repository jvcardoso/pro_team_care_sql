-- =================================================================================
-- Script:         018_Create_Reveal_Data_Procedure.sql (v1.3 - Corrigido)
-- Descrição:
-- v1.3 - Corrige erro de conversão de tipo (sql_variant para bigint)
--        usando TRY_CAST ao ler o SESSION_CONTEXT.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER PROCEDURE [core].[sp_reveal_sensitive_data]
    @entity_type NVARCHAR(128),
    @entity_id BIGINT,
    @fields_to_reveal JSON,
    @user_email NVARCHAR(255),
    @ip_address NVARCHAR(45),
    @endpoint NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;

    IF [core].[fn_CanUserUnmaskData]() = 0
    BEGIN
        THROW 50001, 'O usuário não tem permissão para revelar estes dados.', 1;
        RETURN;
    END

    BEGIN TRY
        -- CORREÇÃO: Adicionado TRY_CAST para converter o sql_variant para BIGINT.
        DECLARE @current_user_id BIGINT = TRY_CAST(SESSION_CONTEXT(N'user_id') AS BIGINT);
        DECLARE @company_id BIGINT;

        IF @current_user_id IS NULL
        BEGIN
            THROW 50005, 'Contexto da sessão (user_id) não encontrado. A API precisa enviar o contexto.', 1;
            RETURN;
        END

        IF @entity_type = 'pf_profiles'
            SELECT @company_id = p.company_id FROM core.people p JOIN core.pf_profiles pp ON p.id = pp.person_id WHERE pp.id = @entity_id;
        ELSE IF @entity_type = 'pj_profiles'
            SELECT @company_id = company_id FROM core.pj_profiles WHERE id = @entity_id;

        INSERT INTO [pro_team_care_logs].[core].[lgpd_audit_log]
            (company_id, user_id, user_email, action_type, entity_type, entity_id, sensitive_fields, ip_address, endpoint)
        VALUES
            (@company_id, @current_user_id, @user_email, 'REVEAL', @entity_type, @entity_id, @fields_to_reveal, @ip_address, @endpoint);
    END TRY
    BEGIN CATCH
        THROW 50002, 'Falha ao registrar o log de auditoria. A operação foi cancelada.', 1;
        RETURN;
    END CATCH

    DECLARE @fieldList NVARCHAR(MAX);
    SELECT @fieldList = STRING_AGG(QUOTENAME([value]), ',') FROM OPENJSON(@fields_to_reveal);

    IF @fieldList IS NULL OR @fieldList = ''
    BEGIN
         THROW 50004, 'A lista de campos a revelar está vazia ou em formato inválido.', 1;
        RETURN;
    END

    DECLARE @sql NVARCHAR(MAX);
    DECLARE @schema_name NVARCHAR(128) = N'core';

    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = @entity_type AND SCHEMA_NAME(schema_id) = @schema_name)
    BEGIN
        THROW 50003, 'Tipo de entidade inválido.', 1;
        RETURN;
    END

    SET @sql = N'SELECT ' + @fieldList +
               N' FROM ' + QUOTENAME(@schema_name) + '.' + QUOTENAME(@entity_type) +
               N' WHERE id = @p_entity_id;';

    EXEC sp_executesql @sql, N'@p_entity_id BIGINT', @p_entity_id = @entity_id;
END
GO

PRINT 'Stored Procedure [core].[sp_reveal_sensitive_data] (v1.3) atualizada com sucesso.';
