-- =================================================================================
-- Script:         007_Add_Contact_Tables_Documentation.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Adiciona a documentação (Extended Properties) nas tabelas e colunas
-- de contato (phones, emails, addresses).
--
-- Pré-requisitos:
-- - Executar após o script 006.
-- =================================================================================

USE pro_team_care;
GO

-- Tabela [core].[phones]
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Armazena telefones de contato de forma polimórfica.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'phones';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Tipo da entidade dona do telefone (Ex: App\Models\People).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'phones', @level2type=N'COLUMN',@level2name=N'phoneable_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ID da entidade dona do telefone.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'phones', @level2type=N'COLUMN',@level2name=N'phoneable_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Flag que indica se este é o telefone principal da entidade.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'phones', @level2type=N'COLUMN',@level2name=N'is_principal';
GO

-- Tabela [core].[emails]
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Armazena emails de contato de forma polimórfica.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'emails';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Tipo da entidade dona do email (Ex: App\Models\People).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'emails', @level2type=N'COLUMN',@level2name=N'emailable_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ID da entidade dona do email.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'emails', @level2type=N'COLUMN',@level2name=N'emailable_id';
GO

-- Tabela [core].[addresses]
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Armazena endereços de forma polimórfica.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'addresses';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Tipo da entidade dona do endereço (Ex: App\Models\People).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'addresses', @level2type=N'COLUMN',@level2name=N'addressable_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ID da entidade dona do endereço.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'addresses', @level2type=N'COLUMN',@level2name=N'addressable_id';
GO
