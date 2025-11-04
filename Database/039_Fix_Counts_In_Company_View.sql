-- ===========================================
-- CORREÇÃO DEFINITIVA: View com contagens funcionais
-- ===========================================

USE [pro_team_care];
GO

-- 1. REMOVER VIEW EXISTENTE
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    DROP VIEW [core].[vw_complete_company_data];
    PRINT '✓ View vw_complete_company_data removida para correção';
END
GO

-- 2. RECRIAR VIEW COM CONTAGENS CORRETAS
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
            SUBSTRING(pj.tax_id, 1, 2) + '.***.***/****-' + SUBSTRING(pj.tax_id, 13, 2)
        ELSE
            '**.***.***/****-**'
    END AS CNPJ,

    -- Inscrição Estadual mascarada conforme LGPD
    CASE
        WHEN LEN(LTRIM(RTRIM(ISNULL(pj.secondary_tax_id, '')))) > 0 THEN
            SUBSTRING(pj.secondary_tax_id, 1, 3) + '.***.***'
        ELSE
            NULL
    END AS SecondaryTaxId,

    -- Inscrição Municipal mascarada conforme LGPD
    CASE
        WHEN LEN(LTRIM(RTRIM(ISNULL(pj.municipal_registration, '')))) > 0 THEN
            '******' + SUBSTRING(pj.municipal_registration, LEN(pj.municipal_registration) - 1, 2)
        ELSE
            NULL
    END AS MunicipalRegistration,

    -- Regime Tributário e Natureza Jurídica (não sensíveis, podem ser exibidos)
    pj.tax_regime,
    pj.legal_nature,

    -- Endereço principal
    addr.id AS PrincipalAddressId,
    addr.street AS PrincipalStreet,
    addr.number AS PrincipalNumber,
    addr.neighborhood AS PrincipalNeighborhood,
    addr.city AS PrincipalCity,
    addr.state AS PrincipalState,
    addr.zip_code AS PrincipalZipCode,

    -- CONTAGENS CORRETAS
    -- Estabelecimentos: conta direta na tabela establishments
    ISNULL((
        SELECT COUNT(*)
        FROM [core].[establishments] e
        WHERE e.company_id = c.id AND e.is_active = 1
    ), 0) AS establishments_count,

    -- Clientes: usuários com roles não-sistema associados à empresa
    ISNULL((
        SELECT COUNT(DISTINCT ur.user_id)
        FROM [core].[user_roles] ur
        JOIN [core].[roles] r ON ur.role_id = r.id
        WHERE ur.context_id = c.id
          AND ur.context_type = 'company'
          AND ur.status = 'active'
          AND r.is_system_role = 0
    ), 0) AS clients_count,

    -- Profissionais: usuários com roles específicos ou qualquer role associado
    ISNULL((
        SELECT COUNT(DISTINCT ur.user_id)
        FROM [core].[user_roles] ur
        WHERE ur.context_id = c.id
          AND ur.context_type IN ('company', 'establishment')
          AND ur.status = 'active'
    ), 0) AS professionals_count,

    -- Usuários totais: todos os usuários associados (mesma lógica dos profissionais)
    ISNULL((
        SELECT COUNT(DISTINCT ur.user_id)
        FROM [core].[user_roles] ur
        WHERE ur.context_id = c.id
          AND ur.context_type IN ('company', 'establishment')
          AND ur.status = 'active'
    ), 0) AS users_count,

    -- Telefones como JSON ARRAY
    ISNULL((
        SELECT
            ph.id,
            REPLACE(REPLACE(REPLACE(REPLACE(ph.number, '(', ''), ')', ''), ' ', ''), '-', '') as number,
            ph.type,
            ph.is_principal
        FROM [core].[phones] ph
        WHERE ph.company_id = c.id
        FOR JSON PATH
    ), '[]') AS PhoneNumbers,

    -- Emails como JSON ARRAY
    ISNULL((
        SELECT
            em.id,
            em.email_address as email,
            em.type,
            em.is_principal
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

PRINT '✓ View vw_complete_company_data recriada com contagens corrigidas';
GO

-- 3. TESTE IMEDIATO
PRINT '';
PRINT '=== TESTE DAS CONTAGENS CORRIGIDAS ===';
GO

SELECT TOP 5
    CompanyId,
    RazaoSocial,
    CNPJ,
    establishments_count,
    clients_count,
    professionals_count,
    users_count,
    CompanyAccessStatus
FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

-- 4. VERIFICAÇÃO DETALHADA
PRINT '';
PRINT '=== VERIFICAÇÃO DETALHADA ===';
GO

SELECT
    COUNT(*) as Total_Empresas,
    SUM(establishments_count) as Total_Estabelecimentos,
    SUM(clients_count) as Total_Clientes,
    SUM(professionals_count) as Total_Profissionais,
    SUM(users_count) as Total_Usuarios
FROM [core].[vw_complete_company_data];
GO

PRINT '✓ Script concluído - execute as consultas de diagnóstico em diagnostico_contagens.sql';
GO