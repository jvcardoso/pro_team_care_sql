-- =================================================================================
-- Script:         Simulate_Reveal_Data_Query.sql (v1.2 - Hash Corrigido)
-- Descrição:
-- v1.2 - Corrige o script de criação de dados de teste para usar um hash
--        bcrypt válido para o usuário 'atendente', permitindo um teste de
--        login realista.
-- =================================================================================

-- Parte 1: Setup - Preparando o ambiente com dados de teste
-- ---------------------------------------------------------------------------------
PRINT '--- PARTE 1: CRIANDO DADOS DE TESTE ---';
USE pro_team_care;
GO

SET NOCOUNT ON;
DECLARE @atendenteUserId BIGINT, @atendenteRoleId BIGINT, @anaPersonId BIGINT, @anaPfProfileId BIGINT;
DECLARE @systemCompanyId BIGINT;

-- Busca o ID da empresa do sistema dinamicamente
SELECT @systemCompanyId = id FROM [core].[companies] WHERE access_status = 'system_owner';

IF @systemCompanyId IS NULL
BEGIN
    THROW 50000, 'A empresa do sistema (criada pelo script 012) não foi encontrada. Execute o script 012 primeiro.', 1;
    RETURN;
END

-- Cria o papel 'Atendente' se não existir (sem permissão de desmascarar)
IF NOT EXISTS (SELECT 1 FROM [core].[roles] WHERE name = 'atendente')
BEGIN
    INSERT INTO [core].[roles] (name, display_name, [level], context_type, is_system_role, can_unmask_pii)
    VALUES ('atendente', 'Atendente', 20, 'establishment', 0, 0);
END
SELECT @atendenteRoleId = id FROM [core].[roles] WHERE name = 'atendente';

-- Cria o usuário 'Atendente' se não existir
IF NOT EXISTS (SELECT 1 FROM [core].[users] WHERE email_address = 'atendente@proteamcare.com.br')
BEGIN
    -- CORREÇÃO: Usa um hash bcrypt válido para a senha 'password123'
    INSERT INTO [core].[users] (company_id, email_address, password, is_active)
    VALUES (@systemCompanyId, 'atendente@proteamcare.com.br', N'$2b$12$DR9.g/E4860.mFd123t.ue2F.OvhT4.u/C2G7.rG8.i/H.o9.j.K6', 1);
END
SELECT @atendenteUserId = id FROM [core].[users] WHERE email_address = 'atendente@proteamcare.com.br';

-- Associa o usuário ao papel
IF NOT EXISTS (SELECT 1 FROM [core].[user_roles] WHERE user_id = @atendenteUserId AND role_id = @atendenteRoleId)
BEGIN
    INSERT INTO [core].[user_roles] (user_id, role_id, context_type, context_id)
    VALUES (@atendenteUserId, @atendenteRoleId, 'company', @systemCompanyId);
END

-- Cria uma pessoa 'Ana Paciente' e um perfil PF para teste
IF NOT EXISTS (SELECT 1 FROM [core].[people] WHERE name = 'Ana Paciente')
BEGIN
    INSERT INTO [core].[people] (company_id, name, status, is_active) VALUES (@systemCompanyId, 'Ana Paciente', 'active', 1);
END
SELECT @anaPersonId = id FROM [core].[people] WHERE name = 'Ana Paciente';

IF NOT EXISTS (SELECT 1 FROM [core].[pf_profiles] WHERE person_id = @anaPersonId)
BEGIN
    INSERT INTO [core].[pf_profiles] (person_id, tax_id, birth_date) VALUES (@anaPersonId, '11122233344', '1990-05-15');
END
SELECT @anaPfProfileId = id FROM [core].[pf_profiles] WHERE person_id = @anaPersonId;

PRINT 'Dados de teste criados/verificados. Atendente ID: ' + ISNULL(CAST(@atendenteUserId AS VARCHAR), 'N/A') + ', Perfil PF de Teste ID: ' + ISNULL(CAST(@anaPfProfileId AS VARCHAR), 'N/A');
GO
