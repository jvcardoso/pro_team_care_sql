-- =================================================================================
-- Script:         009_Create_Log_Table_And_Indexes.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Cria o schema 'core' e a tabela 'login_logs' com seus respectivos
-- índices de performance no banco de dados 'pro_team_care_logs'.
--
-- Pré-requisitos:
-- - Executar após o script 008.
-- =================================================================================

USE pro_team_care_logs;
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'core')
BEGIN
    EXEC('CREATE SCHEMA [core]');
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[core].[login_logs]') AND type in (N'U'))
BEGIN
    CREATE TABLE [core].[login_logs] (
        [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
        [company_id] BIGINT NULL,
        [user_id] BIGINT NULL,
        [email_attempted] NVARCHAR(255) NOT NULL,
        [ip_address] NVARCHAR(45),
        [user_agent] NVARCHAR(1024),
        [status] NVARCHAR(20) NOT NULL,
        [failure_reason] NVARCHAR(255),
        [session_id] NVARCHAR(255),
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),

        CONSTRAINT [CHK_login_logs_status]
            CHECK ([status] IN ('SUCCESS', 'FAILED', 'INACTIVE_USER_ATTEMPT'))
    );

    -- Índices para performance
    CREATE INDEX [idx_login_logs_company_date] ON [core].[login_logs] ([company_id], [created_at] DESC);
    CREATE INDEX [idx_login_logs_email_status] ON [core].[login_logs] ([email_attempted], [status]);
    CREATE INDEX [idx_login_logs_ip_date] ON [core].[login_logs] ([ip_address], [created_at] DESC);
END
GO
