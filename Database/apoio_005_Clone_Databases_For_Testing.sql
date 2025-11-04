-- =================================================================================
-- Script:         Clone_Databases_For_Testing.sql (v1.2 - Express Edition Fix)
-- Descrição:
-- v1.2 - Remove a opção WITH COMPRESSION, que não é suportada pelo SQL Server
--        Express Edition. O caminho do backup foi pré-configurado.
-- =================================================================================

-- **********************************************************************************
-- ****** CONFIGURAÇÃO: O caminho do backup já foi ajustado abaixo.   ******
-- **********************************************************************************
DECLARE @backupPath NVARCHAR(MAX) = 'C:\pro_team_care\Banco\Backup\';
-- **********************************************************************************


SET NOCOUNT ON;
IF RIGHT(@backupPath, 1) <> '\' SET @backupPath = @backupPath + '\';

------------------------------------------------------------------------------------
-- CLONANDO O BANCO DE DADOS PRINCIPAL: pro_team_care
------------------------------------------------------------------------------------
PRINT '--- Iniciando clone do banco de dados [pro_team_care] ---';

DECLARE @sourceDbName NVARCHAR(128) = 'pro_team_care';
DECLARE @destDbName NVARCHAR(128) = 'pro_team_care_test';
DECLARE @backupFile NVARCHAR(MAX) = @backupPath + @sourceDbName + '.bak';
DECLARE @sql NVARCHAR(MAX);

IF DB_ID(@destDbName) IS NOT NULL
BEGIN
    PRINT 'Apagando o banco de dados de teste antigo: ' + QUOTENAME(@destDbName);
    SET @sql = N'ALTER DATABASE ' + QUOTENAME(@destDbName) + N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE;';
    EXEC sp_executesql @sql;
    SET @sql = N'DROP DATABASE ' + QUOTENAME(@destDbName) + N';';
    EXEC sp_executesql @sql;
END

PRINT '1/3: Fazendo backup de ' + QUOTENAME(@sourceDbName) + ' para ' + @backupFile;
-- CORREÇÃO: Removido ", COMPRESSION" do final da linha
BACKUP DATABASE @sourceDbName TO DISK = @backupFile WITH INIT;

