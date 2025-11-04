-- =================================================================================
-- Script:         003_Create_Admin_Indexes_And_Constraints.sql (v1.1 - Corrigido)
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Aplica índices, chaves estrangeiras (FKs) e constraints de checagem (CHECK)
-- nas tabelas do núcleo administrativo.
--
-- Histórico de Alterações:
-- v1.1 - Adicionado 'system_owner' à constraint de status da tabela companies.
-- =================================================================================

USE pro_team_care;
GO

-- Índices
CREATE INDEX [idx_users_active_non_deleted] ON [core].[users] ([email_address]) WHERE [deleted_at] IS NULL;
CREATE INDEX [idx_establishments_active_non_deleted] ON [core].[establishments] ([company_id], [is_active]) WHERE [deleted_at] IS NULL;
GO

-- Constraints para [companies]
ALTER TABLE [core].[companies] ADD CONSTRAINT [companies_person_id_unique] UNIQUE ([person_id]);
-- VERSÃO CORRIGIDA DA CONSTRAINT:
ALTER TABLE [core].[companies] ADD CONSTRAINT [companies_access_status_check] CHECK ([access_status] IN ('pending_contract', 'contract_signed', 'pending_user', 'active', 'suspended', 'system_owner'));
GO

-- (O restante do arquivo continua o mesmo...)
-- Constraints para [people]
ALTER TABLE [core].[people] ADD CONSTRAINT [FK_people_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies] ([id]);
ALTER TABLE [core].[people] ADD CONSTRAINT [people_person_type_check] CHECK ([person_type] IN ('PF', 'PJ'));
ALTER TABLE [core].[people] ADD CONSTRAINT [people_status_check] CHECK ([status] IN ('active', 'inactive', 'pending', 'suspended', 'blocked'));
ALTER TABLE [core].[people] ADD CONSTRAINT [people_company_tax_id_unique] UNIQUE ([company_id], [tax_id]);
GO

-- Constraints para [establishments]
ALTER TABLE [core].[establishments] ADD CONSTRAINT [FK_establishments_person] FOREIGN KEY ([person_id]) REFERENCES [core].[people] ([id]);
ALTER TABLE [core].[establishments] ADD CONSTRAINT [FK_establishments_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies] ([id]);
ALTER TABLE [core].[establishments] ADD CONSTRAINT [establishments_type_check] CHECK ([type] IN ('matriz', 'filial', 'unidade', 'posto'));
ALTER TABLE [core].[establishments] ADD CONSTRAINT [establishments_category_check] CHECK ([category] IN ('clinica', 'hospital', 'laboratorio', 'farmacia', 'consultorio', 'upa', 'ubs', 'outro'));
ALTER TABLE [core].[establishments] ADD CONSTRAINT [establishments_company_code_unique] UNIQUE ([company_id], [code]);
GO

-- Constraints para [roles]
ALTER TABLE [core].[roles] ADD CONSTRAINT [roles_context_type_check] CHECK ([context_type] IN ('system', 'company', 'establishment'));
GO

-- Constraints para [users]
ALTER TABLE [core].[users] ADD CONSTRAINT [FK_users_person] FOREIGN KEY ([person_id]) REFERENCES [core].[people] ([id]);
ALTER TABLE [core].[users] ADD CONSTRAINT [FK_users_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies] ([id]);
ALTER TABLE [core].[users] ADD CONSTRAINT [FK_users_establishment] FOREIGN KEY ([establishment_id]) REFERENCES [core].[establishments] ([id]);
ALTER TABLE [core].[users] ADD CONSTRAINT [FK_users_invited_by] FOREIGN KEY ([invited_by_user_id]) REFERENCES [core].[users] ([id]);
GO

-- Constraints para [user_roles]
ALTER TABLE [core].[user_roles] ADD CONSTRAINT [FK_user_roles_user] FOREIGN KEY ([user_id]) REFERENCES [core].[users] ([id]);
ALTER TABLE [core].[user_roles] ADD CONSTRAINT [FK_user_roles_role] FOREIGN KEY ([role_id]) REFERENCES [core].[roles] ([id]);
ALTER TABLE [core].[user_roles] ADD CONSTRAINT [FK_user_roles_assigned_by] FOREIGN KEY ([assigned_by_user_id]) REFERENCES [core].[users] ([id]);
ALTER TABLE [core].[user_roles] ADD CONSTRAINT [user_roles_context_type_check] CHECK ([context_type] IN ('system', 'company', 'establishment'));
ALTER TABLE [core].[user_roles] ADD CONSTRAINT [user_roles_status_check] CHECK ([status] IN ('active', 'inactive', 'suspended', 'expired'));
ALTER TABLE [core].[user_roles] ADD CONSTRAINT [user_roles_unique] UNIQUE ([user_id], [role_id], [context_type], [context_id]);
GO

-- FKs Finais (para dependências circulares ou tardias)
ALTER TABLE [core].[companies] ADD CONSTRAINT [FK_companies_person] FOREIGN KEY ([person_id]) REFERENCES [core].[people] ([id]);
ALTER TABLE [core].[companies] ADD CONSTRAINT [FK_companies_activated_by_user] FOREIGN KEY ([activated_by_user_id]) REFERENCES [core].[users] ([id]);
GO