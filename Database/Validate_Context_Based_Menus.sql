-- =================================================================================
-- Script:         Validate_Context_Based_Menus.sql
-- Descrição:      Valida a implementação dos menus baseados em contexto.
-- =================================================================================
USE pro_team_care;
GO

PRINT '--- Iniciando Validação dos Menus Baseados em Contexto ---';

-- 1. Verifica se a coluna context_type existe em menu_items
PRINT CHAR(10) + '--- 1. Verificando a Coluna [context_type] na Tabela [menu_items] ---';
IF EXISTS (SELECT 1 FROM sys.columns WHERE Name = N'context_type' AND Object_ID = Object_ID(N'core.menu_items'))
    SELECT '✅ OK' AS Status, 'Coluna [context_type] existe.' AS Mensagem;
ELSE
    SELECT '❌ ERRO' AS Status, 'Coluna [context_type] NÃO encontrada em [menu_items]!' AS Mensagem;
GO

-- 2. Lista os menus e seus contextos definidos
PRINT CHAR(10) + '--- 2. Listando Menus e seus Contextos Atuais ---';
SELECT
    id,
    parent_id,
    name,
    label,
    ISNULL(context_type, '<COMUM>') AS context_type -- Mostra <COMUM> se for NULL
FROM
    [core].[menu_items]
ORDER BY
    ISNULL(parent_id, id), display_order;
GO

-- 3. Testa a procedure sp_get_dynamic_menus para o Admin
PRINT CHAR(10) + '--- 3. Testando Menus Visíveis para o Usuário Admin (context_type = ''system'') ---';
DECLARE @AdminUserID BIGINT = (SELECT id FROM [core].[users] WHERE email_address = 'admin@proteamcare.com.br');
IF @AdminUserID IS NOT NULL
    EXEC [core].[sp_get_dynamic_menus] @user_id_input = @AdminUserID;
ELSE
    PRINT 'Usuário Admin não encontrado.';
GO

-- 4. Testa a procedure sp_get_dynamic_menus para o Atendente
PRINT CHAR(10) + '--- 4. Testando Menus Visíveis para o Usuário Atendente (context_type = ''professional'') ---';
DECLARE @AtendenteUserID BIGINT = (SELECT id FROM [core].[users] WHERE email_address = 'atendente@proteamcare.com.br');
IF @AtendenteUserID IS NOT NULL
    EXEC [core].[sp_get_dynamic_menus] @user_id_input = @AtendenteUserID;
ELSE
    PRINT 'Usuário Atendente não encontrado.';
GO

-- 5. Verifica se o menu profissional foi criado
PRINT CHAR(10) + '--- 5. Verificando Menu Específico para Profissionais ---';
SELECT
    'Menus para profissionais:' AS Info,
    COUNT(*) AS Quantidade
FROM [core].[menu_items]
WHERE context_type = 'professional' AND is_active = 1 AND deleted_at IS NULL;

SELECT
    id,
    name,
    label,
    path,
    context_type
FROM [core].[menu_items]
WHERE context_type = 'professional' AND is_active = 1 AND deleted_at IS NULL
ORDER BY display_order;
GO

PRINT CHAR(10) + '--- Validação Concluída ---';