-- Script para testar a view vw_complete_company_data após as correções
-- Execute este script no SQL Server para verificar se o CNPJ está mascarado
-- e se telefones/emails estão retornando JSON nativo

USE [pro_team_care];
GO

-- Teste 1: Verificar estrutura da view
SELECT TOP 1 * FROM [core].[vw_complete_company_data];
GO

-- Teste 2: Verificar especificamente CNPJ e campos JSON
SELECT
    CompanyId,
    CNPJ,
    PhoneNumbers,
    EmailAddresses
FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

-- Teste 3: Verificar se CNPJ está mascarado (deve mostrar formato XX.***.***/XXXX-XX)
SELECT
    CompanyId,
    CNPJ,
    CASE
        WHEN CNPJ LIKE '[0-9][0-9].***.***/[0-9][0-9][0-9][0-9]-[0-9][0-9]' THEN 'MASCARADO_CORRETAMENTE'
        WHEN CNPJ = '**.***.***/****-**' THEN 'MASCARADO_GENERICO'
        ELSE 'NAO_MASCARADO'
    END AS Status_Mascaramento
FROM [core].[vw_complete_company_data];
GO

-- Teste 4: Verificar se PhoneNumbers é JSON válido
SELECT
    CompanyId,
    PhoneNumbers,
    ISJSON(PhoneNumbers) as IsValidJson
FROM [core].[vw_complete_company_data];
GO

-- Teste 5: Verificar se EmailAddresses é JSON válido
SELECT
    CompanyId,
    EmailAddresses,
    ISJSON(EmailAddresses) as IsValidJson
FROM [core].[vw_complete_company_data];
GO