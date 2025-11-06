-- =============================================
-- Script: 054_Import_Dasa_Cards_v2.sql
-- Descrição: Importa cards a partir de uma lista de INSERTs, incluindo DisplayOrder.
-- Autor: Gemini
-- Data: 2025-11-05
-- Versão: 2.0
-- =============================================

USE [pro_team_care];
GO

BEGIN TRANSACTION;

BEGIN TRY
    DECLARE @CompanyID BIGINT = 1;
    DECLARE @UserID BIGINT = 1;

    -- Mapeamento de Colunas
    DECLARE @BacklogID INT = 1;
    DECLARE @EmAndamentoID INT = 3;
    DECLARE @ConcluidoID INT = 5;

    PRINT 'Iniciando a inserção de novos cards (v2)...';

    -- Inserindo os cards com DisplayOrder
    INSERT INTO [core].[Cards] (CompanyID, UserID, ColumnID, Title, Description, Priority, DueDate, StartDate, CompletedDate, DisplayOrder) VALUES
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM Deploy Programas', 'Demandas em Pronto para Publica??o.', 'Average', '2025-11-03', '2025-11-03 09:42:58', '2025-11-04 09:38:16', 1),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] -Workflow de Cancelamento - Solicita??o de Cria??o de Grupo AD', 'Objetivo: Solicitar cria??o de grupo no AD para controle de acesso de aplica??o do Workflow no PSCD...', 'Average', '2025-11-03', '2025-10-29 18:13:44', NULL, 2),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] Criar Grupos - GG_BR_APL_PSCD_APROV_HML e GG_BR_APL_PSCD_APROV_PROD', 'Solicitar cria??o do grupo para o portal de acesso...', 'Average', '2025-10-29', '2025-10-29 09:49:13', NULL, 3),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] -  Abrir RDM para atividade do DBA nos bancos', 'Para manter o PSCD com performance e estvel, ser feita uma manuten??o preventiva em bancos do sistema...', 'Average', '2025-10-29', '2025-10-29 09:18:28', '2025-11-04 09:37:38', 4),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - 23. Evidncia de GMUD para a amostra selecionada', '23. Evidncia de GMUD para a amostra selecionada OBS: As evidncias devem demonstrar o ticket da GMUD...', 'Average', '2025-10-28', '2025-10-27 12:09:30', '2025-10-29 08:59:44', 5),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajustar Interface de Rede de backup - LNXPODPRO01 - 10.122.20.46 / Prev. 05/11', 'Alinhado com o Antonio para adequar a interface de rede de Backup...', 'Average', '2025-11-05', '2025-10-27 11:54:40', '2025-10-29 09:00:51', 6),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Liberar Azure K8S x PSCD', 'Foi feito este Fireflow pelo daniel mas foi encerrado, sem executar...', 'Average', '2025-10-28', '2025-10-27 11:06:31', '2025-10-30 10:04:26', 7),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075677- PSCD- Entrega de Demandas Homologadas da Sprint -Programas(2025-10-16)', NULL, 'Average', NULL, '2025-10-17 10:15:25', '2025-10-20 09:48:56', 8),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075613- PSCD- Reconstru??o de Replica dos Bancos de Dados  do Sistema - DAPACIENTE', NULL, 'Average', NULL, '2025-10-17 10:14:11', '2025-10-27 11:02:37', 9),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075607- Manuten??o de Performance PSCD- Dump/Load dos Bancos TORRE IF e DAPACIENTE', NULL, 'Average', NULL, '2025-10-17 10:06:34', '2025-10-20 09:48:51', 10),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM DUMP/LOAD torre_if e dapaciente', NULL, 'Average', '2025-10-10', '2025-10-10 15:32:52', '2025-10-13 09:50:30', 11),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Levantar Licenas PASOE - Validar se foi trocado', NULL, 'Average', '2025-10-10', '2025-10-10 10:05:54', '2025-10-13 14:58:46', 12),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Gerar evidencias auditoria', NULL, 'Average', '2025-10-09', '2025-10-09 15:15:32', '2025-10-10 09:39:24', 13),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] RDM CHG0075279 - Criacao de usuario de servico do  PSCD \ PASOE', 'Testes Durante a execu??o.', 'Average', '2025-10-06', '2025-10-06 18:04:50', '2025-10-07 09:57:54', 14),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajuste Envio e-mail - Erro ao enviar mltiplos anexos', 'Durante os testes foi identificado problemas ao fazer o envio com mltiplos anexos...', 'Average', '2025-10-06', '2025-10-06 09:35:17', '2025-10-10 09:40:23', 15),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - PI 4 2025 - Atividades Diversas', NULL, 'Average', '2025-10-03', '2025-10-01 16:34:48', '2025-10-10 09:40:19', 16),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Elaboar DOC Auditoria', NULL, 'Average', '2025-09-30', '2025-09-30 14:45:42', '2025-09-30 14:47:22', 17),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] - Worflow de Cancelamento', 'Solicita??o Elaborado Pelo Michael:', 'Average', '2025-10-01', '2025-09-29 10:11:00', NULL, 18),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM CHG0074894 - Gliese - Implantar vers?o 191 na Piloto(atendepiloto.dasa.com.br) e virar 190 para BR(atende.dasa.com.br)', 'Apoiar implementa??o da RDM referente a apomyat o servio de gera??o do RPS para...', 'Average', NULL, '2025-09-25 18:51:53', '2025-09-29 10:07:39', 19),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - (315129) Ajuste envio de E-Mails com anexo do Linux', 'https://dasa.businessmap.io/ctrl_board/155/cards/315129/details/', 'Average', '2025-09-24', '2025-09-24 14:52:24', '2025-09-25 14:53:41', 20),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Falha no Envio de E-mails com Anexo: Documentos N?o Gerados', 'chamado : RITM0914705...', 'Average', '2025-10-20', '2025-09-24 14:45:52', '2025-10-21 19:31:25', 21),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] -Workflow de Cancelamento - Desenvolvimento', 'Objetivo: Elaborar um planejamento detalhado, tcnico e funcionais...', 'Average', '2025-10-06', NULL, NULL, 22),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Manuten??o de Banco de Dados - Novembro', 'Objetivo: Otimiza??o e manuten??o proativa de nossas bases do banco...', 'Average', NULL, NULL, NULL, 23),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Manuten??o de Banco de Dados - Outubro', 'Objetivo: Otimiza??o e manuten??o proativa de nossas bases do banco...', 'Average', NULL, NULL, NULL, 24),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Manuten??o de Banco de Dados - Julho', 'Objetivo: Otimiza??o e manuten??o proativa de nossas bases do banco...', 'Average', '2025-07-28', '2025-07-01 09:53:39', '2025-07-07 09:32:49', 25),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] -  Moderniza??o do PSCD - fase 2 - TROCA DO END POINT', 'Objetivo: Defini??es entre as reas de Gliese, Paperless e SAP...', 'Average', '2025-11-03', '2025-09-24 09:55:37', NULL, 26),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Planejamento - Workflow de Cancelamento', 'Objetivo: Elaborar um planejamento detalhado, tcnico e funcionais...', 'Average', '2025-11-03', '2025-10-08 16:20:55', '2025-10-29 18:15:55', 27),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Ajustar o relatrio do Clculo da Provis?o Mensal para controle de Status no exame', 'Objetivo:
Hoje o controle de valores da provis?o  feito com base no cod. status do paciente(atendimento)...', 'Average', '2025-05-05', '2025-06-24 09:50:05', '2025-06-24 09:50:36', 28),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Clculo da Provis?o Mensal para Status por exames', 'Objetivo: Fazer uma analise detalhada do processo de Clculo de provis?o para adapta??o do processo de status no exame...', 'Average', '2025-05-19', '2025-04-08 15:42:25', '2025-07-21 15:54:53', 29),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Criar Relatrio Baseado no ESFT111 adaptado as funcionalidade de controle de Status por exame ( RL2111)', 'Objetivo:Criar um relatorio RL2111, clonar do relatorio ESFT111...', 'Average', '2025-04-21', '2025-04-08 15:55:06', '2025-04-24 20:53:43', 30);

    PRINT CAST(@@ROWCOUNT AS VARCHAR) + ' cards inseridos com sucesso.';

    COMMIT TRANSACTION;
    PRINT '✅ SUCESSO: Importação concluída e transação commitada.';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '❌ ERRO: A operação de importação falhou e a transação foi revertida.';
    THROW;
END CATCH
GO
