-- ===========================================
-- SCRIPT DE DEMONSTRAÇÃO: Adicionar dados de teste para validar contagens
-- Associar usuários como clientes/profissionais à empresa ID 181
-- ===========================================

USE [pro_team_care];
GO

PRINT '=== INÍCIO: ADICIONANDO DADOS DE TESTE PARA VALIDAÇÃO ===';
GO

-- 1. VERIFICAR ESTADO ATUAL DA EMPRESA 181
PRINT 'Estado atual da empresa 181:';
SELECT
    CompanyId,
    RazaoSocial,
    establishments_count,
    clients_count,
    professionals_count,
    users_count
FROM [core].[vw_complete_company_data]
WHERE CompanyId = 181;
GO

-- 2. CRIAR UM ESTABELECIMENTO PARA A EMPRESA 181
PRINT '';
PRINT 'Criando estabelecimento para empresa 181...';
IF NOT EXISTS (SELECT 1 FROM [core].[establishments] WHERE company_id = 181)
BEGIN
    INSERT INTO [core].[establishments] (company_id, name, is_active, created_at)
    VALUES (181, 'Unidade Central - Distrito Federal', 1, GETDATE());
    PRINT '✓ Estabelecimento criado para empresa 181';
END
ELSE
BEGIN
    PRINT '⚠ Estabelecimento já existe para empresa 181';
END
GO

-- 3. CRIAR UM USUÁRIO DE TESTE (CLIENTE)
PRINT '';
PRINT 'Criando usuário de teste (cliente)...';
DECLARE @testUserId BIGINT;
DECLARE @clientRoleId BIGINT;

-- Verificar se já existe usuário de teste
SELECT @testUserId = id FROM [core].[users] WHERE email_address = 'cliente.teste@proteamcare.com.br';

IF @testUserId IS NULL
BEGIN
    -- Criar pessoa física
    INSERT INTO [core].[people] (name, created_at)
    VALUES ('Cliente de Teste', GETDATE());

    DECLARE @personId BIGINT = SCOPE_IDENTITY();

    -- Criar usuário
    INSERT INTO [core].[users] (person_id, email_address, password, is_active, created_at)
    VALUES (@personId, 'cliente.teste@proteamcare.com.br', '$2b$12$dummy.hash.for.test.user', 1, GETDATE());

    SET @testUserId = SCOPE_IDENTITY();
    PRINT '✓ Usuário cliente criado (ID: ' + CAST(@testUserId AS VARCHAR) + ')';
END
ELSE
BEGIN
    PRINT '⚠ Usuário cliente já existe (ID: ' + CAST(@testUserId AS VARCHAR) + ')';
END

-- 4. ASSOCIAR USUÁRIO COMO CLIENTE DA EMPRESA 181
PRINT '';
PRINT 'Associando usuário como cliente da empresa 181...';

-- Buscar role de cliente (ou criar uma genérica)
SELECT @clientRoleId = id FROM [core].[roles] WHERE name = 'client';
IF @clientRoleId IS NULL
BEGIN
    -- Criar role de cliente se não existir
    INSERT INTO [core].[roles] (name, display_name, level, context_type, is_system_role, can_unmask_pii)
    VALUES ('client', 'Cliente', 5, 'company', 0, 0);
    SET @clientRoleId = SCOPE_IDENTITY();
    PRINT '✓ Role "client" criada';
END

-- Associar usuário à empresa como cliente
IF NOT EXISTS (SELECT 1 FROM [core].[user_roles] WHERE user_id = @testUserId AND role_id = @clientRoleId AND context_id = 181)
BEGIN
    INSERT INTO [core].[user_roles] (user_id, role_id, context_type, context_id, status, assigned_at)
    VALUES (@testUserId, @clientRoleId, 'company', 181, 'active', GETDATE());
    PRINT '✓ Usuário associado como cliente da empresa 181';
END
ELSE
BEGIN
    PRINT '⚠ Usuário já está associado como cliente da empresa 181';
END

-- 5. CRIAR UM PROFISSIONAL PARA A EMPRESA 181
PRINT '';
PRINT 'Criando profissional para empresa 181...';
DECLARE @profUserId BIGINT;
DECLARE @profRoleId BIGINT;

-- Verificar se já existe profissional de teste
SELECT @profUserId = id FROM [core].[users] WHERE email_address = 'profissional.teste@proteamcare.com.br';

IF @profUserId IS NULL
BEGIN
    -- Criar pessoa física
    INSERT INTO [core].[people] (name, created_at)
    VALUES ('Profissional de Teste', GETDATE());

    DECLARE @profPersonId BIGINT = SCOPE_IDENTITY();

    -- Criar usuário
    INSERT INTO [core].[users] (person_id, email_address, password, is_active, created_at)
    VALUES (@profPersonId, 'profissional.teste@proteamcare.com.br', '$2b$12$dummy.hash.for.test.user', 1, GETDATE());

    SET @profUserId = SCOPE_IDENTITY();
    PRINT '✓ Usuário profissional criado (ID: ' + CAST(@profUserId AS VARCHAR) + ')';
END
ELSE
BEGIN
    PRINT '⚠ Usuário profissional já existe (ID: ' + CAST(@profUserId AS VARCHAR) + ')';
END

-- Buscar ou criar role de profissional
SELECT @profRoleId = id FROM [core].[roles] WHERE name = 'professional';
IF @profRoleId IS NULL
BEGIN
    INSERT INTO [core].[roles] (name, display_name, level, context_type, is_system_role, can_unmask_pii)
    VALUES ('professional', 'Profissional', 10, 'establishment', 0, 0);
    SET @profRoleId = SCOPE_IDENTITY();
    PRINT '✓ Role "professional" criada';
END

-- Associar profissional à empresa
IF NOT EXISTS (SELECT 1 FROM [core].[user_roles] WHERE user_id = @profUserId AND role_id = @profRoleId AND context_id = 181)
BEGIN
    INSERT INTO [core].[user_roles] (user_id, role_id, context_type, context_id, status, assigned_at)
    VALUES (@profUserId, @profRoleId, 'company', 181, 'active', GETDATE());
    PRINT '✓ Profissional associado à empresa 181';
END
ELSE
BEGIN
    PRINT '⚠ Profissional já está associado à empresa 181';
END

-- 6. VERIFICAR RESULTADO FINAL
PRINT '';
PRINT '=== RESULTADO FINAL ===';
SELECT
    CompanyId,
    RazaoSocial,
    establishments_count,
    clients_count,
    professionals_count,
    users_count
FROM [core].[vw_complete_company_data]
WHERE CompanyId = 181;
GO

-- 7. VERIFICAÇÃO GERAL
PRINT '';
PRINT '=== VERIFICAÇÃO GERAL (TOP 5) ===';
SELECT TOP 5
    CompanyId,
    RazaoSocial,
    establishments_count,
    clients_count,
    professionals_count,
    users_count
FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

PRINT '';
PRINT '=== RESUMO ===';
PRINT '✓ Script de demonstração concluído!';
PRINT '✓ Empresa 181 agora deve mostrar:';
PRINT '  - 1 estabelecimento';
PRINT '  - 1 cliente';
PRINT '  - 1 profissional';
PRINT '  - 2 usuários totais';
PRINT '';
PRINT '🎯 Recarregue a página do frontend para ver as contagens atualizadas!';
GO