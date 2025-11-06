-- =============================================
-- Script: 054_Import_Dasa_Cards.sql
-- Descrição: Importa cards a partir de uma lista de INSERTs.
-- Autor: Gemini
-- Data: 2025-11-05
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

    PRINT 'Iniciando a inserção de novos cards...';

    -- Inserindo os cards
    INSERT INTO [core].[Cards] (CompanyID, UserID, ColumnID, Title, Description, Priority, DueDate, StartDate, CompletedDate) VALUES
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM Deploy Programas', 'Demandas em Pronto para Publicação.', 'Average', '2025-11-03', '2025-11-03 09:42:58', '2025-11-04 09:38:16'),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] -Workflow de Cancelamento - Solicitação de Criação de Grupo AD', 'Objetivo: Solicitar criação de grupo no AD para controle de acesso de aplicação do Workflow no PSCD

Criação do grupo para o portal de acesso:

- GG_BR_APL_PSCD_APROV_HML

- GG_BR_APL_PSCD_APROV_PROD

Seguir lista de aprovadores conforme solicitado pela área de negócio:', 'Average', '2025-11-03', '2025-10-29 18:13:44', NULL),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] Criar Grupos - GG_BR_APL_PSCD_APROV_HML e GG_BR_APL_PSCD_APROV_PROD', 'Solicitar criação do grupo para o portal de acesso:

- GG_BR_APL_PSCD_APROV_HML

- GG_BR_APL_PSCD_APROV_PROD

Aprovadores :

- Area de Negocio Processos Recebíveis
- Area de TI (Lino, Alan, Juliano e Daniel)

Negocio:
f35188127857 Larissa Cristina Silva Oliveira Gusmao
f11482054892 Camilo Estefanuto
TI:
f28599206842 - Alan Oliveira Muniz
f21601741812 - Ricardo Lino
f22209249805 - Daniel da Silva Nascimento
f26436305807 - Juliano Ventura Cardoso

https://dasa.businessmap.io/ctrl_board/155/cards/336695/details/', 'Average', '2025-10-29', '2025-10-29 09:49:13', NULL),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] -  Abrir RDM para atividade do DBA nos bancos', 'Para manter o PSCD com performance e estável, será feita uma manutenção preventiva em bancos do sistema.
Janela: 07/11/2025 (sexta), 18:00 as 09/11/2025 (domingo), 23:59
Indisponibilidade:
- Durante a janela de execução haverá indisponibilidade no acesso ao sistema PSCD.
- Todos os processos automáticos serão pausados e após a validação da RDM os dados represados serão processados
Disponibilidade:
- O serviço de consulta de RPS não será afetado pela RDM, ativo durante toda janela.
O que será feito:
- São duas Atividades nas instâncias, quem realiza  o DBA Jonivaldo e nós acompanhamos e validamos o ambiente depois da execução:
- Organização interna para melhorar velocidade de consulta (Reindexação).
- Ajuste de estrutura para melhor desempenho e uso de espaço (Reestruturação de áreas).
Instâncias/Atividades:

| Instância | Reindexar | Reestrutura
| dacomum | Sim | Não
| daesptiss | Sim | Não
| daprovisao | Não | Sim
| daifprod | Não | Sim
| daesp | Não | Sim', 'Average', '2025-10-29', '2025-10-29 09:18:28', '2025-11-04 09:37:38'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - 23. Evidência de GMUD para a amostra selecionada', '23. Evidência de GMUD para a amostra selecionada OBS: As evidências devem demonstrar o ticket da GMUD, aprovações (gestores responsáveis, CAB, áreas de negócio), implementação da GMUD no ambiente produtivo.

Lista de evidencias:
https://dasanet.sharepoint.com/:x:/r/sites/SistemasCorporativosOficial/Documentos%20Compartilhados/Siscorp/Auditoria/Auditoria%20Interna%20PSCD/Amostras%20GMUD.xlsx?d=w809f56ccd4cb412491c2fab698fb4cef&csf=1&web=1&e=LNvdKd

Novo DOC:

https://dasanet.sharepoint.com/:w:/r/sites/SistemasCorporativosOficial/Documentos%20Compartilhados/Siscorp/Auditoria/Auditoria%20Interna%20PSCD/Aud2025_PSCD_Item_23_Evidencias_GMUD_AmostraSelecionada%20NOVO.docx?d=w8fdf7f2ead6b433fbafdc09076a5e261&csf=1&web=1&e=U28qOt', 'Average', '2025-10-28', '2025-10-27 12:09:30', '2025-10-29 08:59:44'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajustar Interface de Rede de backup - LNXPODPRO01 - 10.122.20.46 / Prev. 05/11', 'Alinhado com o Antonio para adequar a interface de rede de Backup :
Adequar as maquinas de banco referente ao Backup que foi criticado novamente sobre a interface estar ausente ele tem que abri uma RDM sem impacto e sem indisponibilidade para:

- LNXPODPRO01 - 10.122.20.46

- Ja tem a interface de rede, porem sem IP atribuído e teria que criar um FS /opt/commvault 100GB

- BRLSPLPRPR03 - 10.120.20.69

- não tem ação , ja tem a interface para backup (10.120.20.69) e FS /opt/commvault', 'Average', '2025-11-05', '2025-10-27 11:54:40', '2025-10-29 09:00:51'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Liberar Azure K8S x PSCD', 'Foi feito este Fireflow pelo daniel mas foi encerrado, sem executar :
#8638 Liberar Azure K8S vs PSCD PASOE', 'Average', '2025-10-28', '2025-10-27 11:06:31', '2025-10-30 10:04:26'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075677- PSCD- Entrega de Demandas Homologadas da Sprint -Programas(2025-10-16)', NULL, 'Average', NULL, '2025-10-17 10:15:25', '2025-10-20 09:48:56'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075613- PSCD- Reconstrução de Replica dos Bancos de Dados  do Sistema - DAPACIENTE', NULL, 'Average', NULL, '2025-10-17 10:14:11', '2025-10-27 11:02:37'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM CHG0075607- Manutenção de Performance PSCD- Dump/Load dos Bancos TORRE IF e DAPACIENTE', NULL, 'Average', NULL, '2025-10-17 10:06:34', '2025-10-20 09:48:51'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abrir RDM DUMP/LOAD torre_if e dapaciente', NULL, 'Average', '2025-10-10', '2025-10-10 15:32:52', '2025-10-13 09:50:30'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Levantar Licenas PASOE - Validar se foi trocado', NULL, 'Average', '2025-10-10', '2025-10-10 10:05:54', '2025-10-13 14:58:46'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Gerar evidencias auditoria', NULL, 'Average', '2025-10-09', '2025-10-09 15:15:32', '2025-10-10 09:39:24'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] RDM CHG0075279 - Criacao de usuario de serviço do  PSCD \ PASOE', 'Testes Durante a execução.', 'Average', '2025-10-06', '2025-10-06 18:04:50', '2025-10-07 09:57:54'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajuste Envio e-mail - Erro ao enviar múltiplos anexos', 'Durante os testes foi identificado problemas ao fazer o envio com múltiplos anexos usando a nova API, vou ajustar para tratar na API quando receber estes dados.

