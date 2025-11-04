-- ===========================================
-- DIAGNÓSTICO: Por que as contagens estão zeradas? (v2 - CORRIGIDO)
-- Execute estas consultas no SQL Server e me mostre os resultados
-- ===========================================

USE [pro_team_care];
GO

-- 1. VERIFICAR ROLES EXISTENTES
PRINT '=== 1. ROLES EXISTENTES ===';
SELECT
    id,
    name,
    display_name,
    context_type,
    is_system_role
FROM [core].[roles]
ORDER BY name;
GO

-- 2. VERIFICAR ASSOCIAÇÕES DE USUÁRIOS PARA UMA EMPRESA ESPECÍFICA
PRINT '';
PRINT '=== 2. ASSOCIAÇÕES DE USUÁRIOS (Empresa ID: 181) ===';
SELECT
    ur.user_id,
    ur.role_id,
    r.name as role_name,
    r.display_name as role_display,
    ur.context_type,
    ur.context_id,
    ur.status
FROM [core].[user_roles] ur
JOIN [core].[roles] r ON ur.role_id = r.id
WHERE ur.context_id = 181
ORDER BY ur.user_id, r.name;
GO

-- 3. VERIFICAR SE EXISTEM ESTABELECIMENTOS
PRINT '';
PRINT '=== 3. ESTABELECIMENTOS EXISTENTES ===';
SELECT
    id,
    company_id,
    code, -- CORREÇÃO: A tabela establishments não tem 'name', mas sim 'code'
    is_active,
    created_at
FROM [core].[establishments]
ORDER BY company_id, id;
GO

-- 4. VERIFICAR DISTRIBUIÇÃO GERAL DE USER_ROLES
PRINT '';
PRINT '=== 4. DISTRIBUIÇÃO GERAL DE USER_ROLES ===';
SELECT
    context_type,
    COUNT(*) as total_associacoes,
    COUNT(DISTINCT user_id) as usuarios_unicos,
    COUNT(DISTINCT context_id) as contextos_unicos
FROM [core].[user_roles]
GROUP BY context_type
ORDER BY context_type;
GO

-- 5. VERIFICAR USUÁRIOS POR EMPRESA (VIA USER_ROLES)
PRINT '';
PRINT '=== 5. USUÁRIOS ASSOCIADOS ÀS EMPRESAS ===';
SELECT
    ur.context_id as company_id,
    p.name as razao_social, -- CORREÇÃO: Razão social vem da tabela people
    COUNT(DISTINCT ur.user_id) as usuarios_associados,
    STRING_AGG(DISTINCT r.name, ', ') as roles_encontrados
FROM [core].[user_roles] ur
JOIN [core].[roles] r ON ur.role_id = r.id
JOIN [core].[companies] c ON ur.context_id = c.id
JOIN [core].[people] p ON c.person_id = p.id -- CORREÇÃO: Adicionado JOIN com people
WHERE ur.context_type IN ('company', 'establishment')
  AND ur.status = 'active'
GROUP BY ur.context_id, p.name -- CORREÇÃO: Agrupado por p.name
ORDER BY ur.context_id;
GO

-- 6. VERIFICAR SE HÁ USUÁRIOS DIRETAMENTE ASSOCIADOS ÀS EMPRESAS
PRINT '';
PRINT '=== 6. USUÁRIOS COM COMPANY_ID DIRETO ===';
SELECT
    u.id,
    u.email_address,
    u.company_id,
    p.name as razao_social, -- CORREÇÃO: Razão social vem da tabela people
    u.is_active
FROM [core].[users] u
LEFT JOIN [core].[companies] c ON u.company_id = c.id
LEFT JOIN [core].[people] p ON c.person_id = p.id -- CORREÇÃO: Adicionado JOIN com people
WHERE u.company_id IS NOT NULL
ORDER BY u.company_id, u.id;
GO

-- 7. VERIFICAR A VIEW ATUAL
PRINT '';
PRINT '=== 7. TESTE DA VIEW ATUAL ===';
SELECT TOP 3
    CompanyId,
    RazaoSocial,
    CNPJ,
    establishments_count,
    clients_count,
    professionals_count,
    users_count
FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO