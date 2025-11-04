-- Script para implementar mascaramento de CNPJ na view vw_complete_company_data
-- Seguindo o padrão "Database-First Presentation" do projeto Pro Team Care

-- Este script deve ser executado no SQL Server (pro_team_care database)

USE [pro_team_care];
GO

-- Verificar se a view existe
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    -- Dropar a view existente
    DROP VIEW [core].[vw_complete_company_data];
    PRINT 'View vw_complete_company_data dropped successfully.';
END
GO

-- Recriar a view com mascaramento de CNPJ
CREATE VIEW [core].[vw_complete_company_data]
AS
SELECT
    c.id AS CompanyId,
    c.access_status AS CompanyAccessStatus,
    c.person_id AS PersonId,
    pj.id AS PjProfileId,
    p.name AS RazaoSocial,
    pj.trade_name AS NomeFantasia,

    -- CNPJ mascarado conforme LGPD
    CASE
        WHEN LEN(LTRIM(RTRIM(ISNULL(pj.tax_id, '')))) = 14 THEN
            -- Formato: XX.***.***/XXXX-XX
            SUBSTRING(pj.tax_id, 1, 2) + '.***.***/' +
            SUBSTRING(pj.tax_id, 9, 4) + '-' +
            SUBSTRING(pj.tax_id, 13, 2)
        ELSE
            -- Se não tiver 14 dígitos ou for nulo, retorna mascarado genérico
            '**.***.***/****-**'
    END AS CNPJ,

    -- Endereço principal
    addr.street AS PrincipalStreet,
    addr.number AS PrincipalNumber,
    addr.neighborhood AS PrincipalNeighborhood,
    addr.city AS PrincipalCity,
    addr.state AS PrincipalState,
    addr.zip_code AS PrincipalZipCode,

    -- Telefones agregados (JSON nativo)
    ISNULL((
        SELECT
            REPLACE(REPLACE(REPLACE(ph.number, '(', ''), ')', ''), '-', '') as number,
            ph.type
        FROM [core].[phones] ph
        WHERE ph.company_id = c.id
        FOR JSON PATH
    ), '[]') AS PhoneNumbers,

    -- Emails agregados (JSON nativo)
    ISNULL((
        SELECT
            em.email_address as email,
            em.type
        FROM [core].[emails] em
        WHERE em.company_id = c.id
        FOR JSON PATH
    ), '[]') AS EmailAddresses,

    -- Data de incorporação
    pj.incorporation_date,

    -- Data de criação da empresa
    c.created_at AS CompanyCreatedAt

FROM
    [core].[companies] c
    LEFT JOIN [core].[people] p ON c.person_id = p.id
    LEFT JOIN [core].[pj_profiles] pj ON pj.person_id = p.id
    LEFT JOIN [core].[addresses] addr ON addr.company_id = c.id AND addr.is_principal = 1;
GO

PRINT 'View vw_complete_company_data recreated with CNPJ masking.';
PRINT 'CNPJ format: XX.***.***/XXXX-XX (LGPD compliant)';
GO

-- Verificar permissões (recomendação)
-- A conta da aplicação deve ter SELECT apenas na view, não na tabela base
PRINT 'IMPORTANT: Ensure application database user has SELECT permission ONLY on this view, not on base tables.';
GO