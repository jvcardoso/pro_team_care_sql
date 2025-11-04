-- ===========================================
-- DIAGNÓSTICO COMPLETO: Empresa 164 e Endereços
-- ===========================================
-- Execute este script no SQL Server Management Studio
-- ou Azure Data Studio para identificar o problema exato

USE pro_team_care;
GO

PRINT '===========================================';
PRINT '🔍 DIAGNÓSTICO COMPLETO - EMPRESA 164';
PRINT '===========================================';
GO

-- ===========================================
-- 1. VERIFICAR SE EMPRESA EXISTE
-- ===========================================
PRINT '';
PRINT '1️⃣ VERIFICANDO SE EMPRESA 164 EXISTE:';
PRINT '--------------------------------------';
GO

IF EXISTS (SELECT 1 FROM [core].[companies] WHERE id = 164)
BEGIN
    PRINT '✅ Empresa 164 EXISTE na tabela companies';
    SELECT
        id,
        person_id,
        access_status,
        created_at,
        updated_at
    FROM [core].[companies]
    WHERE id = 164;
END
ELSE
BEGIN
    PRINT '❌ Empresa 164 NÃO EXISTE na tabela companies';
    PRINT '   → Problema: Empresa não encontrada';
    SELECT TOP 5 id, person_id, access_status FROM [core].[companies] ORDER BY id DESC;
END
GO

-- ===========================================
-- 2. VERIFICAR ENDEREÇOS DA EMPRESA
-- ===========================================
PRINT '';
PRINT '2️⃣ VERIFICANDO ENDEREÇOS DA EMPRESA 164:';
PRINT '-----------------------------------------';
GO

DECLARE @AddressCount INT = (SELECT COUNT(*) FROM [core].[addresses] WHERE company_id = 164);

IF @AddressCount > 0
BEGIN
    PRINT '✅ Empresa 164 TEM ENDEREÇOS (' + CAST(@AddressCount AS VARCHAR) + ' encontrado(s))';
    SELECT
        id,
        company_id,
        street,
        number,
        neighborhood,
        city,
        state,
        zip_code,
        is_principal,
        created_at
    FROM [core].[addresses]
    WHERE company_id = 164
    ORDER BY is_principal DESC, id;
END
ELSE
BEGIN
    PRINT '❌ Empresa 164 NÃO TEM ENDEREÇOS';
    PRINT '   → Problema: Nenhum endereço cadastrado';
END
GO

-- ===========================================
-- 3. VERIFICAR ENDEREÇO PRINCIPAL
-- ===========================================
PRINT '';
PRINT '3️⃣ VERIFICANDO ENDEREÇO PRINCIPAL:';
PRINT '-----------------------------------';
GO

DECLARE @PrincipalAddressId INT = (
    SELECT id FROM [core].[addresses]
    WHERE company_id = 164 AND is_principal = 1
);

IF @PrincipalAddressId IS NOT NULL
BEGIN
    PRINT '✅ Empresa 164 TEM ENDEREÇO PRINCIPAL (ID: ' + CAST(@PrincipalAddressId AS VARCHAR) + ')';
    SELECT
        id,
        street,
        number,
        neighborhood,
        city,
        state,
        zip_code
    FROM [core].[addresses]
    WHERE id = @PrincipalAddressId;
END
ELSE
BEGIN
    PRINT '❌ Empresa 164 NÃO TEM ENDEREÇO PRINCIPAL';
    PRINT '   → Problema: Endereço principal não definido';
END
GO

-- ===========================================
-- 4. VERIFICAR VIEW VW_COMPLETE_COMPANY_DATA
-- ===========================================
PRINT '';
PRINT '4️⃣ VERIFICANDO VIEW VW_COMPLETE_COMPANY_DATA:';
PRINT '---------------------------------------------';
GO

-- Verificar se view existe
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    PRINT '✅ View vw_complete_company_data EXISTE';

    -- Verificar se empresa 164 está na view
    IF EXISTS (SELECT 1 FROM [core].[vw_complete_company_data] WHERE CompanyId = 164)
    BEGIN
        PRINT '✅ Empresa 164 EXISTE na view vw_complete_company_data';
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
            CompanyCreatedAt
        FROM [core].[vw_complete_company_data]
        WHERE CompanyId = 164;
    END
    ELSE
    BEGIN
        PRINT '❌ Empresa 164 NÃO EXISTE na view vw_complete_company_data';
        PRINT '   → Problema: View não inclui empresa 164';
    END

    -- Verificar estrutura da view (colunas)
    PRINT '';
    PRINT '📋 ESTRUTURA DA VIEW:';
    SELECT
        c.name AS ColumnName,
        t.name AS DataType,
        c.max_length,
        c.is_nullable
    FROM sys.columns c
    INNER JOIN sys.views v ON c.object_id = v.object_id
    INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
    WHERE v.name = 'vw_complete_company_data'
    ORDER BY c.column_id;

END
ELSE
BEGIN
    PRINT '❌ View vw_complete_company_data NÃO EXISTE';
    PRINT '   → Problema crítico: View não foi criada';
END
GO

-- ===========================================
-- 5. VERIFICAR COLUNA PrincipalAddressId
-- ===========================================
PRINT '';
PRINT '5️⃣ VERIFICANDO COLUNA PrincipalAddressId:';
PRINT '------------------------------------------';
GO

