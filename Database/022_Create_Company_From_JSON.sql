-- =================================================================================
-- Script:         022_Create_Company_From_JSON.sql
-- Projeto:        Pro Team Care
-- Descrição:
-- Cria a Stored Procedure [sp_create_company_from_json] que realiza o cadastro
-- completo de uma nova empresa e seus contatos a partir de um único
-- objeto JSON, garantindo atomicidade e performance.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER PROCEDURE [core].[sp_create_company_from_json]
    @jsonData JSON
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;

    BEGIN TRY
        -- Declaração de variáveis para os IDs gerados
        DECLARE @companyId BIGINT;
        DECLARE @personId BIGINT;
        DECLARE @pjProfileId BIGINT;

        -- ============================================================================
        -- ETAPA 1: Extrair dados do JSON e criar a Company, a People e o PJ Profile
        -- ============================================================================
        
        -- Insere a "conta" na tabela companies
        INSERT INTO [core].[companies] (access_status)
        SELECT JSON_VALUE(@jsonData, '$.access_status')
        WHERE JSON_VALUE(@jsonData, '$.access_status') IS NOT NULL; -- Garante que o campo existe no JSON

        IF @@ROWCOUNT = 0 -- Se não inseriu, usa um valor padrão
            INSERT INTO [core].[companies] (access_status) VALUES ('pending_contract');

        SET @companyId = SCOPE_IDENTITY();

        -- Insere a "pessoa raiz" com o nome (Razão Social) do JSON
        INSERT INTO [core].[people] (company_id, name, status)
        SELECT @companyId, JSON_VALUE(@jsonData, '$.pj_profile.name'), 'active';
        SET @personId = SCOPE_IDENTITY();

        -- Insere o perfil de Pessoa Jurídica com os dados do JSON
        INSERT INTO [core].[pj_profiles] (
            person_id, company_id, tax_id, trade_name, incorporation_date,
            tax_regime, legal_nature, municipal_registration
        )
        SELECT
            @personId,
            @companyId,
            JSON_VALUE(@jsonData, '$.pj_profile.tax_id'),
            JSON_VALUE(@jsonData, '$.pj_profile.trade_name'),
            TRY_CAST(JSON_VALUE(@jsonData, '$.pj_profile.incorporation_date') AS DATE),
            JSON_VALUE(@jsonData, '$.pj_profile.tax_regime'),
            JSON_VALUE(@jsonData, '$.pj_profile.legal_nature'),
            JSON_VALUE(@jsonData, '$.pj_profile.municipal_registration')
        ;
        SET @pjProfileId = SCOPE_IDENTITY();

        -- Atualiza a company para fechar o ciclo de referência
        UPDATE [core].[companies] SET person_id = @personId WHERE id = @companyId;


        -- ============================================================================
        -- ETAPA 2: Inserir múltiplos contatos a partir dos arrays JSON
        -- ============================================================================

        -- Insere todos os endereços do array 'addresses'
        INSERT INTO [core].[addresses] (
            addressable_type, addressable_id, company_id, street, number, details,
            neighborhood, city, state, zip_code, country, type, is_principal
        )
        SELECT
            'PjProfile', @pjProfileId, @companyId, street, number, details,
            neighborhood, city, state, zip_code, country, type, is_principal
        FROM OPENJSON(@jsonData, '$.addresses')
        WITH (
            street NVARCHAR(255) '$.street',
            number NVARCHAR(20) '$.number',
            details NVARCHAR(100) '$.details',
            neighborhood NVARCHAR(100) '$.neighborhood',
            city NVARCHAR(100) '$.city',
            state NVARCHAR(2) '$.state',
            zip_code NVARCHAR(10) '$.zip_code',
            country NVARCHAR(2) '$.country',
            type NVARCHAR(20) '$.type',
            is_principal BIT '$.is_principal'
        );

        -- Insere todos os telefones do array 'phones'
        INSERT INTO [core].[phones] (
            phoneable_type, phoneable_id, company_id, country_code, number,
            extension, type, is_principal, is_whatsapp, phone_name
        )
        SELECT
            'PjProfile', @pjProfileId, @companyId, country_code, number,
            extension, type, is_principal, is_whatsapp, phone_name
        FROM OPENJSON(@jsonData, '$.phones')
        WITH (
            country_code NVARCHAR(3) '$.country_code',
            number NVARCHAR(20) '$.number',
            extension NVARCHAR(10) '$.extension',
            type NVARCHAR(20) '$.type',
            is_principal BIT '$.is_principal',
            is_whatsapp BIT '$.is_whatsapp',
            phone_name NVARCHAR(100) '$.phone_name'
        );

        -- Insere todos os emails do array 'emails'
        INSERT INTO [core].[emails] (
            emailable_type, emailable_id, company_id, email_address, type, is_principal
        )
        SELECT
            'PjProfile', @pjProfileId, @companyId, email_address, type, is_principal
        FROM OPENJSON(@jsonData, '$.emails')
        WITH (
            email_address NVARCHAR(255) '$.email_address',
            type NVARCHAR(20) '$.type',
            is_principal BIT '$.is_principal'
        );

        -- ============================================================================
        -- ETAPA 3: Retornar os IDs das entidades criadas
        -- ============================================================================
        SELECT
            @companyId AS NewCompanyId,
            @personId AS NewPersonId,
            @pjProfileId AS NewPjProfileId;

        COMMIT TRANSACTION;
        PRINT '✅ SUCESSO: Empresa e contatos criados com sucesso a partir do JSON.';

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT '❌ ERRO: Ocorreu um problema e o cadastro foi desfeito (rollback).';
        THROW; -- Lança o erro original para a aplicação poder capturá-lo
    END CATCH;
END;
GO
