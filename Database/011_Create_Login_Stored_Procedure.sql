-- =================================================================================
-- Script:         011_Create_Auth_Stored_Procedures.sql (v2.0 - Refatorado)
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Cria as Stored Procedures de suporte à autenticação.
-- A validação de senha (bcrypt) agora ocorre na aplicação.
--
--  - sp_get_user_for_auth: Apenas busca os dados do usuário para validação.
--  - sp_log_login_success: Atualiza 'last_login_at' e registra o log de sucesso.
--  - sp_log_login_failure: Registra falhas de login (email inválido, senha incorreta, usuário inativo).
-- =================================================================================

USE pro_team_care;
GO

-- Procedure para buscar dados do usuário para a aplicação validar
CREATE OR ALTER PROCEDURE [core].[sp_get_user_for_auth]
    @email_attempted NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        id,
        company_id,
        password AS stored_password_hash, -- A aplicação usará isso para o bcrypt.checkpw()
        is_active
    FROM
        [core].[users]
    WHERE
        email_address = @email_attempted;
END
GO

PRINT 'Stored Procedure [core].[sp_get_user_for_auth] criada/alterada com sucesso.';
GO

-- Procedure para ser chamada APÓS o sucesso da validação na aplicação
CREATE OR ALTER PROCEDURE [core].[sp_log_login_success]
    @user_id BIGINT,
    @ip_address NVARCHAR(45),
    @user_agent NVARCHAR(1024)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Atualiza a data do último login
        UPDATE [core].[users]
        SET last_login_at = GETDATE()
        WHERE id = @user_id;

        -- Registra o sucesso no banco de logs
        INSERT INTO [pro_team_care_logs].[core].[login_logs]
            (company_id, user_id, email_attempted, ip_address, user_agent, status)
        SELECT
            company_id,
            id,
            email_address,
            @ip_address,
            @user_agent,
            'SUCCESS'
        FROM
            [core].[users]
        WHERE
            id = @user_id;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

PRINT 'Stored Procedure [core].[sp_log_login_success] criada/alterada com sucesso.';
GO

-- Procedure para registrar falhas de login
CREATE OR ALTER PROCEDURE [core].[sp_log_login_failure]
    @user_id BIGINT = NULL,           -- NULL se email não encontrado
    @company_id BIGINT = NULL,         -- NULL se email não encontrado
    @email_attempted NVARCHAR(255),
    @ip_address NVARCHAR(45),
    @user_agent NVARCHAR(1024),
    @failure_reason NVARCHAR(255)      -- Ex: 'INVALID_CREDENTIALS', 'USER_INACTIVE'
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        -- Registra a falha no banco de logs
        INSERT INTO [pro_team_care_logs].[core].[login_logs]
            (company_id, user_id, email_attempted, ip_address, user_agent, status, failure_reason)
        VALUES
            (@company_id, @user_id, @email_attempted, @ip_address, @user_agent, 'FAILED', @failure_reason);
    END TRY
    BEGIN CATCH
        -- Em caso de erro, apenas propaga (não interrompe o fluxo de autenticação)
        THROW;
    END CATCH
END
GO

PRINT 'Stored Procedure [core].[sp_log_login_failure] criada/alterada com sucesso.';
GO