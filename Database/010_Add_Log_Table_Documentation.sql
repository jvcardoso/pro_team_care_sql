-- =================================================================================
-- Script:         010_Add_Log_Table_Documentation.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Adiciona a documentação (Extended Properties) na tabela 'login_logs'.
--
-- Pré-requisitos:
-- - Executar após o script 009.
-- =================================================================================

USE pro_team_care_logs;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.extended_properties ep
    JOIN sys.tables t ON ep.major_id = t.object_id
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'core' AND t.name = 'login_logs' AND ep.name = 'MS_Description' AND ep.minor_id = 0
)
BEGIN
    EXEC sp_addextendedproperty
        @name=N'MS_Description', @value=N'Armazena um histórico de todas as tentativas de login, bem-sucedidas ou não.',
        @level0type=N'SCHEMA', @level0name=N'core',
        @level1type=N'TABLE', @level1name=N'login_logs';

    EXEC sp_addextendedproperty
        @name=N'MS_Description', @value=N'ID da empresa associada à tentativa. Nulo se o email não for encontrado.',
        @level0type=N'SCHEMA', @level0name=N'core',
        @level1type=N'TABLE', @level1name=N'login_logs',
        @level2type=N'COLUMN', @level2name=N'company_id';

    EXEC sp_addextendedproperty
        @name=N'MS_Description', @value=N'Status da tentativa de login (SUCCESS, FAILED, INACTIVE_USER_ATTEMPT).',
        @level0type=N'SCHEMA', @level0name=N'core',
        @level1type=N'TABLE', @level1name=N'login_logs',
        @level2type=N'COLUMN', @level2name=N'status';
END
GO
