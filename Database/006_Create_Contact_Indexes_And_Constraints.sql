-- =================================================================================
-- Script:         006_Create_Contact_Indexes_And_Constraints.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Aplica índices (polimórficos e filtrados) e constraints (FKs, CHECKs)
-- nas tabelas de contato.
--
-- Pré-requisitos:
-- - Executar após o script 005.
-- =================================================================================

USE pro_team_care;
GO

-- Chaves Estrangeiras para company_id
ALTER TABLE [core].[phones] ADD CONSTRAINT [FK_phones_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies] ([id]);
ALTER TABLE [core].[emails] ADD CONSTRAINT [FK_emails_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies] ([id]);
ALTER TABLE [core].[addresses] ADD CONSTRAINT [FK_addresses_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies] ([id]);
GO

-- Índices Otimizados
-- Índice polimórfico para buscas rápidas
CREATE INDEX [idx_phones_phoneable] ON [core].[phones] ([phoneable_type], [phoneable_id]);
CREATE INDEX [idx_emails_emailable] ON [core].[emails] ([emailable_type], [emailable_id]);
CREATE INDEX [idx_addresses_addressable] ON [core].[addresses] ([addressable_type], [addressable_id]);
GO

-- Otimização: Garante que só pode haver UM telefone/email/endereço principal por "dono"
CREATE UNIQUE INDEX [uq_phones_one_principal] ON [core].[phones]([company_id], [phoneable_type], [phoneable_id]) WHERE ([is_principal] = 1 AND [deleted_at] IS NULL);
CREATE UNIQUE INDEX [uq_emails_one_principal] ON [core].[emails]([company_id], [emailable_type], [emailable_id]) WHERE ([is_principal] = 1 AND [deleted_at] IS NULL);
CREATE UNIQUE INDEX [uq_addresses_one_principal] ON [core].[addresses]([company_id], [addressable_type], [addressable_id]) WHERE ([is_principal] = 1 AND [deleted_at] IS NULL);
GO

-- Constraints de Checagem
ALTER TABLE [core].[phones] ADD CONSTRAINT [phones_type_check] CHECK ([type] IN ('landline', 'mobile', 'whatsapp', 'commercial', 'emergency', 'fax'));
ALTER TABLE [core].[emails] ADD CONSTRAINT [emails_type_check] CHECK ([type] IN ('personal', 'work', 'billing', 'contact'));
ALTER TABLE [core].[addresses] ADD CONSTRAINT [addresses_type_check] CHECK ([type] IN ('residential', 'commercial', 'correspondence', 'billing', 'delivery'));
GO
