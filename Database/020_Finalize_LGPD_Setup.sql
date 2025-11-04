-- =================================================================================
-- Script:         020_Finalize_LGPD_Setup.sql (v1.1 - Correção de Lote e Lógica)
-- Descrição:
-- v1.1 - Adiciona o separador 'GO' antes do CREATE VIEW e corrige o nome
--        do papel de admin para 'system_admin'.
-- =================================================================================

USE pro_team_care;
GO

-- Parte 1: Corrigindo a Permissão dos Papéis de Administrador
-- ---------------------------------------------------------------------------------
PRINT '--- Parte 1: Configurando a permissão [can_unmask_pii] para os papéis de admin ---';

-- CORREÇÃO: Usando o nome do papel correto ('system_admin') que foi criado no script 012.
UPDATE [core].[roles]
SET [can_unmask_pii] = 1
WHERE [name] = 'system_admin';

-- Verificação
IF EXISTS (SELECT 1 FROM core.roles WHERE name = 'system_admin' AND can_unmask_pii = 1)
    PRINT '✅ Permissão [can_unmask_pii] configurada corretamente para o papel [system_admin].';
ELSE
    PRINT '⚠️ Atenção: Não foi possível configurar a permissão para o papel [system_admin].';
GO


-- Parte 2: Criando a View de Segurança para Perfis PJ
-- ---------------------------------------------------------------------------------
PRINT CHAR(10) + '--- Parte 2: Criando a View de Segurança [vw_secure_pj_profiles] ---';

-- CORREÇÃO: Adicionado o separador 'GO' para iniciar um novo lote.
GO

CREATE OR ALTER VIEW [core].[vw_secure_pj_profiles]
AS
SELECT
    id,
    person_id,
    company_id,

    -- Lógica de mascaramento para o CNPJ (tax_id)
    -- Exemplo: 12.345.678/0001-99 -> 12.***.***/****-99
    CASE
        WHEN [core].[fn_CanUserUnmaskData]() = 1 THEN tax_id -- Desmascarado
        ELSE LEFT(tax_id, 2) + '.' + REPLICATE('*', 3) + '.' + REPLICATE('*', 3) + '/' + REPLICATE('*', 4) + '-' + RIGHT(tax_id, 2)
    END AS tax_id,

    -- Lógica de mascaramento para o Nome Fantasia (trade_name)
    CASE
        WHEN [core].[fn_CanUserUnmaskData]() = 1 THEN trade_name -- Desmascarado
        ELSE LEFT(ISNULL(trade_name, ''), 3) + '...'
    END AS trade_name,

    -- Campos não sensíveis podem ser exibidos diretamente
    incorporation_date,
    tax_regime,
    legal_nature,
    municipal_registration,
    created_at,
    updated_at
FROM
    [core].[pj_profiles];
GO

PRINT '✅ View de segurança [core].[vw_secure_pj_profiles] criada/alterada com sucesso.';
GO
