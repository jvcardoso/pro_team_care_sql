USE [pro_team_care];
GO

PRINT '================================================================================';
PRINT '[CORREÇÃO FINAL] Atualizando SP core.UpsertCardFromImport para incluir classificação ITIL e tipos corretos';
PRINT '================================================================================';

IF OBJECT_ID('core.UpsertCardFromImport', 'P') IS NOT NULL
    DROP PROCEDURE core.UpsertCardFromImport;
GO

CREATE PROCEDURE core.UpsertCardFromImport
    @CompanyID BIGINT,
    @UserID BIGINT,
    @ExternalCardID NVARCHAR(255),
    @Title NVARCHAR(255),
    @Description NVARCHAR(MAX),
    @ColumnName NVARCHAR(255),
    @Priority NVARCHAR(50),
    @Deadline DATETIME = NULL,
    @StartDate DATETIME = NULL,
    @CompletedDate DATETIME = NULL,
    @LastComment NVARCHAR(MAX),
    @Size NVARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CardID INT;
    DECLARE @ColumnID INT;

    -- Obter ColumnID
    SELECT @ColumnID = ColumnID
    FROM core.CardColumns
    WHERE CompanyID = @CompanyID AND ColumnName = @ColumnName;

    IF @ColumnID IS NULL
    BEGIN
        -- Se a coluna não existir, criar e obter o novo ID
        INSERT INTO core.CardColumns (CompanyID, ColumnName, CreatedAt)
        VALUES (@CompanyID, @ColumnName, GETUTCDATE());
        
        SET @ColumnID = SCOPE_IDENTITY();
    END

    -- CLASSIFICAÇÃO ITIL
    DECLARE @TextBlob NVARCHAR(MAX) = CONCAT(
        ISNULL(@Title, ''), ' ',
        ISNULL(@Description, ''), ' ',
        ISNULL(@LastComment, '')
    );

    DECLARE @ITILCategory VARCHAR(30) =
        CASE
            WHEN @TextBlob LIKE '%GMUD%' OR @TextBlob LIKE '%RDM%' OR @TextBlob LIKE '%CHG%' OR @TextBlob LIKE '%Deploy%' OR @TextBlob LIKE '%Janela%' OR @TextBlob LIKE '%CAB%' THEN 'Change'
            WHEN @TextBlob LIKE '%Falha%' OR @TextBlob LIKE '%Erro%' OR @TextBlob LIKE '%Incidente%' OR @TextBlob LIKE '%Indisponibilidade%' THEN 'Incident'
            WHEN @TextBlob LIKE '%Solicitar%' OR @TextBlob LIKE '%Criar grupo%' OR @TextBlob LIKE '%Permiss%' OR @TextBlob LIKE '%Acesso%' THEN 'Service Request'
            ELSE 'Operation Task'
        END;

    DECLARE @HasWindow BIT = CASE WHEN @TextBlob LIKE '%Janela%' OR @TextBlob LIKE '%window%' THEN 1 ELSE 0 END;
    DECLARE @HasCAB BIT = CASE WHEN @TextBlob LIKE '%CAB%' OR @TextBlob LIKE '%Comitê%' THEN 1 ELSE 0 END;
    DECLARE @HasBackout BIT = CASE WHEN @TextBlob LIKE '%backout%' OR @TextBlob LIKE '%rollback%' THEN 1 ELSE 0 END;

    DECLARE @PriorityNorm VARCHAR(10) = 
        CASE LOWER(ISNULL(@Priority, ''))
            WHEN 'high' THEN 'High'
            WHEN 'average' THEN 'Medium'
            WHEN 'low' THEN 'Low'
            ELSE 'Medium'
        END;

    DECLARE @RiskLevel VARCHAR(20) =
        CASE
            WHEN @ITILCategory = 'Change' AND @HasCAB = 1 AND @HasBackout = 1 THEN 'Low'
            WHEN @ITILCategory = 'Change' AND (@HasCAB = 0 OR @HasBackout = 0) THEN 'High'
            WHEN @ITILCategory = 'Incident' THEN 'High'
            ELSE 'Low'
        END;

    -- Verificar se o card já existe
    SELECT @CardID = CardID
    FROM core.Cards
    WHERE CompanyID = @CompanyID AND ExternalCardID = @ExternalCardID;

    IF @CardID IS NOT NULL
    BEGIN
        -- Atualizar card existente
        UPDATE [core].[Cards]
        SET Title = @Title,
            Description = @Description,
            OriginalText = @TextBlob,
            Priority = @PriorityNorm,
            ColumnID = @ColumnID,
            DueDate = @Deadline,
            CompletedDate = ISNULL(@CompletedDate, CompletedDate),
            StartDate = ISNULL(@StartDate, StartDate),
            ITILCategory = @ITILCategory,
            HasWindow = @HasWindow,
            HasCAB = @HasCAB,
            HasBackout = @HasBackout,
            Size = @Size,
            RiskLevel = @RiskLevel
        WHERE CardID = @CardID;
    END
    ELSE
    BEGIN
        -- Inserir novo card
        INSERT INTO [core].[Cards] (
            CompanyID, UserID, ColumnID, Title, Description, OriginalText,
            Priority, DueDate, StartDate, CompletedDate, ExternalCardID,
            ITILCategory, HasWindow, HasCAB, HasBackout, Size, RiskLevel,
            IsDeleted, CreatedAt, DisplayOrder
        )
        VALUES (
            @CompanyID, @UserID, @ColumnID, @Title, @Description, @TextBlob,
            @PriorityNorm, @Deadline, @StartDate, @CompletedDate, @ExternalCardID,
            @ITILCategory, @HasWindow, @HasCAB, @HasBackout, @Size, @RiskLevel,
            0, ISNULL(@StartDate, GETUTCDATE()), 0
        );
        SET @CardID = SCOPE_IDENTITY();
    END

    SELECT @CardID AS CardID;
END;
GO

PRINT '✅ Stored Procedure core.UpsertCardFromImport corrigida e atualizada com sucesso!';
PRINT '================================================================================';
GO