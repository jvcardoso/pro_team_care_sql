-- =================================================================================
-- Script:         013_Person_Profile_Enhancement.sql (v1.1 - Corrigido)
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Refatora a tabela [core].[people] para suportar perfis PF/PJ.
--
-- Histórico de Alterações:
-- v1.1 - Adicionada a remoção da CHECK constraint 'people_person_type_check'
--        antes de apagar a coluna 'person_type' para evitar erro de dependência.
-- =================================================================================

USE pro_team_care;
GO

SET NOCOUNT ON;
BEGIN TRANSACTION;

BEGIN TRY
    PRINT 'Iniciando a refatoração para perfis PF/PJ independentes...';

    -- Passo 1: Criar as novas tabelas de perfis
    CREATE TABLE [core].[pf_profiles] (
        [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [person_id] BIGINT NOT NULL, [tax_id] NVARCHAR(11) NOT NULL,
        [birth_date] DATE, [gender] NVARCHAR(20), [marital_status] NVARCHAR(50), [occupation] NVARCHAR(100),
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Tabela [core].[pf_profiles] criada.';

    CREATE TABLE [core].[pj_profiles] (
        [id] BIGINT IDENTITY(1,1) PRIMARY KEY, [person_id] BIGINT NOT NULL, [company_id] BIGINT NOT NULL,
        [tax_id] NVARCHAR(14) NOT NULL, [trade_name] NVARCHAR(200), [incorporation_date] DATE,
        [tax_regime] NVARCHAR(50), [legal_nature] NVARCHAR(100), [municipal_registration] NVARCHAR(20),
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(), [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Tabela [core].[pj_profiles] criada.';

    ALTER TABLE [core].[pf_profiles] ADD CONSTRAINT [FK_pf_profiles_person] FOREIGN KEY ([person_id]) REFERENCES [core].[people]([id]);
    ALTER TABLE [core].[pf_profiles] ADD CONSTRAINT [UQ_pf_profiles_person_id] UNIQUE ([person_id]);
    ALTER TABLE [core].[pf_profiles] ADD CONSTRAINT [UQ_pf_profiles_tax_id] UNIQUE ([tax_id]);

    ALTER TABLE [core].[pj_profiles] ADD CONSTRAINT [FK_pj_profiles_person] FOREIGN KEY ([person_id]) REFERENCES [core].[people]([id]);
    ALTER TABLE [core].[pj_profiles] ADD CONSTRAINT [FK_pj_profiles_company] FOREIGN KEY ([company_id]) REFERENCES [core].[companies]([id]);
    ALTER TABLE [core].[pj_profiles] ADD CONSTRAINT [UQ_pj_profiles_company_tax_id] UNIQUE ([company_id], [tax_id]);
    PRINT 'Constraints para as novas tabelas de perfil criadas.';

    -- Passo 2: Migrar os dados existentes de [people] para [pj_profiles]
    PRINT 'Migrando dados de PJ existentes de [people] para [pj_profiles]...';
    INSERT INTO [core].[pj_profiles]
        (person_id, company_id, tax_id, trade_name, incorporation_date, tax_regime, legal_nature, municipal_registration)
    SELECT
        id, company_id, tax_id, trade_name, incorporation_date, tax_regime, legal_nature, municipal_registration
    FROM [core].[people]
    WHERE person_type = 'PJ';
    PRINT CAST(@@ROWCOUNT AS VARCHAR) + ' registro(s) de PJ migrado(s).';

    -- Passo 3: Limpar a tabela [core].[people] para se tornar a tabela "raiz"
    PRINT 'Removendo constraints e colunas antigas da tabela [core].[people]...';

    -- Primeiro, remove as constraints que serão movidas ou que dependem de colunas a serem removidas
    ALTER TABLE [core].[people] DROP CONSTRAINT [people_company_tax_id_unique];
    -- CORREÇÃO: Adicionada a remoção da CHECK constraint que estava causando o erro.
    ALTER TABLE [core].[people] DROP CONSTRAINT [people_person_type_check];

    -- Agora, remove as colunas que foram migradas para os perfis
    ALTER TABLE [core].[people] DROP COLUMN
        person_type,
        trade_name,
        tax_id,
        secondary_tax_id,
        birth_date,
        incorporation_date,
        gender,
        marital_status,
        occupation,
        tax_regime,
        legal_nature,
        municipal_registration;
    
    PRINT 'Tabela [core].[people] foi limpa e agora atua como tabela raiz.';

    COMMIT TRANSACTION;
    PRINT CHAR(10) + 'SUCESSO: A estrutura foi refatorada para perfis PF/PJ independentes!';

END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT CHAR(10) + 'ERRO: A refatoração falhou e a transação foi revertida (rollback).';
    THROW;
END CATCH
GO