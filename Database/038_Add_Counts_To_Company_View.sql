-- Script para adicionar campos de contagem na view vw_complete_company_data
-- Necessário para exibir estatísticas na tabela de empresas do frontend

USE [pro_team_care];
GO

-- ===========================================
-- ATUALIZAÇÃO DA VIEW COM CAMPOS DE CONTAGEM
-- ===========================================

-- 1. Remover view existente se existir
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[core].[vw_complete_company_data]'))
BEGIN
    DROP VIEW [core].[vw_complete_company_data];
    PRINT '✓ View vw_complete_company_data removida para atualização com contagens';
END
GO

-- 2. Recriar view com campos de contagem incluídos
CREATE VIEW [core].[vw_complete_company_data]
AS
SELECT
    c.id AS CompanyId,
    c.access_status AS CompanyAccessStatus,
    c.person_id AS PersonId,
    pj.id AS PjProfileId,
    p.name AS RazaoSocial,
    pj.trade_name AS NomeFantasia,

    -- CNPJ mascarado conforme LGPD (Database-First Presentation)
    CASE
        WHEN LEN(LTRIM(RTRIM(ISNULL(pj.tax_id, '')))) = 14 THEN
            SUBSTRING(pj.tax_id, 1, 2) + '.***.***/****-' + SUBSTRING(pj.tax_id, 13, 2)
        ELSE
            '**.***.***/****-**'
    END AS CNPJ,

    -- Endereço principal
    addr.id AS PrincipalAddressId,
    addr.street AS PrincipalStreet,
    addr.number AS PrincipalNumber,
    addr.neighborhood AS PrincipalNeighborhood,
    addr.city AS PrincipalCity,
    addr.state AS PrincipalState,
    addr.zip_code AS PrincipalZipCode,

    -- CONTAGENS - Campos adicionados para estatísticas na tabela
    ISNULL((
        SELECT COUNT(*)
        FROM [core].[establishments] e
        WHERE e.company_id = c.id AND e.is_active = 1
    ), 0) AS establishments_count,

    -- Clientes: usuários com roles associadas à empresa (qualquer role não-admin)
    ISNULL((
        SELECT COUNT(DISTINCT ur.user_id)
        FROM [core].[user_roles] ur
        JOIN [core].[roles] r ON ur.role_id = r.id
        WHERE ur.context_id = c.id
          AND ur.context_type IN ('company', 'establishment')
          AND ur.status = 'active'
          AND r.is_system_role = 0
          AND r.name NOT LIKE '%admin%'
          AND r.name NOT LIKE '%system%'
    ), 0) AS clients_count,

    -- Profissionais: usuários com roles específicas de profissionais
    ISNULL((
        SELECT COUNT(DISTINCT ur.user_id)
        FROM [core].[user_roles] ur
        JOIN [core].[roles] r ON ur.role_id = r.id
        WHERE ur.context_id = c.id
          AND ur.context_type IN ('company', 'establishment')
          AND ur.status = 'active'
          AND r.name IN ('professional', 'doctor', 'nurse', 'therapist', 'caregiver', 'atendente')
    ), 0) AS professionals_count,

    -- Usuários totais: todos os usuários associados à empresa
    ISNULL((
        SELECT COUNT(DISTINCT ur.user_id)
        FROM [core].[user_roles] ur
        WHERE ur.context_id = c.id
          AND ur.context_type IN ('company', 'establishment')
          AND ur.status = 'active'
    ), 0) AS users_count,

    -- Telefones como JSON ARRAY nativo
    ISNULL((
        SELECT
            ph.id,
            REPLACE(REPLACE(REPLACE(REPLACE(ph.number, '(', ''), ')', ''), ' ', ''), '-', '') as number,
            ph.type,
            ph.is_principal
        FROM [core].[phones] ph
        WHERE ph.company_id = c.id
        FOR JSON PATH
    ), '[]') AS PhoneNumbers,

    -- Emails como JSON ARRAY nativo
    ISNULL((
        SELECT
            em.id,
            em.email_address as email,
            em.type,
            em.is_principal
        FROM [core].[emails] em
        WHERE em.company_id = c.id
        FOR JSON PATH
    ), '[]') AS EmailAddresses,

    -- Data de incorporação
    pj.incorporation_date,

    -- Data de criação da empresa
    c.created_at AS CompanyCreatedAt

FROM
    [core].[companies] c
    LEFT JOIN [core].[people] p ON c.person_id = p.id
    LEFT JOIN [core].[pj_profiles] pj ON pj.person_id = p.id
    LEFT JOIN [core].[addresses] addr ON addr.company_id = c.id AND addr.is_principal = 1;
GO

PRINT '✓ View vw_complete_company_data recriada com campos de contagem';
PRINT '✓ Adicionados: establishments_count, clients_count, professionals_count, users_count';
GO

-- ===========================================
-- TESTE DA VIEW ATUALIZADA
-- ===========================================

PRINT '';
PRINT '=== TESTE DA VIEW COM CONTAGENS ===';
GO

-- Verificar se os campos de contagem foram adicionados
SELECT TOP 5
    CompanyId,
    RazaoSocial,
    CNPJ,
    establishments_count,
    clients_count,
    professionals_count,
    users_count,
    CompanyAccessStatus
FROM [core].[vw_complete_company_data]
ORDER BY CompanyId DESC;
GO

-- Verificar totais para validação
SELECT
    COUNT(*) as Total_Empresas,
    SUM(establishments_count) as Total_Estabelecimentos,
    SUM(clients_count) as Total_Clientes,
    SUM(professionals_count) as Total_Profissionais,
    SUM(users_count) as Total_Usuarios
FROM [core].[vw_complete_company_data];

-- ===========================================
-- DIAGNÓSTICO DETALHADO
-- ===========================================

PRINT '';
PRINT '=== DIAGNÓSTICO DOS DADOS ===';
GO

-- Verificar se existem estabelecimentos
SELECT
    'Estabelecimentos' as Tipo,
    COUNT(*) as Total,
    COUNT(CASE WHEN is_active = 1 THEN 1 END) as Ativos
FROM [core].[establishments];
GO

-- Verificar roles existentes
SELECT
    'Roles' as Tipo,
    COUNT(*) as Total,
    STRING_AGG(name, ', ') as Nomes
FROM [core].[roles];
GO

-- Verificar associações de usuários a empresas
SELECT
    'User Roles' as Tipo,
    COUNT(*) as Total_Associacoes,
    COUNT(DISTINCT user_id) as Usuarios_Unicos,
    COUNT(DISTINCT context_id) as Contextos_Unicos
FROM [core].[user_roles]
WHERE context_type IN ('company', 'establishment');
GO

-- Verificar distribuição por context_type
SELECT
    context_type,
    COUNT(*) as Quantidade
FROM [core].[user_roles]
GROUP BY context_type;
GO
GO

PRINT '✓ Teste concluído - view atualizada com sucesso';
PRINT '✓ Campos de contagem adicionados para estatísticas na tabela';
GO