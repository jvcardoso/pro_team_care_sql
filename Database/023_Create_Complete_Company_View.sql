-- =================================================================================
-- Script:         023_Create_Complete_Company_View.sql
-- Projeto:        Pro Team Care
-- Descrição:
-- Cria a view [vw_complete_company_data] que une todas as informações
-- relevantes de uma empresa em uma única consulta, já aplicando as
-- regras de mascaramento de dados (LGPD).
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER VIEW [core].[vw_complete_company_data]
AS
WITH AllPhones AS (
    -- Agrega todos os telefones de um perfil PJ em uma única string
    SELECT
        pjp.person_id,
        STRING_AGG(ph.number, ', ') AS PhoneNumbers
    FROM core.pj_profiles pjp
    JOIN core.phones ph ON pjp.id = ph.phoneable_id AND ph.phoneable_type = 'PjProfile'
    GROUP BY pjp.person_id
),
AllEmails AS (
    -- Agrega todos os emails de um perfil PJ em uma única string
    SELECT
        pjp.person_id,
        STRING_AGG(em.email_address, ', ') AS EmailAddresses
    FROM core.pj_profiles pjp
    JOIN core.emails em ON pjp.id = em.emailable_id AND em.emailable_type = 'PjProfile'
    GROUP BY pjp.person_id
)
SELECT
    -- Dados da Conta (Company)
    c.id AS CompanyId,
    c.access_status AS CompanyAccessStatus,

    -- Dados da Pessoa Raiz e Perfil PJ
    p.id AS PersonId,
    pjp.id AS PjProfileId,
    p.name AS RazaoSocial,

    -- Campos Sensíveis com Mascaramento LGPD
    CASE
        WHEN [core].[fn_CanUserUnmaskData]() = 1 THEN pjp.trade_name
        ELSE LEFT(ISNULL(pjp.trade_name, ''), 3) + '...'
    END AS NomeFantasia,
    CASE
        WHEN [core].[fn_CanUserUnmaskData]() = 1 THEN pjp.tax_id
        ELSE LEFT(pjp.tax_id, 2) + '.' + REPLICATE('*', 3) + '.' + REPLICATE('*', 3) + '/' + REPLICATE('*', 4) + '-' + RIGHT(pjp.tax_id, 2)
    END AS CNPJ,

    -- Dados do Endereço Principal
    addr.street AS PrincipalStreet,
    addr.number AS PrincipalNumber,
    addr.neighborhood AS PrincipalNeighborhood,
    addr.city AS PrincipalCity,
    addr.state AS PrincipalState,
    addr.zip_code AS PrincipalZipCode,

    -- Dados de Contato Agregados
    phones.PhoneNumbers,
    emails.EmailAddresses,

    -- Datas
    pjp.incorporation_date,
    c.created_at AS CompanyCreatedAt

FROM
    [core].[companies] c
-- Usamos LEFT JOIN para garantir que empresas em estado de cadastro (person_id = NULL) ainda apareçam
LEFT JOIN [core].[people] p ON c.person_id = p.id
LEFT JOIN [core].[pj_profiles] pjp ON p.id = pjp.person_id
-- Junta apenas o endereço marcado como principal
LEFT JOIN [core].[addresses] addr ON pjp.id = addr.addressable_id AND addr.addressable_type = 'PjProfile' AND addr.is_principal = 1
-- Junta as listas de telefones e emails agregados
LEFT JOIN AllPhones phones ON p.id = phones.person_id
LEFT JOIN AllEmails emails ON p.id = emails.person_id;
GO

PRINT '✅ View [core].[vw_complete_company_data] criada/alterada com sucesso.';