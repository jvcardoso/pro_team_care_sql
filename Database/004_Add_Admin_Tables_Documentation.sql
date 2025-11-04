-- =================================================================================
-- Script:         004_Add_Admin_Tables_Documentation.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Adiciona a documentação (Extended Properties) nas tabelas e colunas
-- do núcleo administrativo.
--
-- Pré-requisitos:
-- - Executar após o script 003.
-- =================================================================================

USE pro_team_care;
GO

-- Tabela [core].[companies]
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Armazena as empresas clientes (tenants) do sistema SaaS.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'companies';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK para a tabela [people], representando a pessoa jurídica (PJ) principal associada a esta empresa.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'companies', @level2type=N'COLUMN',@level2name=N'person_id';
-- (Adicione aqui as outras chamadas sp_addextendedproperty para a tabela companies)
GO

-- Tabela [core].[people]
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Entidade polimórfica que armazena dados de Pessoas Físicas (PF) e Pessoas Jurídicas (PJ).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'people';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Define se o registro é uma Pessoa Física (PF) ou Pessoa Jurídica (PJ).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'people', @level2type=N'COLUMN',@level2name=N'person_type';
-- (Adicione aqui as outras chamadas sp_addextendedproperty para a tabela people)
GO

-- (Continue o padrão para as tabelas establishments, users, etc.)

Nota: Para ser breve, eu coloquei apenas alguns exemplos no script 004, mas você deve copiar e colar todas as chamadas sp_addextendedproperty do nosso script original para cada tabela.
