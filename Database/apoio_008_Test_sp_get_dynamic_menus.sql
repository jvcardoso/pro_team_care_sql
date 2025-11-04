-- =================================================================================
-- Script:         Test_sp_get_dynamic_menus.sql
-- Projeto:        Pro Team Care
-- Data:           22/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Testa a Stored Procedure [sp_get_dynamic_menus] executando-a para
-- diferentes perfis de usuário (admin e atendente) e exibindo
-- os menus que cada um deles deveria ver.
-- =================================================================================

USE pro_team_care;
GO

SET NOCOUNT ON;

-- =================================================================================
-- CENÁRIO 1: TESTE COM O USUÁRIO ADMINISTRADOR (ID = 1)
-- =================================================================================
PRINT '--- CENÁRIO 1: Executando para o Usuário Admin (ID = 1) ---';
PRINT 'Resultado esperado: Deve retornar TODOS os menus ativos, pois o admin tem todas as permissões.';

DECLARE @AdminUserID BIGINT = 1; -- ID do usuário admin

-- Verifica se o usuário admin existe
IF NOT EXISTS (SELECT 1 FROM [core].[users] WHERE id = @AdminUserID)
BEGIN
    PRINT 'ERRO: Usuário Admin (ID=1) não encontrado. Execute o script 012.';
END
ELSE
BEGIN
    -- Executa a procedure para o admin
    EXEC [core].[sp_get_dynamic_menus] @user_id_input = @AdminUserID;
END
GO -- Separa os lotes

-- =================================================================================
-- CENÁRIO 2: TESTE COM O USUÁRIO ATENDENTE (ID = 2 - criado na simulação)
-- =================================================================================
PRINT CHAR(10) + '--- CENÁRIO 2: Executando para o Usuário Atendente (ID = 2) ---';
PRINT 'Resultado esperado: Deve retornar APENAS os menus que não exigem permissão (como o Dashboard).';

DECLARE @AtendenteUserID BIGINT = (SELECT id FROM pro_team_care.core.users WHERE email_address = 'atendente@proteamcare.com.br');

-- Verifica se o usuário atendente existe
IF @AtendenteUserID IS NULL
BEGIN
    PRINT 'ERRO: Usuário Atendente (atendente@proteamcare.com.br) não encontrado. Execute o script de simulação anterior para criá-lo.';
END
ELSE
BEGIN
    -- Executa a procedure para o atendente
    EXEC [core].[sp_get_dynamic_menus] @user_id_input = @AtendenteUserID;
END
GO -- Separa os lotes