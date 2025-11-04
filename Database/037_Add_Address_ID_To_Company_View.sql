-- Script para adicionar ID do endereço principal na view vw_complete_company_data
-- Necessário para funcionalidade LGPD de revelação de endereços

IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    DROP VIEW [core].[vw_complete_company_data];
    PRINT '✓ View vw_complete_company_data removida para atualização';
END
GO

-- Recriar view com ID do endereço principal incluído
CREATE VIEW [core].[vw_complete_company_data]
AS
SELECT
    c.id AS CompanyId,
    c.access_status AS CompanyAccessStatus,
    c.person_id AS PersonId,
    pj.id AS PjProfileId,
    p.name AS RazaoSocial,
    pj.trade_name AS NomeFantasia,

    -- CNPJ mascarado (Database-First Presentation)
    CASE
        WHEN LEN(LTRIM(RTRIM(ISNULL(pj.tax_id, '')))) = 14 THEN
            SUBSTRING(pj.tax_id, 1, 2) + '.***.***/****-' + SUBSTRING(pj.tax_id, 13, 2)
        ELSE
            '**.***.***/****-**'
    END AS CNPJ,

    -- Endereço principal (MASCARADO) - AGORA COM ID
    addr.id AS PrincipalAddressId,  -- ← NOVO: ID do endereço para LGPD
    [core].[fn_MaskStreet](addr.street) AS PrincipalStreet,
    addr.number AS PrincipalNumber, -- Número não é PII sensível neste contexto
    [core].[fn_MaskNeighborhood](addr.neighborhood) AS PrincipalNeighborhood,
    addr.city AS PrincipalCity, -- Cidade/Estado não são PII sensíveis
    addr.state AS PrincipalState,
    [core].[fn_MaskZipCode](addr.zip_code) AS PrincipalZipCode,

    -- Telefones como JSON ARRAY (MASCARADO)
    ISNULL((
        SELECT
            ph.id, -- ID é necessário para a revelação (reveal)
            -- Limpa formatação E aplica máscara
            [core].[fn_MaskPhone](ph.number) as number,
            ph.type,
            ph.is_principal
        FROM [core].[phones] ph
        WHERE ph.company_id = c.id
        FOR JSON PATH
    ), '[]') AS PhoneNumbers,

    -- Emails como JSON ARRAY (MASCARADO)
    ISNULL((
        SELECT
            em.id, -- ID é necessário para a revelação (reveal)
            -- Aplica máscara
            [core].[fn_MaskEmail](em.email_address) as email,
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

PRINT '✓ View vw_complete_company_data recriada com ID do endereço principal';
GO

-- ===========================================
-- TESTE DA VIEW ATUALIZADA
-- ===========================================

PRINT '';
PRINT '=== TESTE DA VIEW ATUALIZADA ===';
GO

-- Verificar se a coluna PrincipalAddressId foi adicionada
SELECT TOP 1
    CompanyId,
    PrincipalAddressId,
    PrincipalStreet,
    PrincipalNumber,
    PrincipalNeighborhood
FROM [core].[vw_complete_company_data]
WHERE PrincipalAddressId IS NOT NULL;
GO

PRINT '✓ Teste concluído - view atualizada com sucesso';
GO