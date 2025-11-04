-- Script para verificar se as atualizações da view foram aplicadas corretamente
-- Execute este script APÓS executar update_company_view_cnpj_masking.sql

USE [pro_team_care];
GO

PRINT '=== VERIFICAÇÃO DAS ATUALIZAÇÕES DA VIEW ===';
GO

-- 1. Verificar se a view existe e está atualizada
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    PRINT '✅ View vw_complete_company_data existe';

    -- Verificar definição da view (procurar por mascaramento)
    IF EXISTS (
        SELECT * FROM sys.sql_modules
        WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]')
        AND definition LIKE '%***%'
    )
    BEGIN
        PRINT '✅ View contém lógica de mascaramento de CNPJ';
    END
    ELSE
    BEGIN
        PRINT '❌ View NÃO contém lógica de mascaramento de CNPJ';
    END

    -- Verificar se usa FOR JSON PATH
    IF EXISTS (
        SELECT * FROM sys.sql_modules
        WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]')
        AND definition LIKE '%FOR JSON PATH%'
    )
    BEGIN
        PRINT '✅ View usa FOR JSON PATH para telefones/emails';
    END
    ELSE
    BEGIN
        PRINT '❌ View NÃO usa FOR JSON PATH para telefones/emails';
    END
END
ELSE
BEGIN
    PRINT '❌ View vw_complete_company_data NÃO existe';
END
GO

-- 2. Testar dados retornados
PRINT '';
PRINT '=== TESTE DE DADOS RETORNADOS ===';
GO

SELECT TOP 2
    CompanyId,
    CNPJ,
    CASE
        WHEN CNPJ LIKE '[0-9][0-9].***.***/****-[0-9][0-9]' THEN '✅ MASCARADO_CORRETAMENTE'
        WHEN CNPJ LIKE '**.***.***/****-**' THEN '⚠️ MASCARADO_GENERICO'
        WHEN CNPJ LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]' THEN '❌ NAO_MASCARADO'
        ELSE '❓ FORMATO_DESCONHECIDO'
    END AS Status_CNPJ,

    CASE WHEN ISJSON(PhoneNumbers) = 1 THEN '✅ JSON_VALIDO' ELSE '❌ JSON_INVALIDO' END AS Status_Telefones,
    CASE WHEN ISJSON(EmailAddresses) = 1 THEN '✅ JSON_VALIDO' ELSE '❌ JSON_INVALIDO' END AS Status_Emails,

    PhoneNumbers,
    EmailAddresses

FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

-- 3. Verificar permissões
PRINT '';
PRINT '=== VERIFICAÇÃO DE PERMISSÕES ===';
GO

DECLARE @AppUser NVARCHAR(100) = 'app_user'; -- Ajuste para o usuário da aplicação

IF EXISTS (SELECT * FROM sys.database_principals WHERE name = @AppUser)
BEGIN
    -- Verificar permissões na view
    IF EXISTS (
        SELECT * FROM sys.database_permissions
        WHERE grantee_principal_id = (SELECT principal_id FROM sys.database_principals WHERE name = @AppUser)
        AND major_id = OBJECT_ID(N'[core].[vw_complete_company_data]')
        AND permission_name = 'SELECT'
        AND state_desc = 'GRANT'
    )
    BEGIN
        PRINT '✅ Usuário ' + @AppUser + ' tem SELECT na view vw_complete_company_data';
    END
    ELSE
    BEGIN
        PRINT '❌ Usuário ' + @AppUser + ' NÃO tem SELECT na view vw_complete_company_data';
    END

    -- Verificar se NÃO tem permissões nas tabelas base (segurança)
    DECLARE @HasBaseTableAccess INT = 0;

    IF EXISTS (
        SELECT * FROM sys.database_permissions
        WHERE grantee_principal_id = (SELECT principal_id FROM sys.database_principals WHERE name = @AppUser)
        AND major_id IN (OBJECT_ID(N'[core].[companies]'), OBJECT_ID(N'[core].[pj_profiles]'), OBJECT_ID(N'[core].[people]'))
        AND permission_name = 'SELECT'
        AND state_desc = 'GRANT'
    )
    BEGIN
        SET @HasBaseTableAccess = 1;
    END

    IF @HasBaseTableAccess = 0
    BEGIN
        PRINT '✅ Usuário ' + @AppUser + ' NÃO tem acesso direto às tabelas base (segurança OK)';
    END
    ELSE
    BEGIN
        PRINT '⚠️ Usuário ' + @AppUser + ' TEM acesso direto às tabelas base (verificar segurança)';
    END
END
ELSE
BEGIN
    PRINT '❌ Usuário ' + @AppUser + ' não existe no banco';
END
GO

PRINT '';
PRINT '=== RESUMO DA VERIFICAÇÃO ===';
PRINT 'Se todos os itens acima estiverem marcados com ✅, as correções foram aplicadas com sucesso.';
PRINT 'Caso contrário, execute novamente o script update_company_view_cnpj_masking.sql';
GO