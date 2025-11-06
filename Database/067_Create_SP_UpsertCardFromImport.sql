-- Descrição: Cria a SP [core].[sp_UpsertCardFromImport] para criar ou atualizar um card a partir de dados de importação (CSV).
-- Data: 2025-11-05
-- Autor: Gemini
-- Versão: 1.0

USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT 'Iniciando criação da Stored Procedure [core].[sp_UpsertCardFromImport]';
PRINT '================================================================================';

IF OBJECT_ID('[core].[sp_UpsertCardFromImport]', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE [core].[sp_UpsertCardFromImport];
    PRINT 'Stored Procedure [core].[sp_UpsertCardFromImport] existente foi removida.';
END
GO

CREATE PROCEDURE [core].[sp_UpsertCardFromImport]
    -- Parâmetros que correspondem às colunas do CSV
    @ExternalCardID VARCHAR(50),
    @Title NVARCHAR(255),
    @Description NVARCHAR(MAX) = NULL,
    @OwnerName NVARCHAR(255) = NULL,
    @DeadlineStr VARCHAR(50) = NULL,
    @Priority NVARCHAR(20) = 'Average',
    @ColumnName NVARCHAR(100) = NULL,
    @ActualEndDateStr VARCHAR(50) = NULL,
    @LastStartDateStr VARCHAR(50) = NULL,
    @LastComment NVARCHAR(MAX) = NULL,
    @CardURL NVARCHAR(MAX) = NULL,

    -- Parâmetros de contexto
    @CompanyID BIGINT,
    @DefaultUserID BIGINT,
    
    -- Parâmetros de saída
    @NewCardID INT OUTPUT,
    @ActionTaken NVARCHAR(10) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRANSACTION;

    BEGIN TRY
        -- 1. DECLARAÇÃO DE VARIÁVEIS
        DECLARE @CardID INT = NULL;
        DECLARE @UserID BIGINT = @DefaultUserID;
        DECLARE @ColumnID INT = 1; -- Default: Backlog (ID=1)
        DECLARE @Deadline DATETIME2 = TRY_CONVERT(DATETIME2, @DeadlineStr);
        DECLARE @CompletedDate DATETIME2 = TRY_CONVERT(DATETIME2, @ActualEndDateStr);
        DECLARE @StartDate DATETIME2 = TRY_CONVERT(DATETIME2, @LastStartDateStr);

        -- 2. MAPEAR NOME DA COLUNA PARA ColumnID
        IF @ColumnName IS NOT NULL AND LTRIM(RTRIM(@ColumnName)) <> ''
        BEGIN
            SELECT @ColumnID = ColumnID 
            FROM [core].[CardColumns]
            WHERE CompanyID = @CompanyID 
              AND ColumnName = @ColumnName
              AND IsActive = 1;
            
            -- Se não encontrar, manter Backlog como padrão
            IF @ColumnID IS NULL
                SET @ColumnID = 1;
        END

        -- 3. BUSCA DO CARD EXISTENTE
        SELECT @CardID = CardID FROM [core].[Cards]
        WHERE ExternalCardID = @ExternalCardID AND CompanyID = @CompanyID;

        SET @ActionTaken = CASE WHEN @CardID IS NOT NULL THEN 'UPDATED' ELSE 'CREATED' END;

    -- 4. UPSERT DO CARD
        IF @CardID IS NOT NULL
        BEGIN
            -- UPDATE: Card existe
            UPDATE [core].[Cards]
            SET Title = @Title,
                Description = @Description,
                Priority = @Priority,
                ColumnID = @ColumnID,
                DueDate = @Deadline,
                CompletedDate = ISNULL(@CompletedDate, CompletedDate),  -- Atualizar apenas se vier preenchido
                StartDate = ISNULL(@StartDate, StartDate)  -- Atualizar apenas se vier preenchido
            WHERE CardID = @CardID;
            SET @NewCardID = @CardID;
        END
        ELSE
        BEGIN
            -- INSERT: Card novo
            INSERT INTO [core].[Cards] (
                CompanyID, UserID, ColumnID, Title, Description, Priority,
                DueDate, StartDate, CompletedDate, ExternalCardID,
                DisplayOrder, CreatedAt, IsDeleted
            )
            VALUES (
                @CompanyID, @UserID, @ColumnID, @Title, @Description, @Priority,
                @Deadline, @StartDate, @CompletedDate, @ExternalCardID,
                0, ISNULL(@StartDate, GETUTCDATE()), 0
            );

            SET @NewCardID = SCOPE_IDENTITY();
        END

        -- 5. MOVIMENTOS
        IF @ActionTaken = 'CREATED'
        BEGIN
            -- Movimento 1: Card criado (data de criação do card)
            DECLARE @CreatedAt DATETIME2 = ISNULL(@StartDate, GETUTCDATE());
            
            INSERT INTO [core].[CardMovements] (
                CardID, UserID, LogDate, Subject, OldColumnID, NewColumnID, MovementType
            )
            VALUES (
                @NewCardID, @UserID, @CreatedAt,
                'Card Criado (Importado)', NULL, @ColumnID, 'Created'
            );

            -- Movimento 2: Se iniciou trabalho (saiu do Backlog)
            IF @StartDate IS NOT NULL AND @ColumnID > 1
            BEGIN
                INSERT INTO [core].[CardMovements] (
                    CardID, UserID, LogDate, Subject, OldColumnID, NewColumnID, MovementType
                )
                VALUES (
                    @NewCardID, @UserID, @StartDate,
                    'Trabalho Iniciado (Importado)', 1, @ColumnID, 'ColumnChange'
                );
            END

            -- Movimento 3: Se foi concluído
            IF @CompletedDate IS NOT NULL
            BEGIN
                -- Buscar ID da coluna "Concluído"
                DECLARE @CompletedColumnID INT;
                SELECT @CompletedColumnID = ColumnID 
                FROM [core].[CardColumns]
                WHERE CompanyID = @CompanyID 
                  AND (ColumnName LIKE '%Conclu%' OR ColumnName LIKE '%Done%')
                  AND IsActive = 1;
                
                IF @CompletedColumnID IS NOT NULL
                BEGIN
                    INSERT INTO [core].[CardMovements] (
                        CardID, UserID, LogDate, Subject, OldColumnID, NewColumnID, MovementType
                    )
                    VALUES (
                        @NewCardID, @UserID, @CompletedDate,
                        'Card Concluído (Importado)', @ColumnID, @CompletedColumnID, 'Completed'
                    );
                END
            END

            -- Movimento 4: Comentário da importação
            IF @LastComment IS NOT NULL AND LTRIM(RTRIM(@LastComment)) <> ''
            BEGIN
                INSERT INTO [core].[CardMovements] (
                    CardID, UserID, LogDate, Subject, Description, MovementType
                )
                VALUES (
                    @NewCardID, @UserID, GETUTCDATE(),
                    'Comentário da Importação', @LastComment, 'Comment'
                );
            END
        END

        COMMIT TRANSACTION;

        -- Valores já estão nos parâmetros OUTPUT
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

PRINT '================================================================================';
PRINT '✅ SUCESSO: Stored Procedure [core].[sp_UpsertCardFromImport] criada.';
PRINT '================================================================================';
GO
