-- =================================================================================
-- Script:         005_Create_Contact_Tables.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Cria as tabelas polimórficas para armazenar informações de contato:
-- phones, emails, and addresses.
--
-- Pré-requisitos:
-- - Executar após o script 002.
-- =================================================================================

USE pro_team_care;
GO

-- Tabela de Telefones
CREATE TABLE [core].[phones] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [phoneable_type] NVARCHAR(255) NOT NULL,
    [phoneable_id] BIGINT NOT NULL,
    [company_id] BIGINT NOT NULL,
    [country_code] NVARCHAR(3) DEFAULT '55',
    [number] NVARCHAR(20) NOT NULL,
    [extension] NVARCHAR(10),
    [type] NVARCHAR(20) NOT NULL DEFAULT 'mobile',
    [is_principal] BIT DEFAULT 0,
    [is_active] BIT DEFAULT 1,
    [phone_name] NVARCHAR(100),
    [is_whatsapp] BIT DEFAULT 0,
    [whatsapp_formatted] NVARCHAR(15),
    [whatsapp_verified] BIT DEFAULT 0,
    [whatsapp_verified_at] DATETIME2,
    [whatsapp_business] BIT DEFAULT 0,
    [whatsapp_name] NVARCHAR(100),
    [accepts_whatsapp_marketing] BIT DEFAULT 1,
    [accepts_whatsapp_notifications] BIT DEFAULT 1,
    [whatsapp_preferred_time_start] TIME,
    [whatsapp_preferred_time_end] TIME,
    [carrier] NVARCHAR(30),
    [line_type] NVARCHAR(20),
    [contact_priority] INT DEFAULT 5,
    [last_contact_attempt] DATETIME2,
    [last_contact_success] DATETIME2,
    [contact_attempts_count] INT DEFAULT 0,
    [can_receive_calls] BIT DEFAULT 1,
    [can_receive_sms] BIT DEFAULT 1,
    [verified_at] DATETIME2,
    [verification_method] NVARCHAR(50),
    [api_data] JSON,
    [created_by_user_id] BIGINT,
    [updated_by_user_id] BIGINT,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [deleted_at] DATETIME2
);
GO

-- Tabela de Emails
CREATE TABLE [core].[emails] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [emailable_type] NVARCHAR(255) NOT NULL,
    [emailable_id] BIGINT NOT NULL,
    [company_id] BIGINT NOT NULL,
    [email_address] NVARCHAR(255) NOT NULL,
    [type] NVARCHAR(20) NOT NULL DEFAULT 'work',
    [is_principal] BIT DEFAULT 0,
    [is_active] BIT DEFAULT 1,
    [verified_at] DATETIME2,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [deleted_at] DATETIME2
);
GO

-- Tabela de Endereços
CREATE TABLE [core].[addresses] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [addressable_type] NVARCHAR(255) NOT NULL,
    [addressable_id] BIGINT NOT NULL,
    [company_id] BIGINT NOT NULL,
    [street] NVARCHAR(255) NOT NULL,
    [number] NVARCHAR(20),
    [details] NVARCHAR(100),
    [neighborhood] NVARCHAR(100) NOT NULL,
    [city] NVARCHAR(100) NOT NULL,
    [state] NVARCHAR(2) NOT NULL,
    [zip_code] NVARCHAR(10) NOT NULL,
    [country] NVARCHAR(2) DEFAULT 'BR',
    [type] NVARCHAR(20) NOT NULL DEFAULT 'commercial',
    [is_principal] BIT DEFAULT 0,
    [latitude] DECIMAL(10,8),
    [longitude] DECIMAL(11,8),
    [google_place_id] NVARCHAR(255),
    [formatted_address] NVARCHAR(MAX),
    [ibge_city_code] INT,
    [access_notes] NVARCHAR(MAX),
    [is_validated] BIT DEFAULT 0,
    [last_validated_at] DATETIME2,
    [validation_source] NVARCHAR(100),
    [api_data] JSON,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [deleted_at] DATETIME2
);
GO
