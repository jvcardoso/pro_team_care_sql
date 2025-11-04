-- Script para CORREÇÃO DEFINITIVA da view vw_complete_company_data
-- Implementa mascaramento LGPD de CNPJ e JSON nativo para telefones/emails
-- Seguindo padrão Database-First Presentation

USE [pro_team_care];
GO

-- ===========================================
-- RECRIAÇÃO COMPLETA DA VIEW COM MASCARAMENTO LGPD
-- ===========================================

-- 1. Remover view existente se existir
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    DROP VIEW [core].[vw_complete_company_data];
    PRINT '✓ View vw_complete_company_data removida para recriação';
END
GO

-- 2. Recriar view com mascaramento correto e JSON nativo
CREATE VIEW [core].[vw_complete_company_data]
AS
SELECT
    c.id AS CompanyId,
    c.access_status AS CompanyAccessStatus,
    c.person_id AS PersonId,
    pj.id AS PjProfileId,
    p.name AS RazaoSocial,
    pj.trade_name AS NomeFantasia,

    -- CNPJ mascarado conforme LGPD (Database-First Presentation)
    -- Formato: XX.***.***/****-XX (mascara os 6 dígitos do meio)
    CASE
        WHEN LEN(LTRIM(RTRIM(ISNULL(pj.tax_id, '')))) = 14 THEN
            SUBSTRING(pj.tax_id, 1, 2) + '.***.***/****-' + SUBSTRING(pj.tax_id, 13, 2)
        ELSE
            -- CNPJ inválido ou nulo: máscara genérica
            '**.***.***/****-**'
    END AS CNPJ,

    -- Endereço principal
    addr.street AS PrincipalStreet,
    addr.number AS PrincipalNumber,
    addr.neighborhood AS PrincipalNeighborhood,
    addr.city AS PrincipalCity,
    addr.state AS PrincipalState,
    addr.zip_code AS PrincipalZipCode,

    -- Telefones como JSON ARRAY nativo (FOR JSON PATH garante formato correto)
    ISNULL((
        SELECT
            -- Limpar formatação do telefone (remover parênteses, espaços, hífens)
            REPLACE(REPLACE(REPLACE(REPLACE(ph.number, '(', ''), ')', ''), ' ', ''), '-', '') as number,
            ph.type,
            ph.is_principal
        FROM [core].[phones] ph
        WHERE ph.company_id = c.id
        FOR JSON PATH
    ), '[]') AS PhoneNumbers,

    -- Emails como JSON ARRAY nativo (FOR JSON PATH garante formato correto)
    ISNULL((
        SELECT
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

PRINT '✓ View vw_complete_company_data recriada com mascaramento LGPD e JSON correto';
PRINT '✓ CNPJ formatado como XX.***.***/****-XX';
PRINT '✓ Telefones e emails retornados como arrays JSON nativos';
GO

-- ===========================================
-- TESTE IMEDIATO DA VIEW
-- ===========================================

PRINT '';
PRINT '=== TESTE DA VIEW RECRIADA ===';
GO

-- Teste básico
SELECT TOP 2
    CompanyId,
    CNPJ,
    PhoneNumbers,
    EmailAddresses
FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

-- Validação completa
SELECT
    CompanyId,
    CNPJ,
    CASE
        WHEN CNPJ LIKE '[0-9][0-9].***.***/****-[0-9][0-9]' THEN '✅ MASCARADO_CORRETAMENTE'
        WHEN CNPJ LIKE '**.***.***/****-**' THEN '⚠️ MASCARADO_GENERICO'
        ELSE '❌ FORMATO_INVALIDO'
    END AS Status_CNPJ,

    CASE WHEN ISJSON(PhoneNumbers) = 1 THEN '✅ JSON_VALIDO' ELSE '❌ JSON_INVALIDO' END AS Status_Telefones,
    CASE WHEN ISJSON(EmailAddresses) = 1 THEN '✅ JSON_VALIDO' ELSE '❌ JSON_INVALIDO' END AS Status_Emails,

    -- Preview dos primeiros 100 caracteres
    LEFT(PhoneNumbers, 100) + CASE WHEN LEN(PhoneNumbers) > 100 THEN '...' ELSE '' END AS PhoneNumbers_Preview,
    LEFT(EmailAddresses, 100) + CASE WHEN LEN(EmailAddresses) > 100 THEN '...' ELSE '' END AS EmailAddresses_Preview

FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

PRINT '';
PRINT '=== RESULTADO ESPERADO ===';
PRINT 'Status_CNPJ: ✅ MASCARADO_CORRETAMENTE';
PRINT 'Status_Telefones: ✅ JSON_VALIDO';
PRINT 'Status_Emails: ✅ JSON_VALIDO';
PRINT '';
PRINT '=== PRÓXIMOS PASSOS ===';
PRINT '1. Se tudo estiver ✅, o problema está resolvido no banco';
PRINT '2. Reinicie o backend para limpar cache';
PRINT '3. Teste o endpoint /api/v1/companies/complete-list';
PRINT '4. Verifique se o frontend mostra CNPJs mascarados e arrays JSON corretos';
GO