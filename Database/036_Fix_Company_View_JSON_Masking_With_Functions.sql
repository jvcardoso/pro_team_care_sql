-- Script para CORREÇÃO DEFINITIVA da view vw_complete_company_data
-- FORÇA a recriação da view com JSON correto E MASCARAMENTO LGPD
-- 1. Cria Funções de Mascaramento
-- 2. Recria a View usando as Funções

USE [pro_team_care];
GO

-- ===========================================
-- 1. CRIAR FUNÇÕES DE MASCARAMENTO REUTILIZÁVEIS
-- ===========================================

-- Função para mascarar Email (ex: u***@dominio.com)
IF OBJECT_ID (N'[core].[fn_MaskEmail]', N'FN') IS NOT NULL
    DROP FUNCTION [core].[fn_MaskEmail];
GO
CREATE FUNCTION [core].[fn_MaskEmail] (@email VARCHAR(255))
RETURNS VARCHAR(255)
AS
BEGIN
    IF @email IS NULL OR CHARINDEX('@', @email) = 0
        RETURN @email;
    RETURN SUBSTRING(@email, 1, 1) + '***@' + SUBSTRING(@email, CHARINDEX('@', @email) + 1, LEN(@email));
END;
GO

-- Função para mascarar Telefone (ex: 11*****5678)
IF OBJECT_ID (N'[core].[fn_MaskPhone]', N'FN') IS NOT NULL
    DROP FUNCTION [core].[fn_MaskPhone];
GO
CREATE FUNCTION [core].[fn_MaskPhone] (@phone VARCHAR(20))
RETURNS VARCHAR(20)
AS
BEGIN
    -- Remove formatação (caso a view não tenha limpado)
    SET @phone = REPLACE(REPLACE(REPLACE(REPLACE(@phone, '(', ''), ')', ''), ' ', ''), '-', '');
    IF @phone IS NULL OR LEN(@phone) < 9
        RETURN @phone;
    -- Mostra os 2 primeiros e os 4 últimos
    RETURN SUBSTRING(@phone, 1, 2) + '*****' + SUBSTRING(@phone, LEN(@phone) - 3, 4);
END;
GO

-- Função para mascarar Endereço/Rua (ex: Rua A***)
IF OBJECT_ID (N'[core].[fn_MaskStreet]', N'FN') IS NOT NULL
    DROP FUNCTION [core].[fn_MaskStreet];
GO
CREATE FUNCTION [core].[fn_MaskStreet] (@street VARCHAR(255))
RETURNS VARCHAR(255)
AS
BEGIN
    IF @street IS NULL OR LEN(@street) < 4
        RETURN @street;
    -- Mostra as 3 primeiras letras
    RETURN SUBSTRING(@street, 1, 3) + '***';
END;
GO

-- Função para mascarar Bairro (ex: Bairro C***)
IF OBJECT_ID (N'[core].[fn_MaskNeighborhood]', N'FN') IS NOT NULL
    DROP FUNCTION [core].[fn_MaskNeighborhood];
GO
CREATE FUNCTION [core].[fn_MaskNeighborhood] (@neighborhood VARCHAR(100))
RETURNS VARCHAR(100)
AS
BEGIN
    IF @neighborhood IS NULL OR LEN(@neighborhood) < 4
        RETURN @neighborhood;
    -- Mostra as 3 primeiras letras
    RETURN SUBSTRING(@neighborhood, 1, 3) + '***';
END;
GO

-- Função para mascarar CEP (ex: 12***-***)
IF OBJECT_ID (N'[core].[fn_MaskZipCode]', N'FN') IS NOT NULL
    DROP FUNCTION [core].[fn_MaskZipCode];
GO
CREATE FUNCTION [core].[fn_MaskZipCode] (@zip_code VARCHAR(10))
RETURNS VARCHAR(10)
AS
BEGIN
    IF @zip_code IS NULL OR LEN(@zip_code) < 5
        RETURN @zip_code;
    -- Mostra os 2 primeiros dígitos do CEP
    RETURN SUBSTRING(@zip_code, 1, 2) + '***-***';
END;
GO

PRINT '✓ Funções de mascaramento LGPD criadas/atualizadas';
GO

-- ===========================================
-- 2. RECRIAÇÃO COMPLETA DA VIEW
-- ===========================================

-- Remover view existente se existir
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    DROP VIEW [core].[vw_complete_company_data];
    PRINT '✓ View vw_complete_company_data removida';
END
GO

-- Recriar view com JSON correto E MASCARAMENTO LGPD
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

    -- Endereço principal (MASCARADO)
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

PRINT '✓ View vw_complete_company_data recriada com MASCARAMENTO LGPD e JSON correto';
GO

-- ===========================================
-- 3. TESTE IMEDIATO DA VIEW
-- ===========================================

PRINT '';
PRINT '=== TESTE DA VIEW RECRIADA ===';
GO

-- Validação de JSON e Mascaramento
SELECT TOP 5
    CompanyId,
    CNPJ,

    -- Status CNPJ
    CASE
        WHEN CNPJ LIKE '[0-9][0-9].***.***/****-[0-9][0-9]' THEN '✅ MASCARADO_CNPJ'
        WHEN CNPJ LIKE '**.***.***/****-**' THEN '✅ MASCARADO_CNPJ_GEN'
        ELSE '❌ FORMATO_CNPJ_INVALIDO'
    END AS Status_CNPJ,

    -- Status JSON
    CASE WHEN ISJSON(PhoneNumbers) = 1 THEN '✅ JSON_VALIDO' ELSE '❌ JSON_INVALIDO' END AS Status_Telefones,
    CASE WHEN ISJSON(EmailAddresses) = 1 THEN '✅ JSON_VALIDO' ELSE '❌ JSON_INVALIDO' END AS Status_Emails,

    -- Preview dos dados MASCARADOS
    LEFT(PhoneNumbers, 100) + '...' AS PhoneNumbers_Preview,
    LEFT(EmailAddresses, 100) + '...' AS EmailAddresses_Preview,
    PrincipalStreet,
    PrincipalNeighborhood,
    PrincipalZipCode

FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

PRINT '';
PRINT '=== INSTRUÇÕES ===';
PRINT 'Se todos os status mostrarem ✅, a View está correta e segura (LGPD).';
PRINT 'O próximo passo é criar os Stored Procedures e Endpoints de REVELAÇÃO (LGPD).';
GO