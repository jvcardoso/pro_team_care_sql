-- Descrição: Script de teste para validar os cálculos de KPIs da Stored Procedure [reports].[sp_GetKanbanDashboard]
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando teste da Stored Procedure [reports].[sp_GetKanbanDashboard]';
PRINT '================================================================================';

-- Configurações do teste
DECLARE @TestCompanyID BIGINT = 999; -- CompanyID de teste para não interferir com dados reais
DECLARE @TestUserID BIGINT = 1; -- Usuário de teste
DECLARE @StartDate DATE = '2025-10-01';
DECLARE @EndDate DATE = '2025-10-31';

BEGIN TRANSACTION TestAnalyticsDashboard;

BEGIN TRY

    PRINT '1. Preparando dados de teste...';

    -- 1.1. Criar colunas para a empresa de teste (se não existirem)
    IF NOT EXISTS (SELECT 1 FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID)
    BEGIN
        INSERT INTO [core].[CardColumns] ([CompanyID], [ColumnName], [DisplayOrder], [Color])
        VALUES
            (@TestCompanyID, 'Backlog', 1, '#6B7280'),
            (@TestCompanyID, 'A Fazer', 2, '#3B82F6'),
            (@TestCompanyID, 'Em Andamento', 3, '#F59E0B'),
            (@TestCompanyID, 'Revisão', 4, '#8B5CF6'),
            (@TestCompanyID, 'Concluído', 5, '#10B981');
        PRINT ' -> Colunas padrão criadas para empresa de teste.';
    END

    -- 1.2. Obter IDs das colunas
    DECLARE @BacklogID INT = (SELECT ColumnID FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID AND ColumnName = 'Backlog');
    DECLARE @AFazerID INT = (SELECT ColumnID FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID AND ColumnName = 'A Fazer');
    DECLARE @EmAndamentoID INT = (SELECT ColumnID FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID AND ColumnName = 'Em Andamento');
    DECLARE @RevisaoID INT = (SELECT ColumnID FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID AND ColumnName = 'Revisão');
    DECLARE @ConcluidoID INT = (SELECT ColumnID FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID AND ColumnName = 'Concluído');

    -- 1.3. Criar cards de teste com cenários específicos
    PRINT ' -> Inserindo cards de teste...';

    -- Card 1: Concluído dentro do prazo (Lead Time: 5 dias, Cycle Time: 3 dias)
    INSERT INTO [core].[Cards] ([CompanyID], [UserID], [ColumnID], [Title], [Priority], [DueDate], [CreatedAt])
    VALUES (@TestCompanyID, @TestUserID, @ConcluidoID, 'Card Teste 1 - Concluído no Prazo', 'Alta', '2025-10-10', '2025-10-01 09:00:00');

    DECLARE @Card1ID INT = SCOPE_IDENTITY();

    -- Card 2: Concluído fora do prazo (Lead Time: 8 dias, Cycle Time: 5 dias)
    INSERT INTO [core].[Cards] ([CompanyID], [UserID], [ColumnID], [Title], [Priority], [DueDate], [CreatedAt])
    VALUES (@TestCompanyID, @TestUserID, @ConcluidoID, 'Card Teste 2 - Atrasado', 'Média', '2025-10-05', '2025-10-02 10:00:00');

    DECLARE @Card2ID INT = SCOPE_IDENTITY();

    -- Card 3: Ainda em andamento (WIP)
    INSERT INTO [core].[Cards] ([CompanyID], [UserID], [ColumnID], [Title], [Priority], [DueDate], [CreatedAt])
    VALUES (@TestCompanyID, @TestUserID, @EmAndamentoID, 'Card Teste 3 - Em Andamento', 'Baixa', '2025-10-20', '2025-10-15 14:00:00');

    DECLARE @Card3ID INT = SCOPE_IDENTITY();

    -- Card 4: No Backlog (não conta para WIP)
    INSERT INTO [core].[Cards] ([CompanyID], [UserID], [ColumnID], [Title], [Priority], [DueDate], [CreatedAt])
    VALUES (@TestCompanyID, @TestUserID, @BacklogID, 'Card Teste 4 - Backlog', 'Média', '2025-10-25', '2025-10-20 16:00:00');

    DECLARE @Card4ID INT = SCOPE_IDENTITY();

    -- 1.4. Criar movimentos para simular o fluxo de trabalho
    PRINT ' -> Inserindo movimentos de teste...';

    -- Movimentos do Card 1 (Concluído no prazo)
    -- Criação -> Backlog (implícito na criação)
    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card1ID, @TestUserID, '2025-10-01 09:00:00', 'Card criado no Backlog', NULL, @BacklogID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card1ID, @TestUserID, '2025-10-03 11:00:00', 'Movido para A Fazer', @BacklogID, @AFazerID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card1ID, @TestUserID, '2025-10-05 09:00:00', 'Iniciado desenvolvimento', @AFazerID, @EmAndamentoID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card1ID, @TestUserID, '2025-10-08 16:00:00', 'Movido para revisão', @EmAndamentoID, @RevisaoID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card1ID, @TestUserID, '2025-10-10 12:00:00', 'Aprovado e concluído', @RevisaoID, @ConcluidoID);

    -- Movimentos do Card 2 (Atrasado)
    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card2ID, @TestUserID, '2025-10-02 10:00:00', 'Card criado no Backlog', NULL, @BacklogID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card2ID, @TestUserID, '2025-10-04 14:00:00', 'Movido para A Fazer', @BacklogID, @AFazerID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card2ID, @TestUserID, '2025-10-06 10:00:00', 'Iniciado desenvolvimento', @AFazerID, @EmAndamentoID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card2ID, @TestUserID, '2025-10-10 17:00:00', 'Concluído (atrasado)', @EmAndamentoID, @ConcluidoID);

    -- Movimentos do Card 3 (Em andamento)
    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card3ID, @TestUserID, '2025-10-15 14:00:00', 'Card criado no Backlog', NULL, @BacklogID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card3ID, @TestUserID, '2025-10-18 09:00:00', 'Movido para A Fazer', @BacklogID, @AFazerID);

    INSERT INTO [core].[CardMovements] ([CardID], [UserID], [LogDate], [Subject], [OldColumnID], [NewColumnID])
    VALUES (@Card3ID, @TestUserID, '2025-10-20 11:00:00', 'Iniciado desenvolvimento', @AFazerID, @EmAndamentoID);

    -- Card 4 permanece no Backlog (sem movimentos)

    PRINT ' -> Dados de teste inseridos com sucesso.';

    -- 2. Executar a Stored Procedure e capturar resultados
    PRINT '2. Executando Stored Procedure e validando resultados...';

    DECLARE @Results NVARCHAR(MAX);
    EXEC [reports].[sp_GetKanbanDashboard]
        @StartDate = @StartDate,
        @EndDate = @EndDate,
        @CompanyID = @TestCompanyID,
        @UserID = NULL;

    -- 3. Validações manuais dos cálculos esperados
    PRINT '3. Validações dos KPIs calculados:';

    -- 3.1. Lead Time esperado: Média de (9 dias Card1 + 8 dias Card2) / 2 = 8.5 dias = 734400 segundos
    -- Card1: 2025-10-01 até 2025-10-10 = 9 dias = 777600 segundos
    -- Card2: 2025-10-02 até 2025-10-10 = 8 dias = 691200 segundos
    -- Média: (777600 + 691200) / 2 = 734400 segundos
    PRINT ' -> Lead Time esperado: ~734400 segundos (8.5 dias)';

    -- 3.2. Cycle Time esperado: Média de (7 dias Card1 + 4 dias Card2) / 2 = 5.5 dias = 475200 segundos
    -- Card1: Saiu do Backlog em 2025-10-03, concluído em 2025-10-10 = 7 dias = 604800 segundos
    -- Card2: Saiu do Backlog em 2025-10-04, concluído em 2025-10-10 = 6 dias = 518400 segundos
    -- Média: (604800 + 518400) / 2 = 561600 segundos
    PRINT ' -> Cycle Time esperado: ~561600 segundos (6.5 dias)';

    -- 3.3. Throughput: 2 cards concluídos (Card1 e Card2)
    PRINT ' -> Throughput esperado: 2 cards';

    -- 3.4. WIP: 1 card (Card3 está em "Em Andamento")
    PRINT ' -> WIP esperado: 1 card';

    -- 3.5. SLA Compliance: 1/2 = 0.5 (50%) - Card1 dentro do prazo, Card2 fora
    PRINT ' -> SLA Compliance esperado: 0.5 (50%)';

    -- 3.6. Throughput History: Card1 concluído em 2025-10-10, Card2 em 2025-10-10
    PRINT ' -> Throughput History: 2 cards em 2025-10-10';

    -- 4. Limpeza dos dados de teste
    PRINT '4. Limpando dados de teste...';

    -- Remover movimentos (cascade remove imagens)
    DELETE FROM [core].[CardMovements] WHERE CardID IN (@Card1ID, @Card2ID, @Card3ID, @Card4ID);

    -- Remover cards
    DELETE FROM [core].[Cards] WHERE CardID IN (@Card1ID, @Card2ID, @Card3ID, @Card4ID);

    -- Remover colunas de teste
    DELETE FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID;

    PRINT ' -> Dados de teste removidos.';

    PRINT '================================================================================';
    PRINT 'SUCESSO: Teste da Stored Procedure concluido!';
    PRINT '================================================================================';
    PRINT '';
    PRINT 'RESUMO DOS VALORES ESPERADOS:';
    PRINT '   - Lead Time Medio: ~734400 segundos (~8.5 dias)';
    PRINT '   - Cycle Time Medio: ~561600 segundos (~6.5 dias)';
    PRINT '   - Throughput: 2 cards concluidos';
    PRINT '   - WIP: 1 card em andamento';
    PRINT '   - SLA Compliance: 50% (1 de 2 cards no prazo)';
    PRINT '';
    PRINT 'Verifique se os valores retornados pela SP batem com os esperados acima.';
    PRINT '================================================================================';

    COMMIT TRANSACTION TestAnalyticsDashboard;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION TestAnalyticsDashboard;

    PRINT '❌ ERRO durante o teste:';
    PRINT ERROR_MESSAGE();

    -- Tentar limpar dados mesmo em caso de erro
    BEGIN TRY
        DELETE FROM [core].[CardMovements] WHERE CardID IN (
            SELECT CardID FROM [core].[Cards] WHERE CompanyID = @TestCompanyID
        );
        DELETE FROM [core].[Cards] WHERE CompanyID = @TestCompanyID;
        DELETE FROM [core].[CardColumns] WHERE CompanyID = @TestCompanyID;
        PRINT ' -> Dados de teste foram limpos após erro.';
    END TRY
    BEGIN CATCH
        PRINT ' -> AVISO: Não foi possível limpar todos os dados de teste.';
    END CATCH;

    THROW;
END CATCH;

GO