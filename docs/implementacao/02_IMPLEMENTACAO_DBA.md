# Implementação DBA - Módulo de Atividades com IA

**Responsável:** DBA  
**Tempo Estimado:** 2-3 horas  
**Dependências:** Nenhuma

---

## 📋 Tarefas

### 1. Criar Script SQL
- **Arquivo:** `Database/042_Create_Activity_Tracker_Tables.sql`
- **Ordem:** Próximo número sequencial disponível

### 2. Estrutura das Tabelas

```sql
-- ============================================
-- Script: 042_Create_Activity_Tracker_Tables.sql
-- Descrição: Módulo de Gestão de Atividades com IA
-- Data: 2025-11-03
-- ============================================

USE [pro_team_care];
GO

-- Tabela principal de atividades
CREATE TABLE [core].[Activities] (
    ActivityID INT IDENTITY(1,1) PRIMARY KEY,
    CompanyID INT NOT NULL,
    UserID INT NOT NULL,
    Title NVARCHAR(255) NOT NULL,
    Status NVARCHAR(50) NOT NULL, -- Pendente, Em Andamento, Concluído, Cancelado
    CreationDate DATETIME2 DEFAULT GETDATE(),
    DueDate DATETIME2 NULL,
    IsActive BIT DEFAULT 1,
    CONSTRAINT FK_Activities_Company FOREIGN KEY (CompanyID) REFERENCES [core].[Companies](CompanyID),
    CONSTRAINT FK_Activities_User FOREIGN KEY (UserID) REFERENCES [core].[Users](UserID)
);
GO

CREATE INDEX IX_Activities_Company ON [core].[Activities](CompanyID);
CREATE INDEX IX_Activities_User ON [core].[Activities](UserID);
CREATE INDEX IX_Activities_Status ON [core].[Activities](Status);
GO

-- Conteúdo bruto e análise da IA
CREATE TABLE [core].[ActivityContents] (
    ContentID INT IDENTITY(1,1) PRIMARY KEY,
    ActivityID INT NOT NULL,
    RawText NVARCHAR(MAX) NULL,
    RawImagePath NVARCHAR(500) NULL,
    AIExtractionJSON NVARCHAR(MAX) NULL, -- JSON bruto da IA
    UserCorrectedJSON NVARCHAR(MAX) NULL, -- JSON validado pelo usuário
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_ActivityContents_Activity FOREIGN KEY (ActivityID) REFERENCES [core].[Activities](ActivityID) ON DELETE CASCADE
);
GO

CREATE INDEX IX_ActivityContents_Activity ON [core].[ActivityContents](ActivityID);
GO

-- Entidades extraídas (pessoas, sistemas, links)
CREATE TABLE [core].[ActivityEntities] (
    EntityID INT IDENTITY(1,1) PRIMARY KEY,
    ActivityID INT NOT NULL,
    EntityType NVARCHAR(50) NOT NULL, -- Pessoa, Sistema, Link
    EntityName NVARCHAR(255) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_ActivityEntities_Activity FOREIGN KEY (ActivityID) REFERENCES [core].[Activities](ActivityID) ON DELETE CASCADE
);
GO

CREATE INDEX IX_ActivityEntities_Activity ON [core].[ActivityEntities](ActivityID);
CREATE INDEX IX_ActivityEntities_Type ON [core].[ActivityEntities](EntityType);
GO

-- Pendências/Tarefas
CREATE TABLE [core].[Pendencies] (
    PendencyID INT IDENTITY(1,1) PRIMARY KEY,
    ActivityID INT NOT NULL,
    Description NVARCHAR(500) NOT NULL,
    Owner NVARCHAR(255) NULL, -- Responsável
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pendente', -- Pendente, Cobrado, Resolvido
    Impediment NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    ResolvedAt DATETIME2 NULL,
    CONSTRAINT FK_Pendencies_Activity FOREIGN KEY (ActivityID) REFERENCES [core].[Activities](ActivityID) ON DELETE CASCADE
);
GO

CREATE INDEX IX_Pendencies_Activity ON [core].[Pendencies](ActivityID);
CREATE INDEX IX_Pendencies_Status ON [core].[Pendencies](Status);
CREATE INDEX IX_Pendencies_Owner ON [core].[Pendencies](Owner);
GO

PRINT 'Tabelas do módulo de Atividades criadas com sucesso!';
GO
```

---

## ✅ Checklist de Execução

- [ ] Criar arquivo `042_Create_Activity_Tracker_Tables.sql`
- [ ] Executar script no banco `pro_team_care`
- [ ] Verificar criação das 4 tabelas
- [ ] Verificar índices criados
- [ ] Testar constraints (FKs)
- [ ] Documentar no log de alterações

---

## 🔍 Validação

```sql
-- Verificar tabelas criadas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'core' 
AND TABLE_NAME LIKE 'Activit%' OR TABLE_NAME = 'Pendencies';

-- Verificar índices
SELECT 
    t.name AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType
FROM sys.indexes i
INNER JOIN sys.tables t ON i.object_id = t.object_id
WHERE t.name IN ('Activities', 'ActivityContents', 'ActivityEntities', 'Pendencies');
```

---

## 📝 Observações

- **Multi-tenant:** CompanyID garante isolamento
- **Cascade Delete:** Deletar Activity remove Contents, Entities e Pendencies
- **Índices:** Otimizados para queries por empresa, usuário e status
- **JSON:** Campos NVARCHAR(MAX) para flexibilidade da IA
