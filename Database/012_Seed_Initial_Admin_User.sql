-- =================================================================================
-- Script:         012_Seed_Initial_Admin_User.sql (v3.1 - com MERGE/UPSERT)
-- Descrição:
-- v3.1 - Utiliza o comando MERGE para criar o usuário admin se não existir,
--        ou para atualizar/corrigir o registro se ele já existir (UPSERT).
--        Isso garante que o estado do usuário admin esteja sempre correto.
-- =================================================================================

USE pro_team_care;
GO

SET NOCOUNT ON;
BEGIN TRANSACTION;
BEGIN TRY

    DECLARE @systemCompanyId BIGINT, @systemPersonId BIGINT, @adminRoleId BIGINT, @adminUserId BIGINT;
    DECLARE @adminEmail NVARCHAR(255) = N'admin@proteamcare.com.br';

    -- A criação da empresa e do papel pode continuar com IF NOT EXISTS,
    -- pois são entidades mais estáveis.
    IF NOT EXISTS (SELECT 1 FROM [core].[companies] WHERE [access_status] = 'system_owner')
    BEGIN
        INSERT INTO [core].[companies] (access_status) VALUES ('system_owner');
        SET @systemCompanyId = SCOPE_IDENTITY();
    END
    ELSE
    BEGIN
        SELECT @systemCompanyId = id FROM [core].[companies] WHERE [access_status] = 'system_owner';
    END

    -- Lógica para criar a Pessoa e o Perfil PJ separadamente
    IF NOT EXISTS (SELECT 1 FROM [core].[pj_profiles] pjp JOIN [core].[people] p ON pjp.person_id = p.id WHERE pjp.company_id = @systemCompanyId AND pjp.tax_id = '00000000000000')
    BEGIN
        INSERT INTO [core].[people] (company_id, name, status) VALUES (@systemCompanyId, 'Pro Team Care System Owner', 'active');
        SET @systemPersonId = SCOPE_IDENTITY();
        INSERT INTO [core].[pj_profiles] (person_id, company_id, tax_id, trade_name) VALUES (@systemPersonId, @systemCompanyId, '00000000000000', 'Pro Team Care');
        UPDATE [core].[companies] SET person_id = @systemPersonId WHERE id = @systemCompanyId;
    END

    -- Cria o Papel (Role) de Administrador do Sistema, se não existir
    IF NOT EXISTS (SELECT 1 FROM [core].[roles] WHERE [name] = 'system_admin')
    BEGIN
        INSERT INTO [core].[roles] (name, display_name, [level], context_type, is_system_role, can_unmask_pii)
        VALUES ('system_admin', 'Administrador do Sistema', 100, 'system', 1, 1);
    END
    SELECT @adminRoleId = id FROM [core].[roles] WHERE name = 'system_admin';


    -- =============================================================================
    -- CORREÇÃO: Usando MERGE para criar ou atualizar o usuário admin.
    -- =============================================================================
    PRINT 'Verificando/Criando/Corrigindo o usuário admin...';
    MERGE INTO [core].[users] AS Target
    USING (VALUES
        -- Fonte de dados: Define o estado ideal do nosso usuário admin
        (@systemCompanyId, @adminEmail, N'$2b$12$s.0a0SfkOP61AI.mYS4kMOgGm4V8/aF9eCAhwDfTjx6dn0fzvcrZ.', 1, 1, 'system')
    ) AS Source (company_id, email, password, is_active, is_system_admin, context_type)
    ON Target.email_address = Source.email -- A condição de junção é o email

    -- Se o usuário com este email JÁ EXISTE (WHEN MATCHED)
    WHEN MATCHED THEN
        -- Garante que a senha, o status e outras flags estejam corretas.
        UPDATE SET
            Target.password = Source.password,
            Target.is_active = Source.is_active,
            Target.is_system_admin = Source.is_system_admin,
            Target.company_id = Source.company_id,
            Target.updated_at = GETDATE()

    -- Se o usuário com este email NÃO EXISTE (WHEN NOT MATCHED)
    WHEN NOT MATCHED BY TARGET THEN
        -- Insere um novo usuário com os dados corretos.
        INSERT (company_id, email_address, password, is_active, is_system_admin, context_type)
        VALUES (Source.company_id, Source.email, Source.password, Source.is_active, Source.is_system_admin, Source.context_type);

    -- Pega o ID do usuário, seja ele inserido ou atualizado
    SELECT @adminUserId = id FROM [core].[users] WHERE email_address = @adminEmail;

    -- =============================================================================
    -- CORREÇÃO: Usando MERGE para garantir a associação do papel.
    -- =============================================================================
    PRINT 'Verificando/Criando a associação de papel para o admin...';
    MERGE INTO [core].[user_roles] AS Target
    USING (VALUES
        (@adminUserId, @adminRoleId, 'system', 0, 'active')
    ) AS Source (user_id, role_id, context_type, context_id, status)
    ON Target.user_id = Source.user_id AND Target.role_id = Source.role_id AND Target.context_type = Source.context_type

    -- Se a associação não existe, cria. Se já existe, não faz nada.
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (user_id, role_id, context_type, context_id, status)
        VALUES (Source.user_id, Source.role_id, Source.context_type, Source.context_id, Source.status);


    COMMIT TRANSACTION;
    PRINT '✅ Script de seeding do administrador (v3.1) concluído com sucesso!';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    THROW;
END CATCH;
GOs