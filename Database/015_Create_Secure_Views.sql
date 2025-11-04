-- =================================================================================
-- Script:         015_Create_Secure_Views.sql
-- Projeto:        Pro Team Care
-- Descrição:
-- Cria as views de segurança que aplicam o mascaramento de dados dinâmico
-- utilizando a função [fn_CanUserUnmaskData] e o SESSION_CONTEXT.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER VIEW [core].[vw_secure_pf_profiles]
AS
SELECT
    id,
    person_id,
    -- Aplica o mascaramento condicional no CPF (tax_id)
    CASE
        WHEN [core].[fn_CanUserUnmaskData]() = 1 THEN tax_id -- Desmascarado
        ELSE '***.' + SUBSTRING(tax_id, 4, 3) + '.' + SUBSTRING(tax_id, 7, 3) + '-**' -- Mascarado
    END AS tax_id,

    -- Aplica o mascaramento condicional na data de nascimento
    CASE
        WHEN [core].[fn_CanUserUnmaskData]() = 1 THEN birth_date -- Desmascarado
        ELSE CAST(CONCAT('01/', FORMAT(birth_date, 'MM/yyyy')) AS DATE) -- Mascarado (mostra 01/mês/ano)
    END AS birth_date,

    gender,
    marital_status,
    occupation,
    created_at,
    updated_at
FROM
    [core].[pf_profiles];
GO

PRINT 'View de segurança [core].[vw_secure_pf_profiles] criada/alterada com sucesso.';
