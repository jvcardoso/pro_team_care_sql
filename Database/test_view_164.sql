-- Teste da view vw_complete_company_data para CompanyId 164
-- Executar no SQL Server Management Studio ou similar

-- Verificar se a empresa existe na tabela base
SELECT TOP 1 id, person_id, access_status, created_at FROM [core].[companies]
WHERE id = 164;

-- Verificar se há pessoa jurídica
SELECT TOP 1 id, person_id, tax_id, name, trade_name FROM [core].[pj_profiles]
WHERE person_id IN (SELECT person_id FROM [core].[companies] WHERE id = 164);

-- Verificar se há endereço principal
SELECT TOP 1 id, company_id, street, number, neighborhood, city, state, zip_code, is_principal
FROM [core].[addresses]
WHERE company_id = 164 AND is_principal = 1;

-- Testar a view
SELECT TOP 1
    CompanyId,
    PersonId,
    RazaoSocial,
    NomeFantasia,
    CNPJ,
    PrincipalAddressId,
    PrincipalStreet,
    PrincipalNumber,
    PrincipalNeighborhood,
    PrincipalCity,
    PrincipalState,
    PrincipalZipCode,
    PhoneNumbers,
    EmailAddresses,
    CompanyCreatedAt
FROM [core].[vw_complete_company_data]
WHERE CompanyId = 164;

-- Verificar se há dados JSON válidos
SELECT
    CompanyId,
    ISJSON(PhoneNumbers) as PhoneNumbers_IsValid,
    ISJSON(EmailAddresses) as EmailAddresses_IsValid,
    LEN(PhoneNumbers) as PhoneNumbers_Length,
    LEN(EmailAddresses) as EmailAddresses_Length
FROM [core].[vw_complete_company_data]
WHERE CompanyId = 164;