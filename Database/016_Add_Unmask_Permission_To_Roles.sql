-- =================================================================================
-- Script:         016_Add_Unmask_Permission_To_Roles.sql
-- Projeto:        Pro Team Care
-- Descrição:
-- Adiciona a coluna [can_unmask_pii] à tabela [core].[roles] para
-- controlar explicitamente quais papéis podem visualizar dados sensíveis (LGPD).
-- =================================================================================
USE pro_team_care;
GO

BEGIN TRANSACTION;

-- Adiciona a coluna, permitindo nulos inicialmente para não quebrar
ALTER TABLE [core].[roles]
ADD [can_unmask_pii] BIT NULL;
GO

-- Define um valor padrão de 0 (falso) para a coluna
DECLARE @ConstraintName NVARCHAR(255) = N'DF_roles_can_unmask_pii';
DECLARE @SQL NVARCHAR(MAX) = N'ALTER TABLE [core].[roles] ADD CONSTRAINT ' + @ConstraintName + N' DEFAULT 0 FOR [can_unmask_pii];';
EXEC sp_executesql @SQL;
GO

-- Atualiza todos os registros existentes que são nulos para o valor padrão 0
UPDATE [core].[roles] SET [can_unmask_pii] = 0 WHERE [can_unmask_pii] IS NULL;
GO

-- Altera a coluna para não permitir mais nulos
ALTER TABLE [core].[roles]
ALTER COLUMN [can_unmask_pii] BIT NOT NULL;
GO

-- Agora, concede a permissão explicitamente para os papéis de super admin
UPDATE [core].[roles]
SET [can_unmask_pii] = 1
WHERE [name] IN ('super_admin', 'granular_super_admin');

COMMIT;
GO

PRINT 'Coluna [can_unmask_pii] adicionada e configurada com sucesso na tabela [core].[roles].';
