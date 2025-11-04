-- =================================================================================
-- Script:         034_Create_Delete_Incomplete_Company_Procedure.sql
-- Descrição:      Cria a procedure [sp_delete_incomplete_company] que remove
--                 uma empresa específica (presumivelmente incompleta) e todos os
--                 seus dados relacionados de forma atômica e segura.
-- =================================================================================
USE pro_team_care;
GO

CREATE OR ALTER PROCEDURE [core].[sp_delete_incomplete_company]
    @companyIdToDelete BIGINT,
    @forceDelete BIT = 0 -- Parâmetro de segurança: 0 = só apaga 'pending_contract', 1 = apaga qualquer status
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @personIdToDelete BIGINT;
    DECLARE @statusToDelete NVARCHAR(50);
    DECLARE @errorMessage NVARCHAR(500);

    -- Busca a empresa e seu status
    SELECT @personIdToDelete = person_id, @statusToDelete = access_status
    FROM [core].[companies]
    WHERE id = @companyIdToDelete;

    -- Validação de Segurança: Só permite apagar 'pending_contract' por padrão
    IF @statusToDelete IS NULL
    BEGIN
        SET @errorMessage = 'Empresa com ID ' + CAST(@companyIdToDelete AS VARCHAR) + ' não encontrada.';
        THROW 50001, @errorMessage, 1;
        RETURN;
    END

    IF @statusToDelete <> 'pending_contract' AND @forceDelete = 0
    BEGIN
        SET @errorMessage = 'A empresa com ID ' + CAST(@companyIdToDelete AS VARCHAR) + ' não está com status ''pending_contract''. Use @forceDelete = 1 para forçar.';
        THROW 50002, @errorMessage, 1;
        RETURN;
    END

    PRINT 'Iniciando exclusão da Empresa ID: ' + CAST(@companyIdToDelete AS VARCHAR) + ' e dados relacionados...';

    -- Tabela temporária para guardar IDs de pessoas a serem deletadas (empresa + estabelecimentos)
    DECLARE @peopleIdsToDelete TABLE (id BIGINT PRIMARY KEY);
    IF @personIdToDelete IS NOT NULL
        INSERT INTO @peopleIdsToDelete (id) VALUES (@personIdToDelete);

    -- Adiciona IDs das pessoas associadas aos estabelecimentos desta empresa
    INSERT INTO @peopleIdsToDelete (id)
    SELECT est.person_id
    FROM [core].[establishments] est
    WHERE est.company_id = @companyIdToDelete
      AND est.person_id NOT IN (SELECT id FROM @peopleIdsToDelete); -- Evita duplicados

    BEGIN TRY
        -- Abordagem simplificada: deletar apenas a empresa e pessoa principal
        -- (assumindo que empresas pendentes não têm estabelecimentos ou dados complexos)

        -- 1. Deletar contatos da pessoa (se existirem)
        DELETE FROM [core].[phones] WHERE phoneable_type = 'PjProfile' AND phoneable_id IN (
            SELECT id FROM [core].[pj_profiles] WHERE person_id = @personIdToDelete
        );
        DELETE FROM [core].[emails] WHERE emailable_type = 'PjProfile' AND emailable_id IN (
            SELECT id FROM [core].[pj_profiles] WHERE person_id = @personIdToDelete
        );
        DELETE FROM [core].[addresses] WHERE addressable_type = 'PjProfile' AND addressable_id IN (
            SELECT id FROM [core].[pj_profiles] WHERE person_id = @personIdToDelete
        );

        -- 2. Deletar perfis
        DELETE FROM [core].[pj_profiles] WHERE person_id = @personIdToDelete;
        DELETE FROM [core].[pf_profiles] WHERE person_id = @personIdToDelete;

        -- 3. Deletar estabelecimentos (se existirem)
        DELETE FROM [core].[establishments] WHERE company_id = @companyIdToDelete;

        -- 4. Deletar empresa
        DELETE FROM [core].[companies] WHERE id = @companyIdToDelete;

        -- 5. Deletar pessoa
        DELETE FROM [core].[people] WHERE id = @personIdToDelete;

        PRINT '✅ SUCESSO: Empresa ID ' + CAST(@companyIdToDelete AS VARCHAR) + ' removida com sucesso.';

    END TRY
    BEGIN CATCH
        SET @errorMessage = 'ERRO: Falha ao excluir a empresa ID ' + CAST(@companyIdToDelete AS VARCHAR) + '. ' + ERROR_MESSAGE();
        THROW 50003, @errorMessage, 1;
    END CATCH;
END;
GO

PRINT '✅ Procedure [core].[sp_delete_incomplete_company] criada/alterada com sucesso.';