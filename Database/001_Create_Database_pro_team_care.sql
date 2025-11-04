-- =================================================================================
-- Script:         001_Create_Database_pro_team_care.sql
-- Projeto:        Pro Team Care
-- Data:           19/10/2025
-- Autor:          Gemini DBA
--
-- Descrição:
-- Cria o banco de dados principal da aplicação, 'pro_team_care',
-- e o schema 'core' que abrigará todas as tabelas.
-- =================================================================================

CREATE DATABASE pro_team_care;
GO

USE pro_team_care;
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'core')
BEGIN
    EXEC('CREATE SCHEMA [core]');
END
GO