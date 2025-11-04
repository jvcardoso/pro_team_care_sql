-- =================================================================================
-- Script:         008_Create_Database_pro_team_care_logs.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Cria o banco de dados dedicado para logs, 'pro_team_care_logs',
-- com arquivos .mdf e .ldf em caminhos personalizados.
-- =================================================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'pro_team_care_logs')
BEGIN
    CREATE DATABASE [pro_team_care_logs]
    ON PRIMARY (
        NAME = N'pro_team_care_logs',
        -- Caminho para o arquivo de dados (.mdf)
        FILENAME = N'C:\pro_team_care\Banco\Data\pro_team_care_logs.mdf',
        SIZE = 8192KB, -- 8 MB
        FILEGROWTH = 65536KB -- 64 MB
    )
    LOG ON (
        NAME = N'pro_team_care_logs_log',
        -- Caminho para o arquivo de log (.ldf)
        FILENAME = N'C:\pro_team_care\Banco\Logs\pro_team_care_logs_log.ldf',
        SIZE = 8192KB, -- 8 MB
        FILEGROWTH = 65536KB -- 64 MB
    );
END
GO
