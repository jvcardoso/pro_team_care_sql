-- =================================================================================
-- Script:         apoio_007_Test_sp_get_user_me_data.sql
-- Projeto:        Pro Team Care
-- Data:           22/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Executa e valida a Stored Procedure [sp_get_user_me_data] para depurar
-- o erro 500 da API /auth/me.
-- =================================================================================

-- **********************************************************************************
-- ****** CONFIGURE O ID DO USUÁRIO QUE VOCÊ QUER TESTAR AQUI         ******
-- **********************************************************************************
DECLARE @TestUserID BIGINT = 1; -- 1 para o 'admin', 2 para o 'atendente'
-- **********************************************************************************


SET NOCOUNT ON;
PRINT '--- Iniciando validação da SP [sp_get_user_me_data] para o User ID: ' + CAST(@TestUserID AS VARCHAR) + ' ---';

-- PASSO 1: Simular o login do usuário definindo o contexto da sessão
PRINT CHAR(10) + '--- Passo 1: Definindo SESSION_CONTEXT ---';
EXEC sp_set_session_context @key = N'user_id', @value = @TestUserID;
PRINT 'Contexto da sessão definido para user_id = ' + CAST(@TestUserID AS VARCHAR);


-- PASSO 2: Executar a Stored Procedure
PRINT CHAR(10) + '--- Passo 2: Executando a Stored Procedure... ---';
PRINT 'A execução deve retornar DOIS conjuntos de resultados (Result Sets).';

EXEC [core].[sp_get_user_me_data] @user_id_input = @TestUserID;
GO -- Usamos GO para garantir que a procedure termine antes da verificação


-- PASSO 3: Verificar se o log de auditoria foi criado
PRINT CHAR(10) + '--- Passo 3: Verificando o Log de Auditoria no banco pro_team_care_logs ---';
PRINT 'A consulta abaixo deve retornar UM registro de log para a ação "VIEW".';

-- Buscando o ID do usuário de teste novamente no novo lote
DECLARE @TestUserID BIGINT = 1; -- 1 para o 'admin', 2 para o 'atendente'

SELECT TOP 1
    id,
    user_id,
    user_email,
    action_type,
    entity_type,
    entity_id,
    endpoint,
    created_at
FROM
    [pro_team_care_logs].[core].[lgpd_audit_log]
WHERE
    user_id = @TestUserID
    AND action_type = 'VIEW'
    AND endpoint = '/auth/me'
ORDER BY
    id DESC;
GO