-- =============================================
-- Script: 054_Import_Dasa_Cards_v3.sql
-- Descrição: Importa TODOS os 99 cards a partir de uma lista de INSERTs.
-- Autor: Gemini
-- Data: 2025-11-05
-- Versão: 3.0
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

    PRINT 'Iniciando a inserção de 99 novos cards (v3)...';

    -- Inserindo os cards com DisplayOrder
    INSERT INTO [core].[Cards] (CompanyID, UserID, ColumnID, Title, Description, Priority, DueDate, StartDate, CompletedDate, DisplayOrder) VALUES
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM Deploy Programas', 'Demandas em Pronto para Publicação.', 'Average', '2025-11-03', '2025-11-03 09:42:58', '2025-11-04 09:38:16', 1),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] -Workflow de Cancelamento - Solicitação de Criação de Grupo AD', 'Objetivo: Solicitar criação de grupo no AD para controle de acesso de aplicação do Workflow no PSCD...', 'Average', '2025-11-03', '2025-10-29 18:13:44', NULL, 2),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] Criar Grupos - GG_BR_APL_PSCD_APROV_HML e GG_BR_APL_PSCD_APROV_PROD', 'Solicitar criação do grupo para o portal de acesso...', 'Average', '2025-10-29', '2025-10-29 09:49:13', NULL, 3),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] -  Abrir RDM para atividade do DBA nos bancos', 'Para manter o PSCD com performance e estvel, será feita uma manutenção preventiva em bancos do sistema...', 'Average', '2025-10-29', '2025-10-29 09:18:28', '2025-11-04 09:37:38', 4),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - 23. Evidência de GMUD para a amostra selecionada', '23. Evidência de GMUD para a amostra selecionada OBS: As evidências devem demonstrar o ticket da GMUD...', 'Average', '2025-10-28', '2025-10-27 12:09:30', '2025-10-29 08:59:44', 5),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajuste Interface de Rede de backup - LNXPODPRO01 - 10.122.20.46 / Prev. 05/11', 'Alinhado com o Antonio para adequar a interface de rede de Backup...', 'Average', '2025-11-05', '2025-10-27 11:54:40', '2025-10-29 09:00:51', 6),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Liberar Azure K8S x PSCD', 'Foi feito este Fireflow pelo daniel mas foi encerrado, sem executar...', 'Average', '2025-10-28', '2025-10-27 11:06:31', '2025-10-30 10:04:26', 7),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075677- PSCD- Entrega de Demandas Homologadas da Sprint -Programas(2025-10-16)', NULL, 'Average', NULL, '2025-10-17 10:15:25', '2025-10-20 09:48:56', 8),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075613- PSCD- Reconstrução de Replica dos Bancos de Dados  do Sistema - DAPACIENTE', NULL, 'Average', NULL, '2025-10-17 10:14:11', '2025-10-27 11:02:37', 9),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075607- Manutenção de Performance PSCD- Dump/Load dos Bancos TORRE IF e DAPACIENTE', NULL, 'Average', NULL, '2025-10-17 10:06:34', '2025-10-20 09:48:51', 10),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM DUMP/LOAD torre_if e dapaciente', NULL, 'Average', '2025-10-10', '2025-10-10 15:32:52', '2025-10-13 09:50:30', 11),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Levantar Licenas PASOE - Validar se foi trocado', NULL, 'Average', '2025-10-10', '2025-10-10 10:05:54', '2025-10-13 14:58:46', 12),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Gerar evidencias auditoria', NULL, 'Average', '2025-10-09', '2025-10-09 15:15:32', '2025-10-10 09:39:24', 13),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] RDM CHG0075279 - Criacao de usuario de servico do  PSCD \ PASOE', 'Testes Durante a execução.', 'Average', '2025-10-06', '2025-10-06 18:04:50', '2025-10-07 09:57:54', 14),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajuste Envio e-mail - Erro ao enviar mltiplos anexos', 'Durante os testes foi identificado problemas...', 'Average', '2025-10-06', '2025-10-06 09:35:17', '2025-10-10 09:40:23', 15),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - PI 4 2025 - Atividades Diversas', NULL, 'Average', '2025-10-03', '2025-10-01 16:34:48', '2025-10-10 09:40:19', 16),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Elaboar DOC Auditoria', NULL, 'Average', '2025-09-30', '2025-09-30 14:45:42', '2025-09-30 14:47:22', 17),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] - Worflow de Cancelamento', 'Solicitação Elaborado Pelo Michael:', 'Average', '2025-10-01', '2025-09-29 10:11:00', NULL, 18),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM CHG0074894 - Gliese - Implantar versao 191 na Piloto(atendepiloto.dasa.com.br) e virar 190 para BR(atende.dasa.com.br)', 'Apoiar implementação da RDM...', 'Average', NULL, '2025-09-25 18:51:53', '2025-09-29 10:07:39', 19),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - (315129) Ajuste envio de E-Mails com anexo do Linux', 'https://dasa.businessmap.io/ctrl_board/155/cards/315129/details/', 'Average', '2025-09-24', '2025-09-24 14:52:24', '2025-09-25 14:53:41', 20),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Implementar RDM: CHG0074577 - PSCD - Atualização e Conversão dos Bancos de Dados no Ambiente Homologação', NULL, 'Average', '2025-09-21', '2025-09-22 09:41:34', '2025-09-22 09:41:34', 21),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Implementar RDM: CHG0074592 - PSCD - Reconstrução de Rplicas de todos os bancos de dados do Sistema', NULL, 'Average', '2025-10-24', '2025-09-20 16:51:37', '2025-10-10 09:43:45', 22),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] Implementar RDM: CHG0074562 - PSCD ? Entrega de Demandas Homologadas da Sprint ? Programas (2025-09-18)', NULL, 'Average', '2025-09-18', '2025-09-18 19:02:40', '2025-09-19 12:25:38', 23),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Code Review - 18/09/25', NULL, 'Average', '2025-09-18', '2025-09-18 11:57:48', '2025-10-03 10:01:02', 24),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Apoio  ao Celso em demanda', 'https://dasa.businessmap.io/ctrl_board/155/cards/307331/details/', 'Average', '2025-09-18', '2025-09-18 11:50:40', '2025-09-18 11:53:12', 25),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Integração PSCD => Paperless', NULL, 'Average', '2025-09-16', '2025-09-16 12:40:18', '2025-09-16 18:29:33', 26),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Usúario de Servio nas Maquinas do PASOE', NULL, 'Average', '2025-09-17', '2025-09-16 11:22:24', '2025-09-29 09:53:54', 27),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CHG0074592 - PSCD - Reconstrução de Rplicas de todos os bancos de dados do Sistema - Janela: 22/09/2025 09:00:00 a 24/10/2025 18:00:00', 'CHG0074592 - PSCD - Reconstrução de Rplicas...', 'Average', '2025-09-15', '2025-09-16 10:13:19', '2025-09-16 18:29:11', 28),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CHG0074577 - PSCD - Atualização e Conversão dos Bancos de Dados no Ambiente Homologação - Janela 19/09/2025 17:00 a 21/09/2025 23:59', 'CHG0074577 - PSCD - Atualização e Conversão...', 'Average', '2025-09-15', '2025-09-16 10:11:15', '2025-09-16 18:29:07', 29),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CHG0074562 - PSCD ? Entrega de Demandas Homologadas da Sprint ? Programas (2025-09-18) - Janela 18/09/2025 19:00 a 18/09/2025 20:30', 'Inserir RDM...', 'Average', '2025-09-15', '2025-09-16 10:09:05', '2025-09-16 18:29:02', 30),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Falha no Envio de E-mails com Anexo: Documentos Não Gerados', 'chamado : RITM0914705...', 'Average', '2025-10-20', '2025-09-24 14:45:52', '2025-10-21 19:31:25', 31),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 14/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:11:11', '2025-09-16 09:54:31', 32),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 13/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:10:46', '2025-09-16 09:54:29', 33),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 12/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:10:16', '2025-09-16 09:54:27', 34),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 11/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:09:57', '2025-09-16 09:54:26', 35),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 10/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:09:23', '2025-09-16 09:54:24', 36),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validação PowerCenter PRD progress', NULL, 'Average', '2025-09-09', '2025-09-10 09:54:18', '2025-09-10 09:55:30', 37),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar se Conector do OE10, se conecta a Base OE12 (HML) - PowerCenter', 'No Servidor de testes, apontar o driver do OE10 para conectar ao servidor de HML OE12', 'Average', '2025-09-05', '2025-09-08 12:14:29', '2025-09-08 14:07:18', 38),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Instalar OE12 32 Bits, no servidor BRLSPWPEMS02', NULL, 'Average', '2025-09-05', '2025-09-08 10:58:02', '2025-09-08 10:58:35', 39),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajuste de programas PSCD v12 x SAP CPI Dev - HML', NULL, 'Average', '2025-09-03', '2025-09-03 18:31:11', '2025-09-05 14:24:27', 40),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Configurar maquina Gold Horizon PROD', NULL, 'Average', '2025-09-03', '2025-09-03 18:28:17', '2025-09-10 09:52:49', 41),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CRIAR RDM - CHG0074051 - PSCD- PROJETO MODERNIZAÇÃO PSCD FASE 2', 'Feita a abertura da RDM...', 'Average', '2025-09-02', '2025-09-02 10:07:55', '2025-09-02 10:11:16', 42),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Planejar Atualização Servidor Horizon PSCD - Criar Clone', 'Ns temos que fazer uma atividade no servidor de Produção do PSCD do Horizon...', 'Average', NULL, '2025-08-29 16:30:20', '2025-09-02 10:11:09', 43),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Teste Integrado PSCDxSAP', NULL, 'Average', '2025-08-29', '2025-08-29 15:01:59', '2025-09-02 10:05:46', 44),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abertura RDM CHG0073936 - Repasse de conhecimento para Danubia', NULL, 'Average', '2025-08-29', '2025-08-29 11:42:57', '2025-08-29 14:59:15', 45),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar erro na execução do espr400a1.p (OE12)', NULL, 'Average', '2025-08-27', '2025-08-26 18:53:23', '2025-08-27 09:40:54', 46),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Apoio a testes e correções de Bugs Controle por exame', NULL, 'Average', '2025-08-26', '2025-08-26 15:26:05', '2025-08-26 15:37:12', 47),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Verificar problema no Proxy para chegar no endereço do SAP=>', NULL, 'Average', NULL, '2025-08-26 14:40:23', '2025-08-26 18:51:01', 48),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Levantar todos os CFG da versão 12', 'Nas maquinas linux e windows pegar o codigo CFG da versão 12...', 'Average', '2025-08-26', '2025-08-26 14:37:49', '2025-08-26 14:38:33', 49),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - 1 - Ajustar Programas: Consulta de RPS', 'https://dasa.businessmap.io/ctrl_board/155/cards/306392/details/', 'Average', '2025-08-26', '2025-08-25 17:57:50', '2025-09-10 10:02:23', 50),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Consulta de RPS', 'Objetivo:  criar o banco de dados local do RP e ativar redirect...', 'Average', '2025-09-22', '2025-08-25 17:55:53', '2025-09-16 18:28:50', 51),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Executar: CHG0073496 - PSCD - Entrega de Demandas  Homologadas Projeto Controle Status por Exame e DF', 'https://dasadesk.dasa.com.br/nav_to.do?uri=%2Fchange_request.do%3Fsys_id%3D7d797fc087a766909fa584440cbb350e...', 'Average', '2025-08-23', '2025-08-23 14:46:30', '2025-08-25 09:27:05', 52),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Avaliar proxy Servidor de QAS OE12', 'servio de envio de controle para o SAP', 'Average', '2025-08-20', '2025-08-20 11:17:35', '2025-08-21 11:49:18', 53),
    (@CompanyID, @UserID, @ConcluidoID, '[RDM] - Abertura de RDM - Status do exame', 'Objetivo: Abertura de RDM para virada do projeto Status no exame...', 'Average', '2025-08-19', '2025-08-19 17:28:25', '2025-08-22 12:36:13', 54),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] -  Abertura de RDM - Repasse  de Conhecimento para Danubia', 'Tema: PSCD - Projeto Controle Status por Exame Exame...', 'Average', NULL, '2025-08-19 11:51:51', '2025-08-19 16:55:02', 55),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]   - Implementação e Testes - Construir Redirect para o RPS', 'Anexo desenho, mas basicamente precisa redirecionar as request...', 'Average', '2025-08-20', '2025-08-21 11:49:13', '2025-08-21 17:40:21', 56),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Levantar e relacionar os programas novos e antigos /  construir um programa para copiar as permissões do programa antigo para novo', '1 Levantar e relacionar os programas novos e antigos...', 'Average', '2025-08-20', '2025-08-19 16:55:11', '2025-08-19 19:05:53', 57),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar execução do Fireflow: 8481 Liberar Portas Kubernets/SAP => PSCD', 'Depended on by: 8482: (admin) Liberar Portas Kubernets/SAP => PSCD...', 'Average', '2025-08-19', '2025-08-19 09:22:37', '2025-08-19 18:47:06', 58),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Executar RDM CHG0073206 - Atualizar Aplicação do PSCD na Horizon', NULL, 'Average', '2025-08-16', '2025-08-19 09:17:53', '2025-08-19 09:18:00', 59),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Mapeamento - Demanda Status por Exame', 'eunião Teams para planejamento para a implementação de RDM em 23/08...', 'Average', '2025-08-18', '2025-08-18 17:39:17', '2025-08-18 17:48:06', 60),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Code Review  Demanda: 292043 - Criar um relatório baseado no RL2111 porm com o nome RL2112', 'https://dasa.businessmap.io/ctrl_board/155/cards/292043/details/', 'Average', '2025-08-18', '2025-08-18 12:18:25', '2025-08-22 17:20:26', 61),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Fazer code review da demanda 291357', 'https://dasa.businessmap.io/ctrl_board/155/cards/291357/details/', 'Average', '2025-08-15', '2025-08-15 16:38:45', '2025-08-18 11:33:56', 62),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]   - Construir Redirect para o RPS', 'Anexo desenho, mas basicamente precisa redirecionar as request...', 'Average', '2025-08-15', '2025-08-13 16:07:43', '2025-08-15 16:37:29', 63),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Abertura de regra de firewall', '- Kubernets - SAP - PSCD', 'Average', '2025-08-13', '2025-08-13 12:04:46', '2025-08-13 15:49:09', 64),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Analise Técnica e Viabilidade - Demanda: 294828', 'https://dasa.businessmap.io/ctrl_board/155/cards/294828/details/', 'Average', '2025-08-13', '2025-08-13 11:10:17', '2025-08-13 11:42:31', 65),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar Ambiente Horizon MFA - PSCD', 'Validar junto com o Paulo ambiente de testes novo do Horizon...', 'Average', '2025-08-12', '2025-08-12 11:22:39', '2025-08-12 11:34:02', 66),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abertura de RDM  - Atualização da maquina Gold - 11/08/25', 'Objetivo: Preencher de RDM no Dasa Desk para atualização da maquina Gold...', 'Average', '2025-08-14', '2025-08-11 17:37:00', '2025-08-22 12:35:58', 67),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Teste lote WS ( Criticas )', 'Apoiar Vania e Andre nos testes da integração...', 'Average', '2025-08-11', '2025-08-11 11:40:48', '2025-08-11 16:53:04', 68),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Implementar RDM', 'Implementar RDM para atualizarmos o ambiente do PSCD no Horizon...', 'Average', '2025-08-11', '2025-08-11 10:53:36', '2025-08-13 11:02:57', 69),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]-Ajuste no Relatórios RL6008 - RL2086 - RL2011', 'RL6008: Erro: Relatório extrado não respeitou a seleção de status...', 'Average', '2025-07-14', '2025-07-02 19:41:48', '2025-08-11 16:48:29', 70),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] -Workflow de Cancelamento - Desenvolvimento', 'Objetivo: Elaborar um planejamento detalhado...', 'Average', '2025-10-06', NULL, NULL, 71),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Manutenção de Banco de Dados - Novembro', 'Objetivo: Otimização e manutenção proativa...', 'Average', NULL, NULL, NULL, 72),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Manutenção de Banco de Dados - Outubro', 'Objetivo: Otimização e manutenção proativa...', 'Average', NULL, NULL, NULL, 73),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Manutenção de Banco de Dados - Julho', 'Objetivo: Otimização e manutenção proativa...', 'Average', '2025-07-28', '2025-07-01 09:53:39', '2025-07-07 09:32:49', 74),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] -  Modernização do PSCD - fase 2 - TROCA DO END POINT', 'Objetivo: Definições entre as áreas de Gliese, Paperless e SAP...', 'Average', '2025-11-03', '2025-09-24 09:55:37', NULL, 75),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Planejamento - Workflow de Cancelamento', 'Objetivo: Elaborar um planejamento detalhado...', 'Average', '2025-11-03', '2025-10-08 16:20:55', '2025-10-29 18:15:55', 76),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Ajustar o relatório do Cálculo da Provisão Mensal para controle de Status no exame', 'Objetivo: Hoje o controle de valores da provisão  feito com base no cod. status do paciente(atendimento)...', 'Average', '2025-05-05', '2025-06-24 09:50:05', '2025-06-24 09:50:36', 77),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Clculo da Provisão Mensal para Status por exames', 'Objetivo: Fazer uma analise detalhada do processo de Cálculo de provisão...', 'Average', '2025-05-19', '2025-04-08 15:42:25', '2025-07-21 15:54:53', 78),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Criar Relatório Baseado no ESFT111 adaptado as funcionalidade de controle de Status por exame ( RL2111)', 'Objetivo:Criar um relatorio RL2111, clonar do relatorio ESFT111...', 'Average', '2025-04-21', '2025-04-08 15:55:06', '2025-04-24 20:53:43', 79),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar os programa de Carga ESPR035 de status para nova regra de controle de status no exame', 'Objetivo : ajustar seguintes pontos...', 'Average', '2025-03-24', '2025-03-20 09:40:21', '2025-03-25 10:03:15', 80),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Criar relatório RL2111 para controlar Status por Exame', 'Objetivo: Criar um relatorio RL2111, clonar do relatorio ESFT111...', 'Average', '2025-03-24', '2025-03-19 16:06:19', '2025-04-08 15:18:45', 81),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customização do  Status do exame Cancelado ( cancelamento do Lote )', 'Objetivo: Quando houver um cancelamento do lote...', 'Average', '2025-03-24', '2025-03-11 17:47:05', '2025-03-24 12:32:01', 82),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar os programa de Carga ESPR035 de status para nova regra de controle de status no exame', 'Objetivo: Adaptar os programas de carga de status existentes...', 'Average', '2025-03-24', '2025-03-11 14:34:57', '2025-03-25 10:03:14', 83),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar o processo de refazer os lotes conforme os status no exame', 'Objetivo: Sempre que ocorrer o retorno de consulta de Status da operadora...', 'Average', '2025-03-10', '2025-03-06 14:01:48', '2025-03-24 12:24:21', 84),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Customizar a transição do status 45 para 51 na troca de status por exame', 'Objetivo: Dependendo do retorno da operadora automatizar a troca de status...', 'Average', '2025-02-24', '2025-02-18 14:44:11', '2025-03-10 09:46:36', 85),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar os retornos das operadoras para controlar o status no exame', 'Objetivo: Para cada tipo de exame controlar o retorno do status da operadora...', 'Average', '2025-02-10', '2025-01-29 09:24:22', '2025-02-25 09:50:09', 86),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar a entrada das bases para gerar Pedidos controlando status no exame ? ESPR280', 'Objetivo: Gerar base na ESPR280 onde traga em nível de exame...', 'Average', '2025-02-10', '2025-01-29 09:24:19', '2025-02-25 09:49:40', 87),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar o Cadastro Status Atendimento', 'Objetivo: Indicar no atendimento se a operadora requer o controle em nível de exame...', 'Average', '2025-01-27', '2025-01-14 09:46:38', '2025-01-28 10:03:46', 88),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Customizar o Cadastro de Parâmetros de Convênio', 'Objetivo: Possibilitar a parametrização do controle dos exames por plano...', 'Average', '2025-01-27', '2025-01-14 09:46:30', '2025-01-28 10:03:42', 89),
    (@CompanyID, @UserID, @BacklogID, 'SCRM - 2025 PI 1 S1', 'Objetivo: - Customização dos cadastros e ajuste de banco de dados inserindo os campos novos;', 'Average', '2025-01-27', '2025-01-14 09:45:14', '2025-01-29 09:24:05', 90),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Corrigir Diretório de arquivos temporários de transação', 'Problema - Programa que geram arquivos temporários...', 'Average', '2024-12-13', '2024-12-10 15:17:04', '2024-12-16 22:03:48', 91),
    (@CompanyID, @UserID, @ConcluidoID, 'AMIL- Erro na resposta do Envio e Consulta dos Serviços de WS -  Integrações', 'Problema: O Servidor da Amil esta retornando o erro (504 Gateway Timeout)...', 'Average', NULL, '2024-12-06 00:27:36', '2024-12-09 09:56:46', 92),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]-ESPR130R2 Relatório Atendimentos Faturamento Digital', 'Problema: Erro: programa ESPR130R2 - ESPR130R2RP, relatório de imagem...', 'Average', '2025-02-10', '2025-01-20 09:58:07', '2025-02-11 09:55:54', 93),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Atualização do SO da Maquina BRLSPWPEMS02', 'Demanda: Ação: ...', 'Average', NULL, '2024-12-03 15:35:13', '2024-12-13 09:51:40', 94),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]- Saneamento Parte 3-Solicitação de Ajuste Tela Cadastro ESPR058 e ESPR064', 'Demanda: Solicitação  para criar uma lista suspensa em caixa alta...', 'Average', NULL, '2024-12-03 15:35:05', '2024-12-19 09:48:53', 95),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Piloto WS 4.01.00 - CAIXA', 'Demanda: Ação: REFINAMENTO TÉCNICO...', 'Average', NULL, '2024-12-03 15:34:56', '2024-12-16 22:03:43', 96),
    (@CompanyID, @UserID, @BacklogID, 'Amil - Erro na resposta do Envio e Consulta dos serviços de WS', 'Problema: O servidor da Amil esta retornando o erro (504 Gateway Timeout)...', 'Average', NULL, '2024-11-29 11:57:39', '2024-12-03 11:06:02', 97),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Faturamento Caption ALICE RDI e AC com divergencia de centavos - RITM0619787', 'Demanda: Environment ERRO O cálculo do Captation do convnio ALICE...', 'Average', NULL, '2024-09-17 16:10:12', '2024-12-06 09:47:19', 98),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Configurar WS 4.01.00 - CAIXA', 'Ação: Demanda: Documentação enviado da CAIXA está no anexo...', 'Average', NULL, '2024-09-17 10:47:55', '2024-12-05 09:50:05', 99);

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
