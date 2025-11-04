-- Limpar dados de teste
USE pro_team_care_test;
GO

-- Deletar na ordem correta (respeitando FKs)
DELETE FROM [core].[pj_profiles];
DELETE FROM [core].[pf_profiles];
DELETE FROM [core].[people];
DELETE FROM [core].[companies] WHERE person_id IS NULL OR person_id > 0;

PRINT 'Banco de teste limpo!';