LOG de ERRO:
[25/10/02@22:23:37.298-0300] P-2894648 T-2894648 1 4GL DASA-LOG API-EMAIL: Validações concludas com sucesso
[25/10/02@22:23:37.298-0300] P-2894648 T-2894648 1 4GL DASA-LOG API-EMAIL: Iniciando envio via SMTP direto (método unificado)
[25/10/02@22:23:37.298-0300] P-2894648 T-2894648 2 4GL 4GLTRACE Run pi-SMTP-DIRETO [pi-execute2 - utp/utapi019.p @ 490]
[25/10/02@22:23:37.298-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO: Iniciando envio via SMTP direto
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO: param-global.serv-mail: mail.dasa.com.br
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO: param-global.porta-mail: 25
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO DADOS ENVIO: Servidor=mail.dasa.com.br:25 | De=pscd_fat@dasa.com.br | Para=d.nascimento@dasa.com.br;juliano.cardoso@dasa.com.br | Assunto=Prazo expirado - Periodo: 30/05/2025-02/10/2025
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO: Corpo da mensagem montado - 293 caracteres
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO: Processando anexo: /integracao/spool/crontab/expirado/rel-prazo-expirado-02102025-222337.csv,/integracao/spool/crontab/expirado/rel-prazo-alerta-02102025-222337.csv
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG SMTP-DIRETO: ERRO - Arquivo anexo não encontrado: /integracao/spool/crontab/expirado/rel-prazo-expirado-02102025-222337.csv,/integracao/spool/crontab/expirado/rel-prazo-alerta-02102025-222337.csv
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 2 4GL 4GLTRACE Run pi-criar-erros "99997 Arquivo anexo não encontrado: /integracao/spool/crontab/expirado/rel-prazo-expirado-02102025-222337.csv,/integracao/spool/crontab/expirado/rel-prazo-alerta-02102025-222337.csv /integracao/spool/crontab/expirado/rel-prazo-expirado-02102025-222337.csv,/integracao/spool/crontab/expirado/rel-prazo-alerta-02102025-222337.csv" [pi-SMTP-DIRETO - utp/utapi019.p @ 2132]
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG API-EMAIL: ERRO no envio via SMTP direto
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 1 4GL DASA-LOG API-EMAIL: Processo finalizado COM ERRO em 0,016 segundos - 02/10/2025 22:23:37
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 2 4GL DYNOBJECTS Deleted PROCEDURE Handle:1002 (pi-envia-email esp/espr098_unix.p @ 727) utp/utapi019.p
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 2 4GL DYNOBJECTS Deleted PROCEDURE Handle:1004 ( @ 0) utp/ut-func.p
[25/10/02@22:23:37.299-0300] P-2894648 T-2894648 2 4GL DYNOBJECTS Deleted PROCEDURE Handle:1003 ( @ 0) utp/ut-win.p

/integracao/spool/crontab/expirado/rel-prazo-expirado-02102025-222337.csv
/integracao/spool/crontab/expirado/rel-prazo-alerta-02102025-222337.csv', 'Average', '2025-10-06', '2025-10-06 09:35:17', '2025-10-10 09:40:23'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - PI 4 2025 - Atividades Diversas', NULL, 'Average', '2025-10-03', '2025-10-01 16:34:48', '2025-10-10 09:40:19'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Elaboar DOC Auditoria', NULL, 'Average', '2025-09-30', '2025-09-30 14:45:42', '2025-09-30 14:47:22'),
    (@CompanyID, @UserID, @EmAndamentoID, '[PSCD] - Worflow de Cancelamento', 'Solicitação Elaborado Pelo Michael:', 'Average', '2025-10-01', '2025-09-29 10:11:00', NULL),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM CHG0074894 - Gliese - Implantar versão 191 na Piloto(atendepiloto.dasa.com.br) e virar 190 para BR(atende.dasa.com.br)', 'Apoiar implementação da RDM referente a apomyat o serviço de geração do RPS para

[pscdpasoe.dasa.com.br 8081](http://pscdpasoe.dasa.com.br:8081/)

https://dasa.businessmap.io/ctrl_board/155/cards/268834/details/', 'Average', NULL, '2025-09-25 18:51:53', '2025-09-29 10:07:39'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - (315129) Ajuste envio de E-Mails com anexo do Linux', 'https://dasa.businessmap.io/ctrl_board/155/cards/315129/details/', 'Average', '2025-09-24', '2025-09-24 14:52:24', '2025-09-25 14:53:41'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Implementar RDM: CHG0074577 - PSCD - Atualização e Conversão dos Bancos de Dados no Ambiente Homologação', NULL, 'Average', '2025-09-21', '2025-09-22 09:41:34', '2025-09-22 09:41:34'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Implementar RDM: CHG0074592 - PSCD - Reconstrução de Rplicas de todos os bancos de dados do Sistema', NULL, 'Average', '2025-10-24', '2025-09-20 16:51:37', '2025-10-10 09:43:45'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] Implementar RDM: CHG0074562 - PSCD ? Entrega de Demandas Homologadas da Sprint ? Programas (2025-09-18)', NULL, 'Average', '2025-09-18', '2025-09-18 19:02:40', '2025-09-19 12:25:38'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Code Review - 18/09/25', NULL, 'Average', '2025-09-18', '2025-09-18 11:57:48', '2025-10-03 10:01:02'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Apoio  ao Celso em demanda', 'https://dasa.businessmap.io/ctrl_board/155/cards/307331/details/', 'Average', '2025-09-18', '2025-09-18 11:50:40', '2025-09-18 11:53:12'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Integração PSCD => Paperless', NULL, 'Average', '2025-09-16', '2025-09-16 12:40:18', '2025-09-16 18:29:33'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Usuário de Serviço nas Maquinas do PASOE', NULL, 'Average', '2025-09-17', '2025-09-16 11:22:24', '2025-09-29 09:53:54'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CHG0074592 - PSCD - Reconstrução de Rplicas de todos os bancos de dados do Sistema - Janela: 22/09/2025 09:00:00 a 24/10/2025 18:00:00', 'CHG0074592 - PSCD - Reconstrução de Rplicas de todos os bancos de dados do Sistema - Janela: 22/09/2025 09:00:00 a 24/10/2025 18:00:00

Esta solicitação de mudança refere-se à ativação da replicação dos bancos de dados do sistema PSCD na versão OpenEdge 12.8. Devido à quebra da replicação provocada pela atualização do OpenEdge da versão 11.7 para 12.8, será necessário reconstruir as réplicas para garantir a sincronização correta dos dados entre servidores.

A atividade contempla a atualização do sistema operacional da máquina BRLSPLPRPR03 de RHEL 7.6 para RHEL 8.10, atualização do Java para versão 17, desinstalação da versão OpenEdge 11.7 e instalação da versão 12.8, movimentação gradual dos backups das bases provenientes do servidor LNXPODPRO01, parametrização para a replicação adequada e validação final do funcionamento das réplicas.

Estão envolvidas as réplicas dos seguintes bancos: interfull, daesp, dapaciente, daexame, daesptiss, daprovisao, daifprod, pscd01, torre_if, torre_pscd, torre_daesp, torre_imp, torre_nfe, e dacomum, a atividade exige uma janela longa de.

Esta ação é fundamental para restabelecer a integridade e desempenho da replicação, garantindo a alta disponibilidade e confiabilidade dos dados para as operações do sistema PSCD.

Plantão: Juliano - 17-99145-9588

Sala Teams:
https://teams.microsoft.com/l/meetup-join/19%3ameeting_OGYxMDFkMTUtNGMzMi00MWRmLThhNDMtYjkwY2YxNGM0ZThj%40thread.v2/0?context=%7b%22Tid%22%3a%22f41c4a4c-314b-499d-9a7a-39581944c704%22%2c%22Oid%22%3a%22cee0b022-d528-4994-89ca-e2ea4a3e1da2%22%7d', 'Average', '2025-09-15', '2025-09-16 10:13:19', '2025-09-16 18:29:11'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CHG0074577 - PSCD - Atualização e Conversão dos Bancos de Dados no Ambiente Homologação - Janela 19/09/2025 17:00 a 21/09/2025 23:59', 'CHG0074577 - PSCD - Atualização e Conversão dos Bancos de Dados no Ambiente Homologação - Janela 19/09/2025 17:00 a 21/09/2025 23:59

Esta requisição de mudança (RDM) refere-se à atualização dos bancos de dados do ambiente de Quality Assurance System (QAS), com o objetivo de garantir que o ambiente reflita fielmente o estado atual da produção, permitindo testes e validações mais precisas. Estaremos aproveitando um backup já realizado do ambiente produtivo, eliminando assim uma etapa que chegaria a durar quase 40 horas.

As atividades compreendem desde a liberação da área para receber o backup, restauração do backup de produção no ambiente QAS, conversão das bases de dados do OE1 para OE12, até a disponibilização das bases convertidas e validação funcional do ambiente.

A execução será realizada dentro da janela programada entre 19/09/2025 às 17:00 e 21/09/2025 às 23:59, conforme cronograma acordado.

Essa atualização é essencial para assegurar a integridade e consistência dos dados usados nas fases de homologação e testes, auxiliando a equipe de negócio na avaliação das demandas e garantindo a qualidade dos sistemas em desenvolvimento.

SALA TEAMS:
https://teams.microsoft.com/l/meetup-join/19%3ameeting_NmI3MDk4MTAtZTNkMC00MzI5LTlmZTAtMzRjMDUzN2IzYWRm%40thread.v2/0?context=%7b%22Tid%22%3a%22f41c4a4c-314b-499d-9a7a-39581944c704%22%2c%22Oid%22%3a%22cee0b022-d528-4994-89ca-e2ea4a3e1da2%22%7d', 'Average', '2025-09-15', '2025-09-16 10:11:15', '2025-09-16 18:29:07'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CHG0074562 - PSCD ? Entrega de Demandas Homologadas da Sprint ? Programas (2025-09-18) - Janela 18/09/2025 19:00 a 18/09/2025 20:30', 'Inserir RDM:
[CHG0074562 - PSCD ? Entrega de Demandas Homologadas da Sprint ? Programas (2025-09-18) -](https://dasadesk.dasa.com.br/nav_to.do?uri=%2Fchange_request.do%3Fsys_id%3D0b9bef3087c0f618868332280cbb3579%26sysparm_record_list%3Drequested_byDYNAMIC90d1921e5f510100a9ad2572f2b477fe%5EORDERBYDESCstart_date%26sysparm_record_row%3D2%26sysparm_record_rows%3D117%26sysparm_record_target%3Dchange_request%26sysparm_view%3D%26sysparm_view_forced%3Dtrue) Janela 18/09/2025 19:00 a 18/09/2025 20:30

Aplicar em produção Demandas homologadas durante a Sprint:
[PSCD]- Monitor de Lotes Guias XML - ESPR280
https://dasa.businessmap.io/ctrl_board/155/cards/292449/details/

[PSCD] - Alteração descrição TUSS 40314537 - Bradesco
https://dasa.businessmap.io/ctrl_board/155/cards/304832/details/

[PSCD]-Erro no programa ESPR007 na liberação de Lote
https://dasa.businessmap.io/ctrl_board/155/cards/303993/details/

[PSCD] - ESCD021 - Criação de plano e Convenio
https://dasa.businessmap.io/ctrl_board/155/cards/306356/details/

[PSCD] - ESPR280 - Ajustar opção refazer lote em situações de represados após criação do Pedido/Lote
https://dasa.businessmap.io/ctrl_board/155/cards/301556/details/

[PSCD] - "ESPR280-D06 - Correção na Importação da Base de Exames com Recurso de Glosa ativo
https://dasa.businessmap.io/ctrl_board/155/cards/306930/details/
-------------------------------------------------------------------------------------------------------------------------------------
Contato plantão: 17-99145-9588 - JULIANO.

Sala Teams:
https://teams.microsoft.com/l/meetup-join/19%3ameeting_ZTRiNDE4MmMtMjFkNi00MTkzLWIwNWItNjllYTA4MWJhZTE3%40thread.v2/0?', 'Average', '2025-09-15', '2025-09-16 10:09:05', '2025-09-16 18:29:02'),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Falha no Envio de E-mails com Anexo: Documentos Não Gerados', 'chamado : RITM0914705

Objetivo: verificar problema que esta ocorrendo no e-mail pscd_fat@dasa.com.br, responsavel pelo envio de anexos com as exclusões e reclculos de exames.

erro relacionado : /integracao/spool/tmpmail/execmail497740: line 1: uuencode: command not found', 'Average', '2025-10-20', '2025-09-24 14:45:52', '2025-10-21 19:31:25'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 14/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:11:11', '2025-09-16 09:54:31'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 13/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:10:46', '2025-09-16 09:54:29'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 12/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:10:16', '2025-09-16 09:54:27'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 11/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:09:57', '2025-09-16 09:54:26'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - RDM: CHG0074051 - PROJETO MODERNIZAÇÃO PSCD FASE 2 - Atividades dia 10/09/25', NULL, 'Average', '2025-09-10', '2025-09-10 10:09:23', '2025-09-16 09:54:24'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validação PowerCenter PRD progress', NULL, 'Average', '2025-09-09', '2025-09-10 09:54:18', '2025-09-10 09:55:30'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar se Conector do OE10, se conecta a Base OE12 (HML) - PowerCenter', 'No Servidor de testes, apontar o driver do OE10 para conectar ao servidor de HML OE12', 'Average', '2025-09-05', '2025-09-08 12:14:29', '2025-09-08 14:07:18'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Instalar OE12 32 Bits, no servidor BRLSPWPEMS02', NULL, 'Average', '2025-09-05', '2025-09-08 10:58:02', '2025-09-08 10:58:35'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Ajuste de programas PSCD v12 x SAP CPI Dev - HML', NULL, 'Average', '2025-09-03', '2025-09-03 18:31:11', '2025-09-05 14:24:27'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Configurar maquina Gold Horizon PROD', NULL, 'Average', '2025-09-03', '2025-09-03 18:28:17', '2025-09-10 09:52:49'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - CRIAR RDM - CHG0074051 - PSCD- PROJETO MODERNIZAÇÃO PSCD FASE 2', 'Feita a abertura da RDM:
Esta mudança consiste em implementar a atualização em produção do sistema PSCD, será implementado a atualização do OpenEdge devido o fabricante da tecnologia anunciar o fim do ciclo de vida da versão 11.7 para abril de 2025, A partir desta data, o suporte e as atualizações de segurança serão encerrados, o que representa um risco crítico para a continuidade e a integridade de nossas operações, por tanto precisamos fazer a migração do sistema para a versão mais atual, OpenEdge 12.8. Esta atualização não apenas garante o suporte e a conformidade, mas também posicionamento a plataforma para maior performance e escalabilidade a longo prazo, todo o processo já foi testado em ambiente produtivo.', 'Average', '2025-09-02', '2025-09-02 10:07:55', '2025-09-02 10:11:16'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Planejar Atualização Servidor Horizon PSCD - Criar Clone', 'Ns temos que fazer uma atividade no servidor de Produção do PSCD do Horizon , a virada do nosso sistema vai ocorre em 11/09 a 14/09, seria possível como eu comentei esses dias ja disponibilizar um clone da maquina atual, nós fazemos a atividade nele e no dia da virada efetiva ele como Produção e recriar o pool ?

No clone:

0 - Criar o clone

1 - Remover a instalação do openege 11

2 - Instalar o Openege 12

3 - Atualizar toda base de programas do PSCD Loca (Drive T: na VM)

4 - Ajustar os atalhos do do PSCD (que são chamados no menu da Horizon)

5 - Recriar o Pool

Na virada:

1 - Efetiva o clone como produção;

2 - Recriar o Pool do PSCD', 'Average', NULL, '2025-08-29 16:30:20', '2025-09-02 10:11:09'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Teste Integrado PSCDxSAP', NULL, 'Average', '2025-08-29', '2025-08-29 15:01:59', '2025-09-02 10:05:46'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abertura RDM CHG0073936 - Repasse de conhecimento para Danubia', NULL, 'Average', '2025-08-29', '2025-08-29 11:42:57', '2025-08-29 14:59:15'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar erro na execução do espr400a1.p (OE12)', NULL, 'Average', '2025-08-27', '2025-08-26 18:53:23', '2025-08-27 09:40:54'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Apoio a testes e correções de Bugs Controle por exame', NULL, 'Average', '2025-08-26', '2025-08-26 15:26:05', '2025-08-26 15:37:12'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Verificar problema no Proxy para chegar no endereço do SAP=>', NULL, 'Average', NULL, '2025-08-26 14:40:23', '2025-08-26 18:51:01'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Levantar todos os CFG da versão 12', 'Nas maquinas linux e windows pegar o código CFG da versão 12 que está em casa uma das maquinas abaixo e me passar?

- 10.120.52.11
- brlsplppas01
- brlsplppas02
- brlsplppas03
- brlsplhpas01
- VDI
- Client Horizon', 'Average', '2025-08-26', '2025-08-26 14:37:49', '2025-08-26 14:38:33'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - 1 - Ajustar Programas: Consulta de RPS', 'https://dasa.businessmap.io/ctrl_board/155/cards/306392/details/', 'Average', '2025-08-26', '2025-08-25 17:57:50', '2025-09-10 10:02:23'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Consulta de RPS', 'Objetivo:  criar o banco de dados local do RP e ativar redirect, executando e configurar o redirecionamento de dados, a fim de viabilizar a execução e os testes da tarefa pendente em um ambiente isolado.', 'Average', '2025-09-22', '2025-08-25 17:55:53', '2025-09-16 18:28:50'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Executar: CHG0073496 - PSCD - Entrega de Demandas  Homologadas Projeto Controle Status por Exame e DF', 'https://dasadesk.dasa.com.br/nav_to.do?uri=%2Fchange_request.do%3Fsys_id%3D7d797fc087a766909fa584440cbb350e%26sysparm_domain%3Dnull%26sysparm_domain_scope%3Dnull%26sysparm_view%3D%26sysparm_view_forced%3Dtrue', 'Average', '2025-08-23', '2025-08-23 14:46:30', '2025-08-25 09:27:05'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Avaliar proxy Servidor de QAS OE12', 'serviço de envio de controle para o SAP', 'Average', '2025-08-20', '2025-08-20 11:17:35', '2025-08-21 11:49:18'),
    (@CompanyID, @UserID, @ConcluidoID, '[RDM] - Abertura de RDM - Status do exame', 'Objetivo: Abertura de RDM para virada do projeto Status no exame.

CHG0073496 - PSCD - Entrega de Demandas Homologadas Projeto Controle Status por Exame e DF

Janela: 23/08/2025 08:00:00 a 24/08/2025 16:00:00', 'Average', '2025-08-19', '2025-08-19 17:28:25', '2025-08-22 12:36:13'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] -  Abertura de RDM - Repasse  de Conhecimento para Danubia', 'Tema: PSCD - Projeto Controle Status por Exame Exame
Indisponibilidade: Sim (2 horas de indisponibilidade)

-----------------------------------------------

1. Implementação (2 horas)
2. Teste e Validações (24 horas)
2.1 - Testar a aplicação ps implementação (4 horas)
  2.2 - Deixa as rotinas rodando automaticamente durante esse intervalo de tempo.
2.3 - Repassar todos os processos automaticos no domingo de manhã. (4 horas)
3. Rollback (2 horas)

-----------------------------------------------

RDM - 23/08/2024 08:00 as 24/08/2024 12:00 - (Janela de 28 horas com indisponibilidade de 2 horas)

1. Stop de todos os processos do PSCD => (30 minutos) => Juliano ou Daniel
2. Aplicar no banco de dados daprovisao o delta incremental "delta_provisao.df" => (30 minutos) => Jonivaldo
3. Deploy da aplicação => (30 minutos) => Juliano ou Daniel
4. Start de todos os processos do PSCD => (30 minutos) => => Juliano ou Daniel
5. Testes e Validações => (4 horas) => Vania ou Michael
6. Rollback Aplicação (2 hora) = Daniel ou Juliano', 'Average', NULL, '2025-08-19 11:51:51', '2025-08-19 16:55:02'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]   - Implementação e Testes - Construir Redirect para o RPS', 'Anexo desenho, mas basicamente precisa redirecionar as request do pscdapi.dasa.com.br para pscdpasoe.dasa.com.br

Nesse momento iremos fazer no ambiente de homologação

De: http://brlspwhems01.dasa.net:8081/wsa/wsa1/wsdl?targetURI=urn:asFaturRpsIF

Para: http://brlsplhpas01.dasa.net:8081/soap/wsdl?targetURI=urn:asFaturRpsIF

| http://brlspwhems01.dasa.net:8081/wsa/wsa1/wsdl?targetURI=urn:asFaturRpsIF | http://brlsplhpas01.dasa.net:8081/soap/wsdl?targetURI=urn:asFaturRpsIF

[Redirect.drawio.pdf](file:///C:/Users/F22209249805/Downloads/Redirect.drawio.pdf)', 'Average', '2025-08-20', '2025-08-21 11:49:13', '2025-08-21 17:40:21'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Levantar e relacionar os programas novos e antigos /  construir um programa para copiar as permissões do programa antigo para novo', '1 Levantar e relacionar os programas novos e antigos
2 Utilizar os dados do item 1 para construir um programa provisoria para copiar as permissões do programa antigo para novo', 'Average', '2025-08-20', '2025-08-19 16:55:11', '2025-08-19 19:05:53'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar execução do Fireflow: 8481 Liberar Portas Kubernets/SAP => PSCD', 'Depended on by:
8482: (admin) Liberar Portas Kubernets/SAP => PSCD - 5[23] [pending match]
8483: (admin) Liberar Portas Kubernets/SAP => PSCD - 6[23] [pending match]
8484: (admin) Liberar Portas Kubernets/SAP => PSCD - 1[23] [pending match]
8485: (admin) Liberar Portas Kubernets/SAP => PSCD - 4[23] [pending match]
8486: (admin) Liberar Portas Kubernets/SAP => PSCD - 2[23] [pending match]
8487: (admin) Liberar Portas Kubernets/SAP => PSCD - 8[23] [pending match]
8488: (admin) Liberar Portas Kubernets/SAP => PSCD - 7[23] [pending match]
8489: (admin) Liberar Portas Kubernets/SAP => PSCD - 9[23] [pending match]
8490: (admin) Liberar Portas Kubernets/SAP => PSCD - 10[23] [pending match]
8491: (admin) Liberar Portas Kubernets/SAP => PSCD - 11[23] [pending match]
8492: (admin) Liberar Portas Kubernets/SAP => PSCD - 3[23] [pending match]
8493: (admin) Liberar Portas Kubernets/SAP => PSCD - 13[23] [pending match]
8494: (admin) Liberar Portas Kubernets/SAP => PSCD - 16[23] [pending match]
8495: (admin) Liberar Portas Kubernets/SAP => PSCD - 12[23] [pending match]
8496: (admin) Liberar Portas Kubernets/SAP => PSCD - 15[23] [pending match]
8497: (admin) Liberar Portas Kubernets/SAP => PSCD - 14[23] [pending match]
8498: (admin) Liberar Portas Kubernets/SAP => PSCD - 17[23] [pending match]
8499: (admin) Liberar Portas Kubernets/SAP => PSCD - 18[23] [pending match]
8500: (admin) Liberar Portas Kubernets/SAP => PSCD - 19[23] [pending match]
8501: (admin) Liberar Portas Kubernets/SAP => PSCD - 21[23] [pending match]
8502: (admin) Liberar Portas Kubernets/SAP => PSCD - 20[23] [pending match]
8503: (admin) Liberar Portas Kubernets/SAP => PSCD - 22[23] [pending match]
8504: (admin) Liberar Portas Kubernets/SAP => PSCD - 23[23] [pending match]', 'Average', '2025-08-19', '2025-08-19 09:22:37', '2025-08-19 18:47:06'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Executar RDM CHG0073206 - Atualizar Aplicação do PSCD na Horizon', NULL, 'Average', '2025-08-16', '2025-08-19 09:17:53', '2025-08-19 09:18:00'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Mapeamento - Demanda Status por Exame', 'eunião Teams para planejamento para a implementação de RDM em 23/08

Dubia / Daniel / Michael', 'Average', '2025-08-18', '2025-08-18 17:39:17', '2025-08-18 17:48:06'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Code Review  Demanda: 292043 - Criar um relatório baseado no RL2111 porm com o nome RL2112', 'https://dasa.businessmap.io/ctrl_board/155/cards/292043/details/', 'Average', '2025-08-18', '2025-08-18 12:18:25', '2025-08-22 17:20:26'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Fazer code review da demanda 291357', 'https://dasa.businessmap.io/ctrl_board/155/cards/291357/details/', 'Average', '2025-08-15', '2025-08-15 16:38:45', '2025-08-18 11:33:56'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]   - Construir Redirect para o RPS', 'Anexo desenho, mas basicamente precisa redirecionar as request do pscdapi.dasa.com.br para pscdpasoe.dasa.com.br

Nesse momento iremos fazer no ambiente de homologação

De: http://brlspwhems01.dasa.net:8081/wsa/wsa1/wsdl?targetURI=urn:asFaturRpsIF

Para: http://brlsplhpas01.dasa.net:8081/soap/wsdl?targetURI=urn:asFaturRpsIF

| http://brlspwhems01.dasa.net:8081/wsa/wsa1/wsdl?targetURI=urn:asFaturRpsIF | http://brlsplhpas01.dasa.net:8081/soap/wsdl?targetURI=urn:asFaturRpsIF

[Redirect.drawio.pdf](file:///C:/Users/F22209249805/Downloads/Redirect.drawio.pdf)', 'Average', '2025-08-15', '2025-08-13 16:07:43', '2025-08-15 16:37:29'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Abertura de regra de firewall', '- Kubernets
- SAP
- PSCD', 'Average', '2025-08-13', '2025-08-13 12:04:46', '2025-08-13 15:49:09'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Analise Técnica e Viabilidade - Demanda: 294828', 'https://dasa.businessmap.io/ctrl_board/155/cards/294828/details/', 'Average', '2025-08-13', '2025-08-13 11:10:17', '2025-08-13 11:42:31'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Validar Ambiente Horizon MFA - PSCD', 'Validar junto com o Paulo ambiente de testes novo do Horizon, para aplicação do PSCD autenticando via MFA no Horizon.', 'Average', '2025-08-12', '2025-08-12 11:22:39', '2025-08-12 11:34:02'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Abertura de RDM  - Atualização da maquina Gold - 11/08/25', 'Objetivo: Preencher de RDM no Dasa Desk para atualização da maquina Gold para o dia 14/08.

- Abertura Dasa Desk
- Aps a equipe de RDM informar a data alinhar com área de negocio
-

Acompanhar aprovação', 'Average', '2025-08-14', '2025-08-11 17:37:00', '2025-08-22 12:35:58'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Teste lote WS ( Criticas )', 'Apoiar Vania e Andre nos testes da integração :
https://dasa.businessmap.io/ctrl_board/155/cards/291357/details/', 'Average', '2025-08-11', '2025-08-11 11:40:48', '2025-08-11 16:53:04'),
    (@CompanyID, @UserID, @ConcluidoID, '[GMUD] - Implementar RDM', 'Implementar RDM para atualizarmos o ambiente do PSCD no Horizon(Processo de Abertura)
Verificar viabilidade de agenda e abrir a RDM no DasaDesk.', 'Average', '2025-08-11', '2025-08-11 10:53:36', '2025-08-13 11:02:57'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]-Ajuste no Relatórios RL6008 - RL2086 - RL2011', 'RL6008:
Erro: Relatório extrado não respeitou a seleção de status:
Correção: Ajustar o programa para realizar a geração/extração do relatório conforme Filtro de Status.

===========================================================================================

RL2086
Erro:Valor do atendimento não considerou a soma do status por exame no paciente. No relatório consta o valor total do atendimento, conforme as linhas marcadas abaixo:

Correção: Ajustar programa/relatório para realizar a extração considerando a soma do total por exame dos pacientes.

31/07/2025

Observação:

Melhoria:Acrescentar as colunas relacionadas ao Total Paciente e Recalculo" 
Motivo: Recalculo já foi adicionado a Produção no dia 23/07, e Total Paciente facilita a análise do usuário.

===========================================================================================

RL2011

Erro: Opção "Parâmetro" Filtro "Sintético + Analítico", não gera dados/extração ao finalizar, verificar programa.

Correção: Ajustar programa/relatório para que execute a geração de dois relatórios ?Sintético + Analítico?, extraindo os arquivos separadamente no diretório.', 'Average', '2025-07-14', '2025-07-02 19:41:48', '2025-08-11 16:48:29'),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] -Workflow de Cancelamento - Desenvolvimento', 'Objetivo: Elaborar um planejamento detalhado, técnico e funcionais, com o objetivo de otimizar e redesenhar o nosso workflow de cancelamento do Backend.

Esta etapa é crucial para construir uma infraestrutura robusta e automatizada que sustentar um processo de cancelamento mais eficiente, rastreável e em conformidade com nossos requisitos. Nosso objetivo é garantir que a lógica de negócio e as integrações sejam implementadas com precisão, proporcionando maior agilidade e controle.', 'Average', '2025-10-06', NULL, NULL),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Manutenção de Banco de Dados - Novembro', 'Objetivo: Otimização e manutenção proativa de nossas bases do banco, visando garantir a performance, a segurança e a integridade dos nossos sistemas.

Esta iniciativa abrange as seguintes ações cruciais:

- Expurgo de Dados Antigos e Logs:

- Será efetuado o expurgo sistemático de dados legados e logs, reduzindo o volume de informações desnecessárias e otimizando o espaço de armazenamento. Esta medida contribuirá diretamente para a melhoria da velocidade de processamento e a redução de custos com infraestrutura.

- Dump & Load nas Instâncias de Banco de Dados:

- Realizaremos o processo de Dump & Load nas instâncias de banco de dados. Esta técnica é fundamental para reorganizar e otimizar a estrutura física dos dados, eliminando fragmentação e melhorando significativamente o desempenho das consultas e operações.

- Reindexação Mensal das Bases:

- Implementaremos um ciclo mensal de reindexação das bases de dados. Esta prática é vital para manter a eficiência das buscas e a velocidade de acesso às informações. As datas para a reindexação serão negociadas previamente com as áreas de negócio, a fim de minimizar qualquer impacto nas operações e garantir a continuidade dos serviços.

- Sistema responsável por 100% dos processos de faturamento.
- Sistema responsável por 100% do reporte de produção.
- São 15 instâncias de banco de dados.

As bases de dados estão volumosas e inchadas gerando problemas de lentidão e necessidade de aumento da capacidade de processamento e armazenamento de dados.

Estas ações, serão executadas de forma planejada e coordenada junto área de negocio para que não tenha nenhum impacto na produção.

Benefícios:

1-Performance.

2-Disponibilidade.

3-Custo evitado com Infraestrutura', 'Average', NULL, NULL, NULL),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Manutenção de Banco de Dados - Outubro', 'Objetivo: Otimização e manutenção proativa de nossas bases do banco, visando garantir a performance, a segurança e a integridade dos nossos sistemas.

Esta iniciativa abrange as seguintes ações cruciais:

- Expurgo de Dados Antigos e Logs:

- Será efetuado o expurgo sistemático de dados legados e logs, reduzindo o volume de informações desnecessárias e otimizando o espaço de armazenamento. Esta medida contribuirá diretamente para a melhoria da velocidade de processamento e a redução de custos com infraestrutura.

- Dump & Load nas Instâncias de Banco de Dados:

- Realizaremos o processo de Dump & Load nas instâncias de banco de dados. Esta técnica é fundamental para reorganizar e otimizar a estrutura física dos dados, eliminando fragmentação e melhorando significativamente o desempenho das consultas e operações.

- Reindexação Mensal das Bases:

- Implementaremos um ciclo mensal de reindexação das bases de dados. Esta prática é vital para manter a eficiência das buscas e a velocidade de acesso às informações. As datas para a reindexação serão negociadas previamente com as áreas de negócio, a fim de minimizar qualquer impacto nas operações e garantir a continuidade dos serviços.

- Sistema responsável por 100% dos processos de faturamento.
- Sistema responsável por 100% do reporte de produção.
- São 15 instâncias de banco de dados.

As bases de dados estão volumosas e inchadas gerando problemas de lentidão e necessidade de aumento da capacidade de processamento e armazenamento de dados.

Estas ações, serão executadas de forma planejada e coordenada junto área de negocio para que não tenha nenhum impacto na produção.

Benefícios:

1-Performance.

2-Disponibilidade.

3-Custo evitado com Infraestrutura', 'Average', NULL, NULL, NULL),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Manutenção de Banco de Dados - Julho', 'Objetivo: Otimização e manutenção proativa de nossas bases do banco, visando garantir a performance, a segurança e a integridade dos nossos sistemas.

Esta iniciativa abrange as seguintes ações cruciais:

- Expurgo de Dados Antigos e Logs:

- Será efetuado o expurgo sistemático de dados legados e logs, reduzindo o volume de informações desnecessárias e otimizando o espaço de armazenamento. Esta medida contribuirá diretamente para a melhoria da velocidade de processamento e a redução de custos com infraestrutura.

- Dump & Load nas Instâncias de Banco de Dados:

- Realizaremos o processo de Dump & Load nas instâncias de banco de dados. Esta técnica é fundamental para reorganizar e otimizar a estrutura física dos dados, eliminando fragmentação e melhorando significativamente o desempenho das consultas e operações.

- Reindexação Mensal das Bases:

- Implementaremos um ciclo mensal de reindexação das bases de dados. Esta prática é vital para manter a eficiência das buscas e a velocidade de acesso às informações. As datas para a reindexação serão negociadas previamente com as áreas de negócio, a fim de minimizar qualquer impacto nas operações e garantir a continuidade dos serviços.

- Sistema responsável por 100% dos processos de faturamento.
- Sistema responsável por 100% do reporte de produção.
- São 15 instâncias de banco de dados.

As bases de dados estão volumosas e inchadas gerando problemas de lentidão e necessidade de aumento da capacidade de processamento e armazenamento de dados.

Estas ações, serão executadas de forma planejada e coordenada junto área de negocio para que não tenha nenhum impacto na produção.

Benefícios:

1-Performance.

2-Disponibilidade.

3-Custo evitado com Infraestrutura', 'Average', '2025-07-28', '2025-07-01 09:53:39', '2025-07-07 09:32:49'),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] -  Modernização do PSCD - fase 2 - TROCA DO END POINT', 'Objetivo: Definições entre as áreas de Gliese, Paperless e SAP, para troca de endereço do End Point no dia do GO Live, garantindo que a mudança suporte os objetivos estratégicos de modernização do PSCD, com métricas claras para avaliar o sucesso e identificação de riscos e dependências.', 'Average', '2025-11-03', '2025-09-24 09:55:37', NULL),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Planejamento - Workflow de Cancelamento', 'Objetivo: Elaborar um planejamento detalhado, técnico e funcionais, com o objetivo de otimizar e redesenhar o nosso workflow de cancelamento do Backend. Esta fase inicial é essencial para garantir que a futura solução seja robusta, eficiente e alinhada às necessidades de negócio e requisitos tecnológicos.', 'Average', '2025-11-03', '2025-10-08 16:20:55', '2025-10-29 18:15:55'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Ajustar o relatório do Cálculo da Provisão Mensal para controle de Status no exame', 'Objetivo:
Hoje o controle de valores da provisão é feito com base no cod. status do paciente(atendimento), conforme demanda solicitada pela equipe de negócios vamos ajustar todos os programas relacionados ao cálculo da provisão mensal para adequar ao solicitado, conforme detalhamento técnico.

1 -Cálculo da Provisão, ESFT060PR;

2 - Período x Divisão Provisão, esft002pr.w;

3 - Troca de Status Provisão, ESFT003PR;

4 - Monitor Provisão, ESFT004PR;

5 - Pacientes Provisão, ESFT007PR;

6 - Provisão Inicial, ESFT008PR;

7 - Provisão Histórico, ESFT009PR; Sintético

8 - Provisão Histórico Analítica, ESFT011PR;

Programas para apoio:
**Alguns programas para apoiar consultas ou cadastros:

Consulta de paciente:

Cadastro de Status:

Tabelas a Serem ajustadas :

As tabelas abaixo são as principais identificadas e utilizadas para armazenar os dados de cálculo da provisão mensal.

## Provisao_Historico_Periodo

esft006prrp.p

esft006pr.w

esft112pr.p

esft009prrp.p

esft008prrp.p

esft003pr.w

esft006prx.w

esft009pr.w

esft011pr.w

## imp-LogProvisao (Usada como tabela transitoria)

esft006prrp.p

esft112pr.p

esft008prrp.p

esft003pr.w

esft003pr.i

esft007pr.w

## Provisao_Foto_Periodo

** Ao fazer os ajustes nos programas pode ser que seja avaliado a necessidade de ajustar mais tabelas, seguir mesmo conceito das apresentadas aqui;
** Gerar DF DIF e solicitar o Jonivaldo (DBA) a aplicação em ambiente de homologação;
** Ao desenvolver e alterar as funcionalidades nos programas verificar a necessidade de criar novos índices nas tabelas.

- Como ajustar o Índice:

Criar um novo índice primário onde o novo índice será igual ao já existente porém adicionado o campo "Cod-Status"

**Validar se melhor renomear a tabela e criar uma nova para ambiente de HML;
ex.:

/* Drop do índice existente ix-codigo */

DROP INDEX "ix-codigo" ON "Provisao_Historico_Periodo".

/* Criação do novo índice ix-primario */

ADD INDEX "ix-primario" ON "Provisao_Historico_Periodo"

AREA "i-provisao"

UNIQUE

PRIMARY

INDEX-FIELD "Periodo" ASCENDING

INDEX-FIELD "divisao" ASCENDING

INDEX-FIELD "cod-paciente" ASCENDING

INDEX-FIELD "SeqProvHist" ASCENDING

INDEX-FIELD "Cod-Status" ASCENDING.

- Adicionar Campo novo para armazenar as seq dos exames agrupados :
Criar um novo campo tipo char format x(2000) para armazenar as sequencias dos exames, como os status serão agrupadas;
**armazenar os valores separados por vírgula e sem espaços, ex. "1,3,6,8,10,99", isso serve para recuperarmos caso tenha uma necessidade futura.
ex.:

ADD FIELD "seqExames" OF "Provisao_Historico_Periodo" AS character

FORMAT "x(2000)"

INITIAL ""

POSITION 26

MAX-WIDTH 26

ORDER 250

Fluxo Básico, do processo do cálculo da provisão:

Programas envolvidos no Cálculo da Provisão Mensal:

ESFT111 - Relatório para analisar Convênios\Atendimentos

ESFT001PR - Parâmetros da Provisão

ESFT002PR- Período x Divisão Provisão

ESFT003PR - Troca de Status Provisão

ESFT004PR - Monitor Provisao

ESFT006PR - Processamento de Provisão - CALCULO

ESFT007PR - Pacientes - Provisão

ESFT008PR - Provisão Inicial

ESFT009PR - Provisão Histórico

ESFT011PR - Provisão Histórica e Analítica

1 - Calculo da Provisão, ESFT060PR:

Aps ajustar as tabelas verificar:

1.1 - esft006pr.w, funcionalidade da tela:

- Corrigir o comportamento tela pois contém erros ao selecionar os campos e depois tentar desmarcar onde o enable/disable dos campos ocorre de forma errada;
- Ajuste para não colocar o processo selecionado como finalizado ao pressionar o executar(verificar se foi feito desta forma para evitar duplicidade na execução), se não for possível manter da forma como está.

1.2 - esft006prrp.p, ajuste do processamento dos dados:

- Ajustar o formato de como é calculado e armazenado os dados de provisão conforme a informação já mencionada antes, onde todo processo atual é feito considerando o status do paciente(atendimento) vamos alterar a regra para considerar o status dos exames, como o fator o status do exame é considerado como acumulador, deve-se somar todos os valores referentes ao mesmo status de exame e para cada status salvar os dados na tabelas anteriormente citadas para isto vamos nos atentar nos seguintes pontos, todas as alterações feitas devem ser bem elaboradas e com muito critério visando um melhor desempenho e um menor consumo de recursos, tendo em vista o alto volume de dados processado;

1.2.1 - esft006prrp.p, Novo Período:

1.2.2 - esft006prrp.p, Fluxo Carregar:

1.2.3 - esft006prrp.p, Fluxo Finalizar:

1.2.4 - esft006prrp.p, Fluxo Liberar:

1.2.5 - esft006prrp.p, Fluxo Integrar SAP:

1.3 - esft006prrp.p, pontos a serem avaliados:

- Procure armazenar os dados de exame em uma temp-table para poder reutilizar ela depois, copiar para ela somente os campos utilizados, desta forma não teremos que consultar novamente o banco para buscar as mesma informações quando necessário, ao criar ele faça um testes quando antes de guardar os valores da temp-table fazer um empty na temp-table para limpar todos os registros existentes, pois desta forma mantemos um número menor de registros alocado na memória :

- Modelo de como pode ser feito o ajuste por status do exame
**Não tomar como valido o exemplo, só demonstrar o ajuste:
-

2 - Período x Divisão Provisão, esft002pr.w:

- Ajustar layout da tela aumentado o tamanho para que todos os dados do browser seja apresentados na tela:

- A origem dos dados é a tabela Provisao_Divisao_Periodo, que a princípio não teria ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo :

-

3 - Troca de Status Provisão, ESFT003PR:

- Validar se vai continua fazer o troca de status por ele ou se vai usar o pr2035(NOVO), caso manter ele deve-se fazer uma nova análise do seu comportamento.

4 - Monitor Provisão, ESFT004PR:

- Ajustar o layout da tela para caber todos dos dados do browser:
-

- A origem dos dados é a tabela Provisao_Divisao_Periodo, a principio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo :
-

5 - Pacientes Provisão, ESFT007PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo

6 - Provisão Inicial, ESFT008PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo

7 - Provisão Histórico, ESFT09PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo

8 - Provisão Histórico Analítica, ESFT011PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo', 'Average', '2025-05-05', '2025-06-24 09:50:05', '2025-06-24 09:50:36'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Clculo da Provisão Mensal para Status por exames', 'Objetivo: Fazer uma analise detalhada do processo de Cálculo de provisão para adaptação do processo de status no exame.

Objetivo:
Hoje o controle de valores da provisão é feito com base no cod. status do paciente(atendimento), conforme demanda solicitada pela equipe de negócios vamos ajustar os todos os programas relacionados ao cálculo da provisão mensal para adequar ao solicitado.

Programas para apoio:
**Alguns programas para apoiar consultas ou cadastros:

Consulta de paciente:

Cadastro de Status:

Tabelas a Serem ajustadas :

As tabelas abaixo são as principais identificadas e utilizadas para armazenar os dados de cálculo da provisão mensal.

## Provisao_Historico_Periodo

esft006prrp.p

esft006pr.w

esft112pr.p

esft009prrp.p

esft008prrp.p

esft003pr.w

esft006prx.w

esft009pr.w

esft011pr.w

## imp-LogProvisao (Usada como tabela transitoria)

esft006prrp.p

esft112pr.p

esft008prrp.p

esft003pr.w

esft003pr.i

esft007pr.w

## Provisao_Foto_Periodo

** Ao fazer os ajustes nos programas pode ser que seja avaliado a necessidade de ajustar mais tabelas, seguir mesmo conceito das apresentadas aqui;
** Gerar DF DIF e solicitar o Jonivaldo (DBA) a aplicação em ambiente de homologação;
** Ao desenvolver e alterar as funcionalidades nos programas verificar a necessidade de criar novos índices nas tabelas.

- Como ajustar o Índice:

Criar um novo índice primário onde o novo índice será igual ao já existente porém adicionado o campo "Cod-Status"

**Validar se melhor renomear a tabela e criar uma nova para ambiente de HML;
ex.:

/* Drop do índice existente ix-codigo */

DROP INDEX "ix-codigo" ON "Provisao_Historico_Periodo".

/* Criação do novo índice ix-primario */

ADD INDEX "ix-primario" ON "Provisao_Historico_Periodo"

AREA "i-provisao"

UNIQUE

PRIMARY

INDEX-FIELD "Periodo" ASCENDING

INDEX-FIELD "divisao" ASCENDING

INDEX-FIELD "cod-paciente" ASCENDING

INDEX-FIELD "SeqProvHist" ASCENDING

INDEX-FIELD "Cod-Status" ASCENDING.

- Adicionar Campo novo para armazenar as seq dos exames agrupados :
Criar um novo campo tipo char format x(2000) para armazenar as sequencias dos exames, como os status serão agrupadas;
**armazenar os valores separados por vírgula e sem espaços, ex. "1,3,6,8,10,99", isso serve para recuperarmos caso tenha uma necessidade futura.
ex.:

ADD FIELD "seqExames" OF "Provisao_Historico_Periodo" AS character

FORMAT "x(2000)"

INITIAL ""

POSITION 26

MAX-WIDTH 26

ORDER 250

Fluxo Básico, do processo do cálculo da provisão:

Programas envolvidos no Cálculo da Provisão Mensal:

ESFT111 - Relatório para analisar Convênios\Atendimentos

ESFT001PR - Parâmetros da Provisão

ESFT002PR- Período x Divisão Provisão

ESFT003PR - Troca de Status Provisão

ESFT004PR - Monitor Provisao

ESFT006PR - Processamento de Provisão - CALCULO

ESFT007PR - Pacientes - Provisão

ESFT008PR - Provisão Inicial

ESFT009PR - Provisão Histórico

ESFT011PR - Provisão Histórica e Analítica

1 - Calculo da Provisão, ESFT060PR:

Aps ajustar as tabelas verificar:

1.1 - esft006pr.w, funcionalidade da tela:

- Corrigir o comportamento tela pois contém erros ao selecionar os campos e depois tentar desmarcar onde o enable/disable dos campos ocorre de forma errada;
- Ajuste para não colocar o processo selecionado como finalizado ao pressionar o executar(verificar se foi feito desta forma para evitar duplicidade na execução), se não for possível manter da forma como está.

1.2 - esft006prrp.p, ajuste do processamento dos dados:

- Ajustar o formato de como é calculado e armazenado os dados de provisão conforme a informação já mencionada antes, onde todo processo atual é feito considerando o status do paciente(atendimento) vamos alterar a regra para considerar o status dos exames, como o fator o status do exame é considerado como acumulador, deve-se somar todos os valores referentes ao mesmo status de exame e para cada status salvar os dados na tabelas anteriormente citadas para isto vamos nos atentar nos seguintes pontos, todas as alterações feitas devem ser bem elaboradas e com muito critério visando um melhor desempenho e um menor consumo de recursos, tendo em vista o alto volume de dados processado;

1.2.1 - esft006prrp.p, Novo Período:

1.2.2 - esft006prrp.p, Fluxo Carregar:

1.2.3 - esft006prrp.p, Fluxo Finalizar:

1.2.4 - esft006prrp.p, Fluxo Liberar:

1.2.5 - esft006prrp.p, Fluxo Integrar SAP:

1.3 - esft006prrp.p, pontos a serem avaliados:

- Procure armazenar os dados de exame em uma temp-table para poder reutilizar ela depois, copiar para ela somente os campos utilizados, desta forma não teremos que consultar novamente o banco para buscar as mesma informações quando necessário, ao criar ele faça um testes quando antes de guardar os valores da temp-table fazer um empty na temp-table para limpar todos os registros existentes, pois desta forma mantemos um número menor de registros alocado na memória :

- Modelo de como pode ser feito o ajuste por status do exame
**Não tomar como valido o exemplo, só demonstrar o ajuste:
-

2 - Período x Divisão Provisão, esft002pr.w:

- Ajustar layout da tela aumentado o tamanho para que todos os dados do browser seja apresentados na tela:

- A origem dos dados é a tabela Provisao_Divisao_Periodo, que a princípio não teria ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo :

-

3 - Troca de Status Provisão, ESFT003PR:

- Validar se vai continua fazer o troca de status por ele ou se vai usar o pr2035(NOVO), caso manter ele deve-se fazer uma nova análise do seu comportamento.

4 - Monitor Provisão, ESFT004PR:

- Ajustar o layout da tela para caber todos dos dados do browser:
-

- A origem dos dados é a tabela Provisao_Divisao_Periodo, a principio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo :
-

5 - Pacientes Provisão, ESFT007PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo

6 - Provisão Inicial, ESFT008PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo

7 - Provisão Histórico, ESFT09PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo

8 - Provisão Histórico Analítica, ESFT011PR:
- A princípio sem ajustes na Lógica, mas deve-se reavaliar devido ao comportamento do sistema depois do ajuste dos calculo', 'Average', '2025-05-19', '2025-04-08 15:42:25', '2025-07-21 15:54:53'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Criar Relatório Baseado no ESFT111 adaptado as funcionalidade de controle de Status por exame ( RL2111)', 'Objetivo:Criar um relatório RL2111, clonar do relatório ESFT111, adicionar as tratativas necessárias para atender o controlo de status por exame.', 'Average', '2025-04-21', '2025-04-08 15:55:06', '2025-04-24 20:53:43'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar os programa de Carga ESPR035 de status para nova regra de controle de status no exame', 'Objetivo : ajustar seguintes pontos

1-Aqui gerou vários log sendo que foi feita apenas uma alteração de status

e esta errado esta para 20001, mudei para 530

2-Quando e provisão esta se comportado como controla status do paciente , não esta cravando 20001', 'Average', '2025-03-24', '2025-03-20 09:40:21', '2025-03-25 10:03:15'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Criar relatório RL2111 para controlar Status por Exame', 'Objetivo: Criar um relatório RL2111, clonar do relatório ESFT111, adicionar as tratativas necessárias para atender o controlo de status por exame.', 'Average', '2025-03-24', '2025-03-19 16:06:19', '2025-04-08 15:18:45'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customização do  Status do exame Cancelado ( cancelamento do Lote )', 'Objetivo: Quando houver um cancelamento do lote ,os exames que estiver no lote deve voltar para o status anterior conforme o status de parcial adicionado .

| status exame
| Status | <Voltar
| 530 | 5530
| 531 | 5531
| 532 | 5532
| 533 | 5533
| 534 | 5534
| 535 | 5535
| 536 | 5536
| 537 | 5537
| 538 | 5538
| 539 | 5539

Observação : O status do paciente não muda permanece 20001.

como exemplo abaixo:', 'Average', '2025-03-24', '2025-03-11 17:47:05', '2025-03-24 12:32:01'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar os programa de Carga ESPR035 de status para nova regra de controle de status no exame', 'Objetivo: Adaptar os programas de carga de status existentes para integrar a nova regra de controle de status no processo de exame. hoje e feito somente a carga a nível de paciente.

? ESPR035 - Alteração de Status

regra 1:
verificar se status para gera xml:

regra 2:
verificar se plano do paciente controla por exame

regra 3:
se regra 2 = sim e regra 1 = sim
então troca status do paciente para 20001

regra 4:
exames(não pode estar faturado nr-pedcli <> "") = status_para(ignora status atual)', 'Average', '2025-03-24', '2025-03-11 14:34:57', '2025-03-25 10:03:14'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar o processo de refazer os lotes conforme os status no exame', 'Objetivo: Sempre que ocorrer o retorno de consulta de Status da operadora e voltar com critica o lote precisa ser refeito a nível de exames sem as devidas criticas mencionadas pela operadora.', 'Average', '2025-03-10', '2025-03-06 14:01:48', '2025-03-24 12:24:21'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Customizar a transição do status 45 para 51 na troca de status por exame', 'Objetivo: Dependendo do retorno da operadora automatizar a troca de status de exame de 45 para 51 para que o lote siga o fluxo de concluído.

REFINAMENTO TÉCNICO:

Foi possível avaliar 2 pontos onde é feito a alteração de Status, espr282b10.p e espr280d.p, conforme os prints acima, neste pontos deve ver incluída uma regra para altera os status de exame, porem temos que definir:

- Vai ser tratado o refaz lote ?(espr280d.p)

** A troca de status do exame deve respeitar, se o convênio esta flegado o parâmetro para controlar o status, se não manter regra atual :', 'Average', '2025-02-24', '2025-02-18 14:44:11', '2025-03-10 09:46:36'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar os retornos das operadoras para controlar o status no exame', 'Objetivo: Para cada tipo de exame controlar o retorno do status da operadora, afim de classificar os exames criticados pela operadora e encaminhar para uma fila de tratativas para ser corrigidos e reenviados.

-

Customizar os retornos das operadoras para controlar o status no exame ? Retorno Envio e Retorno das Consulta Status Protocolo.

REFINAMENTO TÉCNICO:

Xml de retorno da Orizon, exemplo:

Requisitos :
- Ter uma tabela que eu aloco o exame com erro;
- #A tabela deve ter os dados de campos chave de paciente, exame;
- #status : status do registro(ex. 10 - inserido, 20 - reprocessado, 30 - finalizado)
- #data_hora_gravacao : dados de data e hora de gravação do reg. na tabela;
- data_hora_status : data e hora da ultima alteração de status;
- erro: Gravar msg de erro;
** verificar caso tenha que inserir mais dados na tabela para atender a demanda;

1 - Na leitura do XMl de retorno das criticas:
- Verificar o Convênio do Paciente (escd021);
- Aba faturamento campo campo controla status exame, se flegado(True/SIM);

- Se flegado então:
- Identificar os exames com erro(se possível);
- Possíveis erros a identificar: Guia ou Guia e Procedimento ou NADA(Cenário atual, manter como esta hoje sem alterar)
- GUIA: todos exames devem ser marcados com status de erro;
- Guia e Procedimento: Se possível identificar outro parâmetro que possibilite chegar no exame, marcar somente estes com status de erro;
- NADA: Se não identificar qual guia esta com erro, então não alterar status do exame;
- Todos registros onde houve a alteração de status, deve gravar um registro na tabela criada acima, porem se o registro existir deve atualizar o status para o status inicial definido(ex. 10 - Inserido)

**Confirmar o cod. de status de erro do exame a ser gravado em caso de erros;
**Se marcado param. refazer lote da operadora escd021 aba faturamento, pode haver erro, avaliar possível impacto, pois o numero da guia TISS pode gerar duplicidade;', 'Average', '2025-02-10', '2025-01-29 09:24:22', '2025-02-25 09:50:09'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar a entrada das bases para gerar Pedidos controlando status no exame ? ESPR280', 'Objetivo: Gerar base na ESPR280 onde traga em nível de exame de um mesmo atendimento, para geração de lotes conforme retorno das operadoras.

Montagem de lote XML e Postagem para operadoras

-

Customizar a entrada das bases para gerar Pedidos controlando status no exame ? ESPR280.

REFINAMENTO TÉCNICO:

Ao gerar o Pedido
1 - Depois de importar a lista de pedidos, verificar (espr280):

2 - Ao ler a Lista verifica o Paciente(esft007)
- Verificar o Convênio do Paciente (escd021);
- Aba faturamento campo campo controla status exame, se flegado(True/SIM);
- Se flegado deve verificar a lista de exames do paciente (esft007 / aba exames);
- No status exame (espr001), verifica se o fleg ?Controla Exame? esta flegado(True/SIM);
- Se flegado então na importação descartar o exame na geração do pedido;
** O valor do exame descartado não entra no calculo do pedido;

** Os campos a serem verificados para o tratamento do status do exame estão previstos nas demandas:

| https://dasa.businessmap.io/ctrl_board/155/cards/210518/details/ | [PSCD] Customizar o Cadastro de Parâmetros de Convênio
| https://dasa.businessmap.io/ctrl_board/155/cards/210523/details/ | [PSCD] Customizar o Cadastro Status Atendimento', 'Average', '2025-02-10', '2025-01-29 09:24:19', '2025-02-25 09:49:40'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Customizar o Cadastro Status Atendimento', 'Objetivo: Indicar no atendimento se a operadora requer o controle em nível de exame dentro de um mesmo atendimento.

- Adicionar flag para identificar se o status pode controlar o exame.

REFINAMENTO TÉCNICO:

1 - Criar novo campo no banco de dados:
Nome do Banco...: daprovisao
Nome da Tabela...: Status_Atd
Nome do Campo.: controla_exame
Tipo de Dados......: LOGICAL
Formato.................: Sim/Não

2 - Na tela do ESPR001(espr001-v01.w) adicionar um novo field tipo logico para gravar o valor no novo campo Status_Atd .controla-exame, atentar para manter o alinhamento de tela no posicionamento do campo, seguindo os padrões dos campos já existentes, assim como ele deve respeitar as mesmas regras dos campos existentes ao incluir/modificar os registros.', 'Average', '2025-01-27', '2025-01-14 09:46:38', '2025-01-28 10:03:46'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] -  Customizar o Cadastro de Parâmetros de Convênio', 'Objetivo: Possibilitar a parametrização do controle dos exames por plano.

- Adicionar flag para identificar se o plano deve controlar o status no exame.
-

REFINAMENTO TÉCNICO:

- Adicionar na tabela DA-PARAM-CONV um campo do tipo logico TOOGLE- BOX
- Adicionar um FLAG na tela no ESCD021 aba faturamento conforme imagem acima
- Campo padrão deve ser NÃO OU FALSE', 'Average', '2025-01-27', '2025-01-14 09:46:30', '2025-01-28 10:03:42'),
    (@CompanyID, @UserID, @BacklogID, 'SCRM - 2025 PI 1 S1', 'Objetivo:
- Customização dos cadastros e ajuste de banco de dados inserindo os campos novos;', 'Average', '2025-01-27', '2025-01-14 09:45:14', '2025-01-29 09:24:05'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Corrigir Diretório de arquivos temporários de transação', 'Problema

- Programa que geram arquivos temporários gerando dados no repositório de relatórios.
- Deixando uma área reservada para relatórios poluídos com dados temporários de transações.

Correção

- Identificar os programas que estão gerando dados nesse repositório e modificar para gravar no spool de transações => /integracao/spool/transacoes', 'Average', '2024-12-13', '2024-12-10 15:17:04', '2024-12-16 22:03:48'),
    (@CompanyID, @UserID, @ConcluidoID, 'AMIL- Erro na resposta do Envio e Consulta dos Serviços de WS -  Integrações', 'Problema: O Servidor da Amil esta retornando o erro (504 Gateway Timeout), no envio do lote ou consulta do protocolo, erro intermitente esta sendo tratado com equipe da Amil, vide em anexo.

Ação: Mudança Recente

- Amil disponibilizou novo endereço de comunicação para as versões 4.01.00 para Lotes Guias e Consulta Status Protocolo.
- Problema

- Amil devolvendo muitos erros de 504-Timeout nas requisições de lotes guias \ Consulta status protocolo.
- Lentidão nas Requisições.

- Impacto

- Ficou uma grande massa represada do lado da Dasa para ser processado com janela reduzida.

- Ações Implementadas:

- Amil:

- Tem atuado com diversas ações para solucionar a questão do erro 504-timeout. Desde ontem os erros reduziram significativamente.
- Aumento da capacidade de processamento. Desde ontem notamos uma boa melhora na performance nas integrações, porém continua mantendo uma taxa de 1 a 2 minutos por requisição.
- Amil ajustou a janela para postagens que era antes de 12 horas e a partir de hoje está aberta por 24 horas até amanhã 06/12/2024. Essa ação é imprescindível para reprocessarmos a massa que ficou represada.

- Dasa:

- Plantão para priorizar as ações de postagens \ monitoramento.
- Abertura de novas filas para as integrações para processar toda massa represada.

Observações:

- Na sala de crise o time Dasa solicitou que as alterações que impactaram positivamente as integrações sejam mantidas pelo Amil para não voltarmos a fase inicial de problemas.
- Nesse momento os processos estão sendo executados com sucesso, porém ainda temos uma grande massa para processar.', 'Average', NULL, '2024-12-06 00:27:36', '2024-12-09 09:56:46'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]-ESPR130R2 Relatório Atendimentos Faturamento Digital', 'Problema: Erro: programa ESPR130R2 - ESPR130R2RP, relatório de imagem.

O programa não fecha a tela do Pedido de execução, gerando MUITOS logs de RPW e impactando com filas de pedidos para execução.

Pedido fica com a situação 1-Não executado, porem está em execução.

A tela do pedido de execução, fica disponível para fechar, quando a execução do pedido é concluída!

Nesse cenário, o programa ficou 40 minutos em execução e gerando logs de RPW .

Solução: Após estudo de Spike, precisa acrescentar campos no TT-PARAM e o Programa carregar varias tabelas temporárias no destino ( Linux).

Resultado: Ganho financeiro na operação.

============================================================
Acompanhamento de Resultados (DASA Oficial)
============================================================

| Resultado Desejado: | Ao pedir que seja gerado o RPW o processamento continue com mais agilidade e não seja gerados logs de RPW.
| Resultado Alcançado: |
| Comentário sobre os resultados alcanados: |', 'Average', '2025-02-10', '2025-01-20 09:58:07', '2025-02-11 09:55:54'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] Atualização do SO da Maquina BRLSPWPEMS02', 'Demanda:

Ação:

============================================================
Acompanhamento de Resultados (DASA Oficial)
============================================================

| Resultado Desejado: |
| Resultado Alcançado: |
| Comentário sobre os resultados alcanados: |

============================================================
Descrição da História (DASA Oficial)
============================================================

Estória de Usuário

| Como: |
| Quero: |
| Para: |
| Desenho:
* Se houver |

Escopo da Alteração

| Sistema: | (nome)
| Micro Serviço: | (nome)

Detalhes

| Dependências: |
| Riscos: |
| Exemplos: |
| Monitoramento: |
| Volumetria: |
| Fora do escopo: |
| Outros detalhes:
* Se houver |

Critério de Aceite 01

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
| Telas:
* Se houver |

Critério de Aceite 02

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
| Telas:
* Se houver |

Critério de Aceite XX

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
| Telas:
* Se houver |

============================================================
Descrição
============================================================

Por que (problema identificado):

Objetivo:

Como/ Recursos:

Critérios de aceite:', 'Average', NULL, '2024-12-03 15:35:13', '2024-12-13 09:51:40'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD]- Saneamento Parte 3-Solicitação de Ajuste Tela Cadastro ESPR058 e ESPR064', 'Demanda: Solicitação é para criar uma lista suspensa em caixa alta para os campos: Família do Produto / Modalidade / Especialidade Programa ESPR058

Em conversa com o Lino, ele recomendou o ajuste também no ESPR064 para manter o padrão de caixa alta.

Refinamento Técnico:

- Criar Combo no cadastro espr062 para os 3 campos mencionados na demanda.
- Permitir que o valor informado no Cadastro seja apenas o informado previamente no Combo.
- ESPR058 - Cadastro de Itens.
- ESPR064 - Cadastro de Centro.
- Permitir que os dados cadastros estejam previamente informados nos combos abaixo.

Família do Produto - COMBO 138 Modalidade - COMBO 139 Especialidade - COMBO 140

============================================================
Acompanhamento de Resultados (DASA Oficial)
============================================================

| Resultado Desejado: |
| Resultado Alcançado: |
| Comentário sobre os resultados alcanados: |

============================================================
Descrição da História (DASA Oficial)
============================================================

Estória de Usuário

| Como: | Cadastro
| Quero: | Ajustar alguns campos nos Cadastros
| Para: | Evitar Duplicidade e Inconsistência
|

Desenho:

- Se houver
| N/A

Escopo da Alteração

| Sistema: | PSCD
| Micro Serviço: | Cadastro

Detalhes

| Dependências: | N/A
| Riscos: | N/A
| Exemplos: | N/A
| Monitoramento: | N/A
| Volumetria: | N/A
| Fora do escopo: | N/A
|

Outros detalhes:

- Se houver
| N/A
| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite 02

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite XX

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

============================================================
Descrição
============================================================

Por que (problema identificado):

Objetivo:

Como/ Recursos:

Critérios de aceite:', 'Average', NULL, '2024-12-03 15:35:05', '2024-12-19 09:48:53'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Piloto WS 4.01.00 - CAIXA', 'Demanda:

Ação:

REFINAMENTO TÉCNICO

Acompanhar a virada em produção da Nova Versão Tiss 4.01.00 para CAIXA.
Acompanhar o Envio Lote Guias
Acompanhar a Consulta Status Protocolo

============================================================
Acompanhamento de Resultados (DASA Oficial)
============================================================

| Resultado Desejado: |
| Resultado Alcançado: |
| Comentário sobre os resultados alcanados: |

============================================================
Descrição da História (DASA Oficial)
============================================================

Estória de Usuário

| Como: | Recebíveis
| Quero: | Integrar com a CAIXA Processos TISS
| Para: | Automatizar os Processos de Postagens
|

Desenho:

- Se houver
|

Escopo da Alteração

| Sistema: | PSCD
| Micro Serviço: | ESPR280

Detalhes

| Dependências: |
| Riscos: |
| Exemplos: |
| Monitoramento: |
| Volumetria: |
| Fora do escopo: |
| 
Outros detalhes:

- Se houver
|

Critério de Aceite 01

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite 02

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite XX

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Estória de Usuário

| Como: |
| Quero: |
| Para: |
|

Desenho:

- Se houver
|

Escopo da Alteração

| Sistema: | (nome)
| Micro Serviço: | (nome)

Detalhes

| Dependências: |
| Riscos: |
| Exemplos: |
| Monitoramento: |
| Volumetria: |
| Fora do escopo: |
| 
Outros detalhes:

- Se houver
|

Critério de Aceite 01

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite 02

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite XX

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

============================================================
Descrição
============================================================

Por que (problema identificado):

Objetivo:

Como/ Recursos:

Critérios de aceite:', 'Average', NULL, '2024-12-03 15:34:56', '2024-12-16 22:03:43'),
    (@CompanyID, @UserID, @BacklogID, 'Amil - Erro na resposta do Envio e Consulta dos serviços de WS', 'Problema: O servidor da Amil esta retornando o erro (504 Gateway Timeout) , no envio do lote ou consulta do protocolo, erro intermitente esta sendo tratado com equipe de Amil, vide em anexo da demanda.

Ação: Atividade esta sendo conduzido pela equipe Dasa e Amil.

Produção de massa de teste para enviar dados para ser analisado pelo equipe da AMIL, Juliano esta analisandos os Logs dos teste enviando para Amil.', 'Average', NULL, '2024-11-29 11:57:39', '2024-12-03 11:06:02'),
    (@CompanyID, @UserID, @ConcluidoID, '[PSCD] - Faturamento Caption ALICE RDI e AC com divergencia de centavos - RITM0619787', 'Demanda:

============================================================
Environment
============================================================

ERRO

O cálculo do Captation do convênio ALICE (Aliceq-Duquesa) está mais ou menos uns 4 meses dando diferença de 0,01 ou 0,02 centavos, geralmente é no RDI, mas neste fechamento de Julho/2024 apareceu a diferença de 0,01 para AC e 0,01 para RDI.

Exemplo - Faturamento de RDI - ALICE CAP RDI

Valor de Faturamento gerado 435.314,01

Valor de Faturamento acordado 435.314,00

Por gentileza, peço-lhes que verifiquem as melhorias que podem ser realizadas.

Solução

Analisar as rotinas que ajustam valor dos exames para ser faturado conforme valor acordado.

Programa - espr070rpw2.p .

Os ajustes de valor nos exames e o valor total geral deve ser conforme valor acordado no Caption

Ganhos

Eliminar devolução de faturamento devido divergência com valor acordado.

Eliminar retrabalho, cancelar todos os faturamento e gerar faturamento manual.

============================================================
Acompanhamento de Resultados (DASA Oficial)
============================================================

| Resultado Desejado: |
| Resultado Alcançado: |
| Comentário sobre os resultados alcanados: |

============================================================
Descrição da História (DASA Oficial)
============================================================

Estória de Usuário

| Como: | Recebíveis
| Quero: | Ajuste de diferença de centavos no Caption do convênio Alice
| Para: | Geração correta dos valores do Faturamento.
|

Desenho:

- Se houver
| N/A

Escopo da Alteração

| Sistema: | PSCD
| Micro Serviço: | PSCD

Detalhes

| Dependências: | N/A
| Riscos: | N/A
| Exemplos: | Exemplo - Faturamento de RDI - ALICE CAP RDI
Valor de Faturamento gerado 435.314,01
Valor de Faturamento acordado 435.314,00
| Monitoramento: | N/A
| Volumetria: | N/A
| Fora do escopo: | N/A
|

Outros detalhes:

- Se houver
| N/A

Critério de Aceite 01

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite 02

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite XX

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

============================================================
Descrição
============================================================

Por que (problema identificado):

Objetivo:

Como/ Recursos:

Critérios de aceite:', 'Average', NULL, '2024-09-17 16:10:12', '2024-12-06 09:47:19'),
    (@CompanyID, @UserID, @BacklogID, '[PSCD] - Configurar WS 4.01.00 - CAIXA', 'Ação:

Demanda:

Documentação enviado da CAIXA está no anexo

-

Refinamento Técnico

Configurar URL no Cadastro ESPR096 Configurar Script de Envio e Consulta no SVPODRPW01 Fazer Testes de Envio e Consulta Usar a Versão mais recente de Integração. ESPR097 - Solicitar Usuários e Senha.

-

PROGRAMAS

esp\espr282d.p esp\espr282d3.p

-

URL

LOTE GUIAS PRD - https://saude.caixa.gov.br/WebApp/NonAuthenticatedServiceHost/tissLoteGuiasV4_01_00.svc CONSULTA STATUS PROTOCOLO PRD - https://saude.caixa.gov.br/WebApp/NonAuthenticatedServiceHost/tissSolicitacaoStatusProtocoloV4_01_00.svc ANS http://www.ans.gov.br/padroes/tiss/schemas/tissLoteGuiasV4_01_00.wsdl http://www.ans.gov.br/padroes/tiss/schemas/tissSolicitacaoStatusProtocoloV4_01_00.wsdl

-

SCRIPT

PRODUÇÃO T:\sisPscd\App\scripts\svpodrpw\prd\batch\Caixa\EnvioXmlTissCham.bat T:\sisPscd\App\scripts\svpodrpw\prd\batch\Caixa\EnvioXmlTiss.bat T:\sisPscd\App\scripts\svpodrpw\prd\batch\Caixa\ConsultaXmlTissCham.bat T:\sisPscd\App\scripts\svpodrpw\prd\batch\Caixa\ConsultaXmlTiss.bat HOMOLOGAÇÃO - GENÉRICO - AJUSTAR ADICIONAR A LINHA DA RESPECTIVA URL T:\sisPscd\App\scripts\svpodrpw\hml\batch\EnvioLote\EnvioXmlTissCham.bat T:\sisPscd\App\scripts\svpodrpw\hml\batch\EnvioLote\EnvioXmlTiss.bat T:\sisPscd\App\scripts\svpodrpw\hml\batch\ConsultaLote\ConsultaXmlTissCham.bat T:\sisPscd\App\scripts\svpodrpw\hml\batch\ConsultaLote\ConsultaXmlTiss.bat

-
CONFIGURAR O SCRIPT NO SCHEDULER DO SVPODRPW01 - PRODUÇÃO
-

SALVAR UMA CÓPIA DOS SCRIPT DO T E NO W
T:\sisPscd\App\scripts\svpodrpw\prd\batch\Caixa W:\sisPscd\App\scripts\svpodrpw\prd\batch\Caixa

============================================================
Acompanhamento de Resultados (DASA Oficial)
============================================================

| Resultado Desejado: |
| Resultado Alcançado: |
| Comentário sobre os resultados alcanados: |

============================================================
Descrição da História (DASA Oficial)
============================================================

Estória de Usuário

| Como: | Recebíveis
| Quero: | Integrar o PSCD com CAIXA
| Para: | Eficiência do Processo de Postagem
|

Desenho:

- Se houver
| N/A

Escopo da Alteração

| Sistema: | PSCD
| Micro Serviço: | Processos TISS do CAIXA

Detalhes

| Dependências: | FERJ
| Riscos: | Que o serviços da CAIXA estejam funcionais
| Exemplos: | N/D
| Monitoramento: | N/D
| Volumetria: | N/D
| Fora do escopo: | N/D
| 
Outros detalhes:

- Se houver
| N/D

Critério de Aceite 01

| Dado: | Estabelecer a integração a CAIXA
| Quando: | Postagem do lotes Guia e Consulta Status Protocolo
| Então: | Troca de informação com a CAIXA
|

Telas:

- Se houver
| N/A

Critério de Aceite 02

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

Critério de Aceite XX

| Dado: | (pr-condição)
| Quando: | (ação do evento)
| Então: | (resultado esperado)
|

Telas:

- Se houver
|

============================================================
Descrição
============================================================

Por que (problema identificado):

Objetivo:

Como/ Recursos:

Critérios de aceite:', 'Average', NULL, '2024-09-17 10:47:55', '2024-12-05 09:50:05');

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
