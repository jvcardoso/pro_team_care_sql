-- =================================================================================
-- Script:         033_Add_Professional_Menu.sql
-- Descrição:      Adiciona menu específico para profissionais (context_type = 'professional').
-- =================================================================================
USE pro_team_care;
GO

-- Insere o menu principal para profissionais
INSERT INTO [core].[menu_items] (
    parent_id,
    name,
    label,
    icon,
    path,
    display_order,
    is_active,
    context_type,
    created_at,
    updated_at
) VALUES (
    NULL, -- Menu raiz
    'dashboard_profissional',
    'Dashboard Profissional',
    'LayoutDashboard', -- Ícone do Lucide React
    '/professional',
    1, -- Primeira posição
    1, -- Ativo
    'professional', -- Contexto específico
    GETDATE(),
    GETDATE()
);

PRINT '✅ Menu "Dashboard Profissional" criado para contexto "professional".';

-- Verifica o resultado
SELECT
    id,
    name,
    label,
    path,
    context_type,
    display_order
FROM [core].[menu_items]
WHERE context_type = 'professional'
ORDER BY display_order;