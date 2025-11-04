-- =================================================================================
-- Script:         040_Seed_System_Roles.sql
-- Descrição:      Insere os papéis (roles) essenciais do sistema que não são
--                 o super-admin. Utiliza MERGE para ser idempotente.
-- Autor:          Gemini DBA
-- Data:           28/10/2025
-- =================================================================================

USE pro_team_care;
GO

BEGIN TRANSACTION;
BEGIN TRY

    PRINT 'Nivelando papéis essenciais do sistema...';

    MERGE INTO [core].[roles] AS Target
    USING (VALUES
        -- name, display_name, level, context_type, is_system_role
        ('company_admin', 'Administrador da Empresa', 90, 'company', 1),
        ('establishment_admin', 'Administrador do Estabelecimento', 80, 'establishment', 0),
        ('professional', 'Profissional', 50, 'establishment', 0),
        ('client', 'Cliente', 10, 'establishment', 0)
    ) AS Source (name, display_name, [level], context_type, is_system_role)
    ON Target.name = Source.name

    -- Se o papel já existe, atualiza para garantir consistência
    WHEN MATCHED THEN
        UPDATE SET
            Target.display_name = Source.display_name,
            Target.[level] = Source.[level],
            Target.context_type = Source.context_type,
            Target.is_system_role = Source.is_system_role,
            Target.updated_at = GETDATE()

    -- Se o papel não existe, cria
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (name, display_name, [level], context_type, is_system_role, created_at, updated_at)
        VALUES (Source.name, Source.display_name, Source.[level], Source.context_type, Source.is_system_role, GETDATE(), GETDATE());

    PRINT '✓ Papéis company_admin, establishment_admin, professional, e client foram criados/atualizados.';

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT '❌ ERRO: A operação falhou e a transação foi revertida.';
    THROW;
END CATCH;
GO
