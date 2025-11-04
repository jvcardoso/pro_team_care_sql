-- =================================================================================
-- Script:         017_Create_Lgpd_Audit_Log_Table.sql (v1.1 - Corrigido)
-- Descrição:
-- v1.1 - Altera a coluna [sensitive_fields] de NVARCHAR(MAX) para JSON.
-- =================================================================================
USE pro_team_care_logs;
GO

CREATE TABLE [core].[lgpd_audit_log] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [company_id] BIGINT NOT NULL,
    [user_id] BIGINT NOT NULL,
    [user_email] NVARCHAR(255) NULL,
    [action_type] NVARCHAR(20) NOT NULL,
    [entity_type] NVARCHAR(50) NOT NULL,
    [entity_id] BIGINT NULL,
    [sensitive_fields] JSON NULL, -- CORREÇÃO: Alterado para JSON
    [changed_fields] JSON NULL,
    [ip_address] NVARCHAR(45) NULL,
    [endpoint] NVARCHAR(255) NULL,
    [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),

    CONSTRAINT [CHK_lgpd_audit_log_action] CHECK ([action_type] IN ('VIEW', 'CREATE', 'UPDATE', 'DELETE', 'EXPORT', 'REVEAL', 'LOGIN'))
);
GO

-- Índices para performance
CREATE INDEX [idx_lgpd_company_created] ON [core].[lgpd_audit_log] ([company_id], [created_at] DESC);
CREATE INDEX [idx_lgpd_entity] ON [core].[lgpd_audit_log] ([entity_type], [entity_id]);
CREATE INDEX [idx_lgpd_user_id] ON [core].[lgpd_audit_log] ([user_id]);
GO

PRINT 'Tabela [core].[lgpd_audit_log] (v1.1) criada com sucesso.';
