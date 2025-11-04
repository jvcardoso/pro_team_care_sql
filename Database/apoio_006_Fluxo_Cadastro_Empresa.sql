-- =================================================================================
-- Blueprint para a API: Fluxo de Cadastro Completo de Empresa
-- Descrição: Este script serve como guia para a implementação na aplicação.
--            A aplicação deve executar estes passos dentro de uma única transação.
-- =================================================================================

-- // Na sua API (Python), você iniciaria a transação aqui.
-- // Ex: async with db.begin():
BEGIN TRANSACTION;

BEGIN TRY
    -- Declaração de variáveis para guardar os IDs (a app fará isso em suas variáveis)
    DECLARE @companyId BIGINT;
    DECLARE @personId BIGINT;
    DECLARE @pjProfileId BIGINT;

    -- // 1. A API executa o PRIMEIRO comando: INSERT na tabela 'companies'.
    -- //    O campo 'person_id' fica NULO intencionalmente.
    PRINT '--- ETAPA 1: Criando a conta da empresa (person_id é NULL) ---';
    INSERT INTO [core].[companies] (access_status) VALUES ('pending_contract');

    -- // 2. A API recupera o ID da empresa que acabou de ser criada.
    SET @companyId = SCOPE_IDENTITY();
    PRINT 'Conta criada com ID: ' + CAST(@companyId AS VARCHAR);


    -- // 3. A API executa o SEGUNDO comando: INSERT na tabela 'people' (a raiz).
    -- //    Ela usa o @companyId recuperado no passo anterior.
    PRINT CHAR(10) + '--- ETAPA 2: Criando a Pessoa raiz e o Perfil Jurídico ---';
    INSERT INTO [core].[people] (company_id, name, status)
    VALUES (@companyId, 'Nova Clinica de Teste LTDA', 'active');

    -- // 4. A API recupera o ID da pessoa que acabou de ser criada.
    SET @personId = SCOPE_IDENTITY();
    PRINT 'Registro raiz [people] criado com ID: ' + CAST(@personId AS VARCHAR);


    -- // 5. A API executa o TERCEIRO comando: INSERT na tabela 'pj_profiles'.
    -- //    Ela usa tanto o @companyId quanto o @personId.
    INSERT INTO [core].[pj_profiles] (person_id, company_id, tax_id, trade_name)
    VALUES (@personId, @companyId, '98765432000100', 'Clínica Saúde Total');
    SET @pjProfileId = SCOPE_IDENTITY();
    PRINT 'Perfil [pj_profiles] criado com ID: ' + CAST(@pjProfileId AS VARCHAR);


    -- // 6. A API executa o QUARTO comando: UPDATE na tabela 'companies'.
    -- //    Isso "fecha o ciclo", preenchendo o 'person_id' que estava nulo.
    PRINT CHAR(10) + '--- ETAPA 3: Finalizando o vínculo (UPDATE) ---';
    UPDATE [core].[companies]
    SET person_id = @personId
    WHERE id = @companyId;
    PRINT 'Vínculo finalizado. O campo person_id agora está preenchido.';


    -- // 7. A API pode continuar inserindo outros dados relacionados (endereços, etc.)
    -- //    dentro da mesma transação.
    PRINT CHAR(10) + '--- ETAPA 4: Criando registros relacionados ---';
    INSERT INTO [core].[establishments] (person_id, company_id, code, type, is_principal)
    VALUES (@personId, @companyId, 'MATRIZ', 'matriz', 1);
    PRINT 'Estabelecimento Matriz criado.';


    -- // 8. Se todos os comandos executaram sem erro, a API envia o COMMIT.
    COMMIT TRANSACTION;
    PRINT CHAR(10) + '✅ SUCESSO: Cadastro completo da empresa foi realizado!';

END TRY
BEGIN CATCH
    -- // 9. Se QUALQUER um dos comandos acima falhar, a API deve enviar o ROLLBACK.
    ROLLBACK TRANSACTION;
    PRINT CHAR(10) + '❌ ERRO: Ocorreu um problema e o cadastro foi desfeito (rollback).';
    -- A API deve capturar o erro e retornar uma resposta apropriada (ex: HTTP 500).
    THROW;
END CATCH
GO