IF EXISTS (
    SELECT 1
    FROM sys.columns c
    INNER JOIN sys.views v ON c.object_id = v.object_id
    WHERE v.name = 'vw_complete_company_data'
    AND c.name = 'PrincipalAddressId'
)
BEGIN
    PRINT '✅ Coluna PrincipalAddressId EXISTE na view';

    -- Verificar valores para empresa 164
    DECLARE @ViewAddressId INT = (
        SELECT PrincipalAddressId
        FROM [core].[vw_complete_company_data]
        WHERE CompanyId = 164
    );

    IF @ViewAddressId IS NOT NULL
    BEGIN
        PRINT '✅ Empresa 164 TEM PrincipalAddressId na view (ID: ' + CAST(@ViewAddressId AS VARCHAR) + ')';

        -- Verificar se o endereço existe
        IF EXISTS (SELECT 1 FROM [core].[addresses] WHERE id = @ViewAddressId)
        BEGIN
            PRINT '✅ Endereço referenciado EXISTE na tabela addresses';
        END
        ELSE
        BEGIN
            PRINT '❌ Endereço referenciado NÃO EXISTE na tabela addresses';
            PRINT '   → Problema: View aponta para endereço inexistente';
        END
    END
    ELSE
    BEGIN
        PRINT '❌ Empresa 164 TEM PrincipalAddressId = NULL na view';
        PRINT '   → Problema: Empresa não tem endereço principal';
    END
END
ELSE
BEGIN
    PRINT '❌ Coluna PrincipalAddressId NÃO EXISTE na view';
    PRINT '   → Problema: View não foi atualizada (execute EXECUTE_037.sql)';
END
GO

-- ===========================================
-- 6. DIAGNÓSTICO FINAL
-- ===========================================
PRINT '';
PRINT '===========================================';
PRINT '🏁 DIAGNÓSTICO FINAL';
PRINT '===========================================';
GO

DECLARE @CompanyExists BIT = CASE WHEN EXISTS (SELECT 1 FROM [core].[companies] WHERE id = 164) THEN 1 ELSE 0 END;
DECLARE @AddressExists BIT = CASE WHEN EXISTS (SELECT 1 FROM [core].[addresses] WHERE company_id = 164) THEN 1 ELSE 0 END;
DECLARE @PrincipalExists BIT = CASE WHEN EXISTS (SELECT 1 FROM [core].[addresses] WHERE company_id = 164 AND is_principal = 1) THEN 1 ELSE 0 END;
DECLARE @ViewExists BIT = CASE WHEN EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]')) THEN 1 ELSE 0 END;
DECLARE @ViewHasCompany BIT = CASE WHEN EXISTS (SELECT 1 FROM [core].[vw_complete_company_data] WHERE CompanyId = 164) THEN 1 ELSE 0 END;
DECLARE @ViewHasColumn BIT = CASE WHEN EXISTS (
    SELECT 1 FROM sys.columns c
    INNER JOIN sys.views v ON c.object_id = v.object_id
    WHERE v.name = 'vw_complete_company_data' AND c.name = 'PrincipalAddressId'
) THEN 1 ELSE 0 END;

PRINT '📊 STATUS GERAL:';
PRINT '----------------';
PRINT 'Empresa existe: ' + CASE WHEN @CompanyExists = 1 THEN '✅' ELSE '❌' END;
PRINT 'Tem endereços: ' + CASE WHEN @AddressExists = 1 THEN '✅' ELSE '❌' END;
PRINT 'Tem endereço principal: ' + CASE WHEN @PrincipalExists = 1 THEN '✅' ELSE '❌' END;
PRINT 'View existe: ' + CASE WHEN @ViewExists = 1 THEN '✅' ELSE '❌' END;
PRINT 'Empresa na view: ' + CASE WHEN @ViewHasCompany = 1 THEN '✅' ELSE '❌' END;
PRINT 'Coluna PrincipalAddressId existe: ' + CASE WHEN @ViewHasColumn = 1 THEN '✅' ELSE '❌' END;

PRINT '';
PRINT '🎯 PROBLEMA IDENTIFICADO:';

IF @CompanyExists = 0
    PRINT '❌ EMPRESA 164 NÃO EXISTE - Verificar ID correto';
ELSE IF @AddressExists = 0
    PRINT '❌ EMPRESA SEM ENDEREÇOS - Precisa cadastrar endereço';
ELSE IF @PrincipalExists = 0
    PRINT '❌ SEM ENDEREÇO PRINCIPAL - Definir endereço principal';
ELSE IF @ViewExists = 0
    PRINT '❌ VIEW NÃO EXISTE - Executar scripts de criação';
ELSE IF @ViewHasCompany = 0
    PRINT '❌ EMPRESA NÃO NA VIEW - Recriar view';
ELSE IF @ViewHasColumn = 0
    PRINT '❌ COLUNA AUSENTE - Executar EXECUTE_037.sql';
ELSE
    PRINT '✅ TUDO OK - Problema pode estar no frontend';

PRINT '';
PRINT '🔧 SOLUÇÕES SUGERIDAS:';

IF @CompanyExists = 0
    PRINT '• Verificar se o ID da empresa está correto';
ELSE IF @AddressExists = 0
    PRINT '• Cadastrar endereço para a empresa 164';
ELSE IF @PrincipalExists = 0
    PRINT '• Definir um endereço como principal (is_principal = 1)';
ELSE IF @ViewExists = 0
    PRINT '• Executar scripts de criação da view (023_Create_Complete_Company_View.sql)';
ELSE IF @ViewHasCompany = 0
    PRINT '• Recriar a view vw_complete_company_data';
ELSE IF @ViewHasColumn = 0
    PRINT '• Executar Database/EXECUTE_037.sql para adicionar PrincipalAddressId';
ELSE
    PRINT '• Verificar logs do backend para erros específicos';

GO

PRINT '';
PRINT '✅ DIAGNÓSTICO CONCLUÍDO';
PRINT 'Execute as correções sugeridas acima.';
GO
