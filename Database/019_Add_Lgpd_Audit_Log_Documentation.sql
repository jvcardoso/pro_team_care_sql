-- =================================================================================
-- Script:         019_Add_Lgpd_Audit_Log_Documentation.sql
-- Projeto:        Pro Team Care
-- Descrição:
-- Adiciona a documentação (Extended Properties) na tabela [lgpd_audit_log].
-- =================================================================================
USE pro_team_care_logs;
GO

EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Registra eventos de auditoria relevantes para a LGPD, como visualização e revelação de dados sensíveis.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'lgpd_audit_log';
GO
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Tipo de ação auditada (VIEW, CREATE, REVEAL, etc.).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'lgpd_audit_log', @level2type=N'COLUMN',@level2name=N'action_type';
GO
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Tipo da entidade que sofreu a ação (ex: pf_profiles, pj_profiles).' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'lgpd_audit_log', @level2type=N'COLUMN',@level2name=N'entity_type';
GO
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Lista em formato JSON dos campos sensíveis que foram acessados ou revelados.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'lgpd_audit_log', @level2type=N'COLUMN',@level2name=N'sensitive_fields';
GO
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Objeto JSON contendo os valores antigos e novos de um campo após um UPDATE.' , @level0type=N'SCHEMA',@level0name=N'core', @level1type=N'TABLE',@level1name=N'lgpd_audit_log', @level2type=N'COLUMN',@level2name=N'changed_fields';
GO

PRINT 'Documentação para a tabela [lgpd_audit_log] adicionada com sucesso.';
