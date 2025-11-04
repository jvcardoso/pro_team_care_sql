-- =================================================================================
-- Script:         014_Create_Security_Function.sql (v2.0 - Corrigido)
-- Descrição:
-- v2.0 - Altera a função para verificar a flag [can_unmask_pii] na tabela
--        de roles, em vez de uma lista de nomes de papéis hardcoded.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER FUNCTION [core].[fn_CanUserUnmaskData]()
RETURNS BIT
AS
BEGIN
    DECLARE @current_user_id BIGINT = TRY_CAST(SESSION_CONTEXT(N'user_id') AS BIGINT);

    IF @current_user_id IS NULL
        RETURN 0;

    -- CORREÇÃO: A lógica agora verifica a flag explícita [can_unmask_pii]
    IF EXISTS (
        SELECT 1
        FROM [core].[user_roles] ur
        JOIN [core].[roles] r ON ur.role_id = r.id
        WHERE
            ur.user_id = @current_user_id
            AND ur.status = 'active'
            AND r.can_unmask_pii = 1 -- Verifica a flag, não o nome!
    )
        RETURN 1; -- Permissão concedida

    RETURN 0; -- Permissão negada
END;
GO

PRINT 'Função de segurança [core].[fn_CanUserUnmaskData] atualizada com sucesso.';