DECLARE @logicalDataName NVARCHAR(128), @logicalLogName NVARCHAR(128);
DECLARE @fileList TABLE (LogicalName NVARCHAR(128), PhysicalName NVARCHAR(260), Type CHAR(1), FileGroupName NVARCHAR(128), Size BIGINT, MaxSize BIGINT, FileId BIGINT, CreateLSN NUMERIC(25,0), DropLSN NUMERIC(25,0), UniqueID UNIQUEIDENTIFIER, ReadOnlyLSN NUMERIC(25,0), ReadWriteLSN NUMERIC(25,0), BackupSizeInBytes BIGINT, SourceBlockSize INT, FileGroupID INT, LogGroupGUID UNIQUEIDENTIFIER, DifferentialBaseLSN NUMERIC(25,0), DifferentialBaseGUID UNIQUEIDENTIFIER, IsReadOnly BIT, IsPresent BIT, TDEThumbprint VARBINARY(32), SnapshotURL NVARCHAR(360));
INSERT INTO @fileList EXEC('RESTORE FILELISTONLY FROM DISK = ''' + @backupFile + '''');
SELECT @logicalDataName = LogicalName FROM @fileList WHERE Type = 'D';
SELECT @logicalLogName = LogicalName FROM @fileList WHERE Type = 'L';

PRINT '2/3: Restaurando o backup com o novo nome: ' + QUOTENAME(@destDbName);
DECLARE @dataFilePath NVARCHAR(MAX) = (SELECT physical_name FROM sys.master_files WHERE database_id = DB_ID(@sourceDbName) AND type_desc = 'ROWS');
DECLARE @logFilePath NVARCHAR(MAX) = (SELECT physical_name FROM sys.master_files WHERE database_id = DB_ID(@sourceDbName) AND type_desc = 'LOG');
DECLARE @destDataFile NVARCHAR(MAX) = REPLACE(@dataFilePath, @sourceDbName + '.mdf', @destDbName + '.mdf');
DECLARE @destLogFile NVARCHAR(MAX) = REPLACE(@logFilePath, '.ldf', '_test.ldf'); -- Nome de arquivo ligeiramente ajustado para evitar conflitos

RESTORE DATABASE @destDbName
FROM DISK = @backupFile
WITH
    MOVE @logicalDataName TO @destDataFile,
    MOVE @logicalLogName TO @destLogFile;

PRINT '3/3: Clone [pro_team_care_test] criado com sucesso!';
GO


------------------------------------------------------------------------------------
-- CLONANDO O BANCO DE DADOS DE LOGS: pro_team_care_logs
------------------------------------------------------------------------------------
PRINT CHAR(10) + '--- Iniciando clone do banco de dados [pro_team_care_logs] ---';

DECLARE @backupPath_logs NVARCHAR(MAX) = 'C:\pro_team_care\Banco\Backup\';
SET NOCOUNT ON;
IF RIGHT(@backupPath_logs, 1) <> '\' SET @backupPath_logs = @backupPath_logs + '\';

DECLARE @sourceDbName_logs NVARCHAR(128) = 'pro_team_care_logs';
DECLARE @destDbName_logs NVARCHAR(128) = 'pro_team_care_logs_test';
DECLARE @backupFile_logs NVARCHAR(MAX) = @backupPath_logs + @sourceDbName_logs + '.bak';
DECLARE @sql_logs NVARCHAR(MAX);

IF DB_ID(@destDbName_logs) IS NOT NULL
BEGIN
    PRINT 'Apagando o banco de dados de teste antigo: ' + QUOTENAME(@destDbName_logs);
    SET @sql_logs = N'ALTER DATABASE ' + QUOTENAME(@destDbName_logs) + N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE;';
    EXEC sp_executesql @sql_logs;
    SET @sql_logs = N'DROP DATABASE ' + QUOTENAME(@destDbName_logs) + N';';
    EXEC sp_executesql @sql_logs;
END

PRINT '1/3: Fazendo backup de ' + QUOTENAME(@sourceDbName_logs) + ' para ' + @backupFile_logs;
-- CORREÇÃO: Removido ", COMPRESSION" do final da linha
BACKUP DATABASE @sourceDbName_logs TO DISK = @backupFile_logs WITH INIT;

DECLARE @logicalDataName_logs NVARCHAR(128), @logicalLogName_logs NVARCHAR(128);
DECLARE @fileList_logs TABLE (LogicalName NVARCHAR(128), PhysicalName NVARCHAR(260), Type CHAR(1), FileGroupName NVARCHAR(128), Size BIGINT, MaxSize BIGINT, FileId BIGINT, CreateLSN NUMERIC(25,0), DropLSN NUMERIC(25,0), UniqueID UNIQUEIDENTIFIER, ReadOnlyLSN NUMERIC(25,0), ReadWriteLSN NUMERIC(25,0), BackupSizeInBytes BIGINT, SourceBlockSize INT, FileGroupID INT, LogGroupGUID UNIQUEIDENTIFIER, DifferentialBaseLSN NUMERIC(25,0), DifferentialBaseGUID UNIQUEIDENTIFIER, IsReadOnly BIT, IsPresent BIT, TDEThumbprint VARBINARY(32), SnapshotURL NVARCHAR(360));
INSERT INTO @fileList_logs EXEC('RESTORE FILELISTONLY FROM DISK = ''' + @backupFile_logs + '''');
SELECT @logicalDataName_logs = LogicalName FROM @fileList_logs WHERE Type = 'D';
SELECT @logicalLogName_logs = LogicalName FROM @fileList_logs WHERE Type = 'L';

PRINT '2/3: Restaurando o backup com o novo nome: ' + QUOTENAME(@destDbName_logs);
DECLARE @dataFilePath_logs NVARCHAR(MAX) = (SELECT physical_name FROM sys.master_files WHERE database_id = DB_ID(@sourceDbName_logs) AND type_desc = 'ROWS');
DECLARE @logFilePath_logs NVARCHAR(MAX) = (SELECT physical_name FROM sys.master_files WHERE database_id = DB_ID(@sourceDbName_logs) AND type_desc = 'LOG');
DECLARE @destDataFile_logs NVARCHAR(MAX) = REPLACE(@dataFilePath_logs, @sourceDbName_logs + '.mdf', @destDbName_logs + '.mdf');
DECLARE @destLogFile_logs NVARCHAR(MAX) = REPLACE(@logFilePath_logs, '.ldf', '_test.ldf'); -- Nome de arquivo ligeiramente ajustado para evitar conflitos

RESTORE DATABASE @destDbName_logs
FROM DISK = @backupFile_logs
WITH
    MOVE @logicalDataName_logs TO @destDataFile_logs,
    MOVE @logicalLogName_logs TO @destLogFile_logs;

PRINT '3/3: Clone [pro_team_care_logs_test] criado com sucesso!';
GO

------------------------------------------------------------------------------------
-- VERIFICAÇÃO FINAL
------------------------------------------------------------------------------------
PRINT CHAR(10) + '--- Verificação Final ---';
SELECT name, create_date FROM sys.databases WHERE name LIKE '%_test';
GO
