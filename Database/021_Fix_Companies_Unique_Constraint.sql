-- Script 021_Fix_Companies_Unique_Constraint.sql
USE pro_team_care;
GO

BEGIN TRANSACTION;

IF EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'companies_person_id_unique' AND type = 'UQ')
BEGIN
    PRINT 'Removendo a constraint antiga [companies_person_id_unique]...';
    ALTER TABLE [core].[companies] DROP CONSTRAINT [companies_person_id_unique];
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_companies_person_id_not_null' AND object_id = OBJECT_ID('core.companies'))
BEGIN
    PRINT 'Criando o novo índice único filtrado [IX_companies_person_id_not_null]...';
    CREATE UNIQUE NONCLUSTERED INDEX [IX_companies_person_id_not_null]
    ON [core].[companies](person_id)
    WHERE person_id IS NOT NULL;
END

COMMIT;
GO

PRINT '✅ Constraint de unicidade da tabela [companies] foi corrigida com sucesso.';
