-- =====================================================================================
-- Script de Debug: sp_create_company_from_json
-- Objetivo: Identificar por que a SP está fazendo rollback com CNPJ válido
-- =====================================================================================

USE pro_team_care_test;
GO

-- 1. TESTAR EXECUÇÃO DIRETA DA SP
DECLARE @jsonData NVARCHAR(MAX) = N'{
    "cnpj": "06990590000123",
    "razao_social": "HOSPITAL TESTE LTDA",
    "nome_fantasia": "HOSPITAL TESTE",
    "telefones": [
        {"number": "(11) 99999-9999", "type": "comercial", "is_whatsapp": true}
    ],
    "emails": [
        {"email": "contato@hospitalteste.com.br", "type": "comercial", "is_principal": true}
    ],
    "enderecos": [{
        "cep": "01001000",
        "logradouro": "PRAÇA DA SÉ",
        "numero": "1",
        "bairro": "SÉ",
        "cidade": "SÃO PAULO",
        "uf": "SP",
        "tipo": "comercial",
        "is_principal": true
    }]
}';

PRINT '=== EXECUTANDO SP DIRETAMENTE ===';
PRINT 'JSON Input: ' + @jsonData;

BEGIN TRY
    EXEC [core].[sp_create_company_from_json] @jsonData = @jsonData;
    PRINT '✅ SP executada com sucesso';
END TRY
BEGIN CATCH
    PRINT '❌ ERRO NA SP:';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT 'Error Procedure: ' + ISNULL(ERROR_PROCEDURE(), 'N/A');
END CATCH;

-- 2. VERIFICAR SE EMPRESA FOI CRIADA
PRINT '';
PRINT '=== VERIFICANDO CRIAÇÃO ===';
SELECT 
    c.id as company_id,
    p.name as razao_social,
    p.tax_id as cnpj,
    c.created_at
FROM core.companies c
INNER JOIN core.people p ON c.person_id = p.id
WHERE p.tax_id = '06990590000123'
ORDER BY c.created_at DESC;

-- 3. VERIFICAR CONSTRAINTS E TRIGGERS
PRINT '';
PRINT '=== VERIFICANDO CONSTRAINTS ===';
SELECT 
    tc.CONSTRAINT_NAME,
    tc.CONSTRAINT_TYPE,
    tc.TABLE_NAME,
    cc.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
LEFT JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE cc 
    ON tc.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
WHERE tc.TABLE_SCHEMA = 'core' 
    AND tc.TABLE_NAME IN ('companies', 'people', 'pj_profiles', 'addresses', 'phones', 'emails')
    AND tc.CONSTRAINT_TYPE IN ('FOREIGN KEY', 'CHECK', 'UNIQUE')
ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_TYPE;

-- 4. VERIFICAR TRIGGERS
PRINT '';
PRINT '=== VERIFICANDO TRIGGERS ===';
SELECT 
    t.name AS trigger_name,
    t.type_desc,
    t.is_disabled,
    OBJECT_NAME(t.parent_id) AS table_name
FROM sys.triggers t
WHERE OBJECT_SCHEMA_NAME(t.parent_id) = 'core'
    AND OBJECT_NAME(t.parent_id) IN ('companies', 'people', 'pj_profiles', 'addresses', 'phones', 'emails');

-- 5. VERIFICAR DADOS EXISTENTES QUE PODEM CAUSAR CONFLITO
PRINT '';
PRINT '=== VERIFICANDO CONFLITOS POTENCIAIS ===';

-- CNPJ já existe?
SELECT 'CNPJ_CONFLICT' as check_type, COUNT(*) as count
FROM core.people 
WHERE tax_id = '06990590000123' AND deleted_at IS NULL;

-- Email já existe?
SELECT 'EMAIL_CONFLICT' as check_type, COUNT(*) as count
FROM core.emails 
WHERE email = 'contato@hospitalteste.com.br' AND deleted_at IS NULL;

-- Telefone já existe?
SELECT 'PHONE_CONFLICT' as check_type, COUNT(*) as count
FROM core.phones 
WHERE number = '(11) 99999-9999' AND deleted_at IS NULL;

-- 6. TESTAR CRIAÇÃO MANUAL PASSO A PASSO
PRINT '';
PRINT '=== TESTE MANUAL PASSO A PASSO ===';

BEGIN TRANSACTION;

BEGIN TRY
    -- Criar Person
    DECLARE @person_id INT;
    INSERT INTO core.people (name, tax_id, person_type, is_active)
    VALUES ('HOSPITAL TESTE LTDA', '06990590000123', 'PJ', 1);
    SET @person_id = SCOPE_IDENTITY();
    PRINT '✅ Person criada: ID = ' + CAST(@person_id AS VARCHAR);

    -- Criar Company
    DECLARE @company_id INT;
    INSERT INTO core.companies (person_id, access_status, is_active)
    VALUES (@person_id, 'active', 1);
    SET @company_id = SCOPE_IDENTITY();
    PRINT '✅ Company criada: ID = ' + CAST(@company_id AS VARCHAR);

    -- Criar PJ Profile
    DECLARE @pj_profile_id INT;
    INSERT INTO core.pj_profiles (person_id, trade_name, is_active)
    VALUES (@person_id, 'HOSPITAL TESTE', 1);
    SET @pj_profile_id = SCOPE_IDENTITY();
    PRINT '✅ PJ Profile criado: ID = ' + CAST(@pj_profile_id AS VARCHAR);

    -- Criar Address
    DECLARE @address_id INT;
    INSERT INTO core.addresses (company_id, street, number, neighborhood, city, state, zip_code, address_type, is_principal, is_active)
    VALUES (@company_id, 'PRAÇA DA SÉ', '1', 'SÉ', 'SÃO PAULO', 'SP', '01001000', 'comercial', 1, 1);
    SET @address_id = SCOPE_IDENTITY();
    PRINT '✅ Address criado: ID = ' + CAST(@address_id AS VARCHAR);

    -- Criar Phone
    DECLARE @phone_id INT;
    INSERT INTO core.phones (company_id, number, phone_type, is_whatsapp, is_active)
    VALUES (@company_id, '(11) 99999-9999', 'comercial', 1, 1);
    SET @phone_id = SCOPE_IDENTITY();
    PRINT '✅ Phone criado: ID = ' + CAST(@phone_id AS VARCHAR);

    -- Criar Email
    DECLARE @email_id INT;
    INSERT INTO core.emails (company_id, email, email_type, is_principal, is_active)
    VALUES (@company_id, 'contato@hospitalteste.com.br', 'comercial', 1, 1);
    SET @email_id = SCOPE_IDENTITY();
    PRINT '✅ Email criado: ID = ' + CAST(@email_id AS VARCHAR);

    PRINT '✅ CRIAÇÃO MANUAL COMPLETA - FAZENDO COMMIT';
    COMMIT;

END TRY
BEGIN CATCH
    PRINT '❌ ERRO NA CRIAÇÃO MANUAL:';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    ROLLBACK;
END CATCH;

-- 7. VERIFICAR RESULTADO FINAL
PRINT '';
PRINT '=== RESULTADO FINAL ===';
SELECT 
    c.id as company_id,
    p.id as person_id,
    pj.id as pj_profile_id,
    p.name as razao_social,
    pj.trade_name as nome_fantasia,
    p.tax_id as cnpj,
    c.created_at
FROM core.companies c
INNER JOIN core.people p ON c.person_id = p.id
LEFT JOIN core.pj_profiles pj ON pj.person_id = p.id
WHERE p.tax_id = '06990590000123'
ORDER BY c.created_at DESC;
