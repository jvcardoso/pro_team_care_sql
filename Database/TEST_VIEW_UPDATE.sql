-- Teste rápido após atualização da View
-- Execute este script para confirmar que a correção funcionou

USE pro_team_care;
GO

PRINT '=== TESTE RÁPIDO APÓS ATUALIZAÇÃO ===';
GO

-- Verificar se coluna PrincipalAddressId existe agora
IF EXISTS (
    SELECT 1
    FROM sys.columns c
    INNER JOIN sys.views v ON c.object_id = v.object_id
    WHERE v.name = 'vw_complete_company_data'
    AND c.name = 'PrincipalAddressId'
)
BEGIN
    PRINT '✅ SUCESSO: Coluna PrincipalAddressId existe na view';
END
ELSE
BEGIN
    PRINT '❌ FALHA: Coluna PrincipalAddressId ainda não existe';
END
GO

-- Testar dados da empresa 164
PRINT '';
PRINT '=== DADOS DA EMPRESA 164 ===';
GO

SELECT TOP 1
    CompanyId,
    PrincipalAddressId,
    PrincipalStreet,
    PrincipalNumber,
    PrincipalNeighborhood,
    PrincipalCity,
    PrincipalState,
    PrincipalZipCode
FROM [core].[vw_complete_company_data]
WHERE CompanyId = 164;

-- Verificar se o endereço referenciado existe
DECLARE @AddressId INT = (
    SELECT PrincipalAddressId
    FROM [core].[vw_complete_company_data]
    WHERE CompanyId = 164
);

IF @AddressId IS NOT NULL
BEGIN
    PRINT '';
    PRINT '=== VERIFICAÇÃO DO ENDEREÇO REFERENCIADO ===';
    PRINT 'ID do endereço principal na view: ' + CAST(@AddressId AS VARCHAR);

    IF EXISTS (SELECT 1 FROM [core].[addresses] WHERE id = @AddressId)
    BEGIN
        PRINT '✅ SUCESSO: Endereço referenciado existe na tabela addresses';

        SELECT
            id,
            company_id,
            street,
            number,
            neighborhood,
            city,
            state,
            zip_code,
            is_principal
        FROM [core].[addresses]
        WHERE id = @AddressId;
    END
    ELSE
    BEGIN
        PRINT '❌ ERRO: Endereço referenciado NÃO existe na tabela addresses';
    END
END
ELSE
BEGIN
    PRINT '❌ ERRO: PrincipalAddressId é NULL na view';
END

GO

PRINT '';
PRINT '=== TESTE CONCLUÍDO ===';
PRINT 'Se tudo estiver ✅, a correção funcionou!';
GO