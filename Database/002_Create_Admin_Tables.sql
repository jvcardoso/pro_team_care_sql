-- =================================================================================
-- Script:         002_Create_Admin_Tables.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Cria as tabelas estruturais do núcleo administrativo do sistema:
-- companies, people, establishments, roles, users, user_roles.
--
-- Pré-requisitos:
-- - Executar após o script 001.
-- =================================================================================

USE pro_team_care;
GO

-- Tabela de Empresas (Tenants)
CREATE TABLE [core].[companies] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [person_id] BIGINT NULL, [settings] JSON, [metadata] JSON, [display_order] INT DEFAULT 0,
    [access_status] NVARCHAR(20) DEFAULT 'pending_contract', [contract_terms_version] NVARCHAR(10), [contract_accepted_at] DATETIME2,
    [contract_accepted_by] NVARCHAR(255), [contract_ip_address] NVARCHAR(45), [activation_sent_at] DATETIME2,
    [activation_sent_to] NVARCHAR(255), [activated_at] DATETIME2, [activated_by_user_id] BIGINT,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [deleted_at] DATETIME2
);
GO
-- Tabela de Pessoas (Físicas e Jurídicas)
CREATE TABLE [core].[people] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [company_id] BIGINT NOT NULL, [person_type] NVARCHAR(255) NOT NULL,
    [name] NVARCHAR(200) NOT NULL, [trade_name] NVARCHAR(200), [tax_id] NVARCHAR(14) NOT NULL, [secondary_tax_id] NVARCHAR(20),
    [birth_date] DATE, [incorporation_date] DATE, [gender] NVARCHAR(20), [marital_status] NVARCHAR(50),
    [occupation] NVARCHAR(100), [tax_regime] NVARCHAR(50), [legal_nature] NVARCHAR(100),
    [municipal_registration] NVARCHAR(20), [website] NVARCHAR(MAX), [description] NVARCHAR(MAX),
    [status] NVARCHAR(20) NOT NULL DEFAULT 'active', [is_active] BIT DEFAULT 1, [lgpd_consent_version] NVARCHAR(10),
    [lgpd_consent_given_at] DATETIME2, [lgpd_data_retention_expires_at] DATETIME2, [metadata] JSON,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO
-- Tabela de Estabelecimentos
CREATE TABLE [core].[establishments] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [person_id] BIGINT NOT NULL, [company_id] BIGINT NOT NULL, [code] NVARCHAR(50) NOT NULL,
    [type] NVARCHAR(20), [category] NVARCHAR(30), [is_active] BIT NOT NULL DEFAULT 1, [is_principal] BIT NOT NULL DEFAULT 0,
    [display_order] INT NOT NULL DEFAULT 0, [settings] JSON, [metadata] JSON, [operating_hours] JSON, [service_areas] JSON,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [deleted_at] DATETIME2
);
GO
-- Tabela de Papéis (Permissões)
CREATE TABLE [core].[roles] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [name] NVARCHAR(125) NOT NULL UNIQUE, [display_name] NVARCHAR(200) NOT NULL,
    [description] NVARCHAR(MAX), [level] INT NOT NULL DEFAULT 0, [context_type] NVARCHAR(255) NOT NULL DEFAULT 'establishment',
    [is_active] BIT DEFAULT 1, [is_system_role] BIT DEFAULT 0, [settings] JSON,
    [created_at] DATETIME2 DEFAULT GETDATE(), [updated_at] DATETIME2 DEFAULT GETDATE()
);
GO
-- Tabela de Usuários
CREATE TABLE [core].[users] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [person_id] BIGINT, [company_id] BIGINT, [establishment_id] BIGINT,
    [invited_by_user_id] BIGINT, [email_address] NVARCHAR(255) NOT NULL UNIQUE, [password] NVARCHAR(255) NOT NULL,
    [is_active] BIT NOT NULL DEFAULT 1, [is_system_admin] BIT DEFAULT 0, [context_type] NVARCHAR(255),
    [notification_settings] JSON, [two_factor_secret] NVARCHAR(MAX), [two_factor_recovery_codes] JSON,
    [last_login_at] DATETIME2, [password_changed_at] DATETIME2, [created_at] DATETIME2 DEFAULT GETDATE(),
    [updated_at] DATETIME2 DEFAULT GETDATE(), [deleted_at] DATETIME2
);
GO
-- Tabela de Ligação Usuário-Papel
CREATE TABLE [core].[user_roles] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [user_id] BIGINT NOT NULL, [role_id] BIGINT NOT NULL,
    [context_type] NVARCHAR(255) NOT NULL, [context_id] BIGINT NOT NULL, [status] NVARCHAR(255) NOT NULL DEFAULT 'active',
    [assigned_by_user_id] BIGINT, [assigned_at] DATETIME2 DEFAULT GETDATE(), [expires_at] DATETIME2,
    [created_at] DATETIME2 DEFAULT GETDATE(), [updated_at] DATETIME2 DEFAULT GETDATE()
);
GO
