-- =================================================================================
-- Script:         reset_atendente_password.sql
-- Descrição:      Atualiza a senha do usuário de teste 'atendente@proteamcare.com.br'
--                 para um novo hash bcrypt correspondente à senha 'test1234'.
-- =================================================================================
USE pro_team_care;
GO

DECLARE @AtendenteEmail NVARCHAR(255) = 'atendente@proteamcare.com.br';
-- Hash Bcrypt pré-gerado para a senha: 'test1234' (custo 12)
-- IMPORTANTE: Gere o hash correto usando Python:
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
-- print(pwd_context.hash("test1234"))
DECLARE @NewBcryptHash NVARCHAR(255) = '$2b$12$abcdefghijklmnopqrstuv'; -- SUBSTITUA PELO HASH REAL

PRINT 'Tentando atualizar a senha para o usuário: ' + @AtendenteEmail;

UPDATE [core].[users]
SET
    hashed_password = @NewBcryptHash,
    -- Opcional: Limpar campos de reset, caso haja lixo de testes
    password_reset_token = NULL,
    password_reset_expires_at = NULL,
    updated_at = GETDATE()
WHERE
    email_address = @AtendenteEmail;

-- Verificação
IF @@ROWCOUNT > 0
    PRINT '✅ SUCESSO: A senha do usuário ' + @AtendenteEmail + ' foi atualizada para o hash correspondente a "test1234".';
ELSE
    PRINT '⚠️ ATENÇÃO: Nenhum usuário encontrado com o email ' + @AtendenteEmail + '. Nenhuma senha foi alterada.';
GO

-- Verifica o novo hash no banco
SELECT id, email_address, hashed_password
FROM [core].[users]
WHERE email_address = 'atendente@proteamcare.com.br';
GO