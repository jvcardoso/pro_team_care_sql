-- =================================================================================
-- Script:         cleanup_failed_insert.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
--
-- Descrição:
-- Limpa dados incompletos de tentativas anteriores que falharam.
-- Execute APENAS se o insert_admin_user.sql falhou no meio.
-- =================================================================================

USE pro_team_care;
GO

BEGIN TRANSACTION;

PRINT 'Limpando dados do Super Admin...';

-- 1. Deletar user_roles do admin (se houver)
DELETE FROM [core].[user_roles]
WHERE user_id IN (SELECT id FROM [core].[users] WHERE email_address = 'admin@proteamcare.com.br');

PRINT 'User_roles do admin removidos.';

-- 2. Deletar usuário admin (se existir)
DELETE FROM [core].[users]
WHERE email_address = 'admin@proteamcare.com.br';

PRINT 'Usuário admin removido.';

-- 3. Deletar role super_admin (se existir e não estiver em uso por outros)
IF NOT EXISTS (
    SELECT 1 FROM [core].[user_roles] ur
    INNER JOIN [core].[roles] r ON ur.role_id = r.id
    WHERE r.name = 'super_admin'
      AND ur.user_id NOT IN (SELECT id FROM [core].[users] WHERE email_address = 'admin@proteamcare.com.br')
)
BEGIN
    DELETE FROM [core].[roles] WHERE name = 'super_admin';
    PRINT 'Role super_admin removida.';
END
ELSE
BEGIN
    PRINT 'Role super_admin está em uso por outros usuários, mantida.';
END

PRINT 'Super Admin não está vinculado a companies, nada mais a limpar.';

COMMIT TRANSACTION;

PRINT '';
PRINT '================================================================';
PRINT 'LIMPEZA CONCLUÍDA!';
PRINT '================================================================';
PRINT 'Agora você pode executar o insert_admin_user.sql novamente.';
PRINT '================================================================';

GO
