-- =================================================================================
-- Script:         Simulate_All_LGPD_Access_Patterns.sql (v1.1 - Corrigido)
-- Descrição:
-- v1.1 - Corrige o erro "Ambiguous column name 'id'" especificando
--        o alias da tabela (pp.id) nas subconsultas.
-- =================================================================================

-- Parte 1: Setup - Preparando o ambiente com dados de teste
-- ---------------------------------------------------------------------------------
PRINT '--- PARTE 1: VERIFICANDO/CRIANDO DADOS DE TESTE ---';
USE pro_team_care;
GO

-- (Esta parte já está correta e não foi alterada)
SET NOCOUNT ON;
DECLARE @atendenteUserId BIGINT, @adminUserId BIGINT, @anaPfProfileId BIGINT, @systemCompanyId BIGINT;
SELECT @systemCompanyId = id FROM [core].[companies] WHERE access_status = 'system_owner';
IF @systemCompanyId IS NULL BEGIN THROW 50000, 'Empresa do sistema não encontrada. Execute o script 012 primeiro.', 1; RETURN; END
IF NOT EXISTS (SELECT 1 FROM [core].[roles] WHERE name = 'atendente')
    INSERT INTO [core].[roles] (name, display_name, [level], context_type, is_system_role, can_unmask_pii) VALUES ('atendente', 'Atendente', 20, 'establishment', 0, 0);
DECLARE @atendenteRoleId BIGINT = (SELECT id FROM [core].[roles] WHERE name = 'atendente');
IF NOT EXISTS (SELECT 1 FROM [core].[users] WHERE email_address = 'atendente@proteamcare.com.br')
    INSERT INTO [core].[users] (company_id, email_address, password, is_active) VALUES (@systemCompanyId, 'atendente@proteamcare.com.br', N'$2b$12$DR9.g/E4860.mFd123t.ue2F.OvhT4.u/C2G7.rG8.i/H.o9.j.K6', 1);
SELECT @atendenteUserId = id FROM [core].[users] WHERE email_address = 'atendente@proteamcare.com.br';
IF NOT EXISTS (SELECT 1 FROM [core].[user_roles] WHERE user_id = @atendenteUserId AND role_id = @atendenteRoleId)
    INSERT INTO [core].[user_roles] (user_id, role_id, context_type, context_id) VALUES (@atendenteUserId, @atendenteRoleId, 'company', @systemCompanyId);
IF NOT EXISTS (SELECT 1 FROM [core].[people] WHERE name = 'Ana Paciente')
    INSERT INTO [core].[people] (company_id, name, status, is_active) VALUES (@systemCompanyId, 'Ana Paciente', 'active', 1);
DECLARE @anaPersonId BIGINT = (SELECT id FROM [core].[people] WHERE name = 'Ana Paciente');
IF NOT EXISTS (SELECT 1 FROM [core].[pf_profiles] WHERE person_id = @anaPersonId)
    INSERT INTO [core].[pf_profiles] (person_id, tax_id, birth_date) VALUES (@anaPersonId, '11122233344', '1990-05-15');
SELECT @anaPfProfileId = id FROM [core].[pf_profiles] WHERE person_id = @anaPersonId;
SELECT @adminUserId = id FROM [core].[users] WHERE email_address = 'admin@proteamcare.com.br';
PRINT 'Dados de teste verificados. Pronto para a simulação.';
GO

----------------------------------------------------------------------------------------------------
-- CENÁRIO 1: CONSULTA COM MÁSCARA (Usuário 'Atendente')
----------------------------------------------------------------------------------------------------
PRINT CHAR(10) + '==============================================================================';
PRINT 'CENÁRIO 1: CONSULTA COMO USUÁRIO "ATENDENTE" (SEM PERMISSÃO)';
PRINT '==============================================================================';
DECLARE @atendenteId_c1 BIGINT = (SELECT id FROM pro_team_care.core.users WHERE email_address = 'atendente@proteamcare.com.br');
EXEC sp_set_session_context @key = N'user_id', @value = @atendenteId_c1;
PRINT 'Executando SELECT na View de Segurança. Os dados de CPF e Data de Nasc. devem vir MASCARADOS.';
SELECT id, person_id, tax_id, birth_date
FROM [core].[vw_secure_pf_profiles]
WHERE id = (
    -- CORREÇÃO: Especificando pp.id para remover a ambiguidade
    SELECT pp.id FROM core.pf_profiles pp JOIN core.people p ON pp.person_id = p.id WHERE p.name = 'Ana Paciente'
);
GO

----------------------------------------------------------------------------------------------------
-- CENÁRIO 2: CONSULTA SEM MÁSCARA (Usuário 'Admin')
----------------------------------------------------------------------------------------------------
PRINT CHAR(10) + '==============================================================================';
PRINT 'CENÁRIO 2: CONSULTA COMO USUÁRIO "ADMIN" (COM PERMISSÃO)';
PRINT '==============================================================================';
DECLARE @adminId_c2 BIGINT = (SELECT id FROM pro_team_care.core.users WHERE email_address = 'admin@proteamcare.com.br');
EXEC sp_set_session_context @key = N'user_id', @value = @adminId_c2;
PRINT 'Executando o MESMO SELECT na View. Os dados agora devem vir DESMASCARADOS.';
SELECT id, person_id, tax_id, birth_date
FROM [core].[vw_secure_pf_profiles]
WHERE id = (
    -- CORREÇÃO: Especificando pp.id para remover a ambiguidade
    SELECT pp.id FROM core.pf_profiles pp JOIN core.people p ON pp.person_id = p.id WHERE p.name = 'Ana Paciente'
);
GO

----------------------------------------------------------------------------------------------------
-- CENÁRIO 3: AÇÃO DE "REVELAR" COM GERAÇÃO DE LOG (Usuário 'Admin')
----------------------------------------------------------------------------------------------------
PRINT CHAR(10) + '==============================================================================';
PRINT 'CENÁRIO 3: AÇÃO DE "REVELAR" COM GERAÇÃO DE LOG DE AUDITORIA';
PRINT '==============================================================================';
DECLARE @adminId_c3 BIGINT = (SELECT id FROM pro_team_care.core.users WHERE email_address = 'admin@proteamcare.com.br');
EXEC sp_set_session_context @key = N'user_id', @value = @adminId_c3;
PRINT 'Executando a procedure sp_reveal_sensitive_data...';
DECLARE @anaPfProfileId_c3 BIGINT = (
    -- CORREÇÃO: Especificando pp.id para remover a ambiguidade
    SELECT pp.id FROM core.pf_profiles pp JOIN core.people p ON pp.person_id = p.id WHERE p.name = 'Ana Paciente'
);
EXEC [pro_team_care].[core].[sp_reveal_sensitive_data]
    @entity_type = 'pf_profiles',
    @entity_id = @anaPfProfileId_c3,
    @fields_to_reveal = '["tax_id","birth_date"]',
    @user_email = 'admin@proteamcare.com.br',
    @ip_address = '127.0.0.1 (simulado)',
    @endpoint = '/api/v1/pf-profiles/reveal';
GO

-- Verificação do Log
PRINT CHAR(10) + '--- Verificando o Log de Auditoria no banco pro_team_care_logs ---';
SELECT TOP 1 id, user_id, user_email, action_type, entity_type, entity_id, sensitive_fields, created_at
FROM [pro_team_care_logs].[core].[lgpd_audit_log]
WHERE action_type = 'REVEAL'
ORDER BY id DESC;
GO

EXEC sp_set_session_context @key = N'user_id', @value = NULL;
GO
