USE pro_team_care;
GO

PRINT '🔍 VERIFICANDO USUÁRIOS EXISTENTES...';
GO

IF NOT EXISTS (SELECT 1 FROM core.users WHERE email_address = 'admin@proteamcare.com.br')
BEGIN
    PRINT '❌ Usuário admin não encontrado. Criando...';
    
    -- Criar pessoa física para o admin
    DECLARE @PersonId INT;
    INSERT INTO core.people (name, created_at, updated_at)
    VALUES ('Administrador Sistema', GETDATE(), GETDATE());
    SET @PersonId = SCOPE_IDENTITY();
    
    -- Criar usuário admin
    INSERT INTO core.users (
        email_address, 
        password, 
        person_id, 
        is_active, 
        is_system_admin, 
        created_at, 
        updated_at
    ) VALUES (
        'admin@proteamcare.com.br',
        -- Senha: admin123 (hash bcrypt)
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeR2uHfGsMitKsHKC',
        @PersonId,
        1, -- ativo
        1, -- admin do sistema
        GETDATE(),
        GETDATE()
    );
    
    PRINT '✅ Usuário admin criado com sucesso\!';
    PRINT '   Email: admin@proteamcare.com.br';
    PRINT '   Senha: admin123';
END
ELSE
BEGIN
    PRINT '✅ Usuário admin já existe';
    
    -- Mostrar status do usuário
    SELECT 
        id,
        email_address,
        is_active,
        is_system_admin,
        last_login_at
    FROM core.users 
    WHERE email_address = 'admin@proteamcare.com.br';
END
GO

PRINT '📊 USUÁRIOS NO SISTEMA:';
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
    SUM(CASE WHEN is_system_admin = 1 THEN 1 ELSE 0 END) as admin_users
FROM core.users;
GO

PRINT '✅ VERIFICAÇÃO CONCLUÍDA';
GO
