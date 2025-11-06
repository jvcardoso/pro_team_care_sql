# 🔧 Correção: Importação XLSX com Classificação ITIL

**Data:** 06/11/2025 17:40  
**Status:** ✅ CORRIGIDA

---

## 🎯 Problema Identificado

### **Erro Original:**
```
Connection is busy with results for another command
```

### **Root Cause:**
O endpoint de importação XLSX estava chamando a stored procedure `core.UpsertCardFromImport` com **parâmetros antigos** que não existem mais na versão atualizada com classificação ITIL.

**Parâmetros Incorretos (Antigos):**
- `@OwnerName`
- `@ActualEndDate`
- `@LastEndDate`
- `@LastStartDate`
- `@PlannedStart`
- `@CardURL`
- `@DefaultUserID`

**Parâmetros Corretos (Versão ITIL):**
- `@CompanyID`
- `@UserID`
- `@ExternalCardID`
- `@Title`
- `@Description`
- `@ColumnName`
- `@Priority`
- `@Deadline`
- `@StartDate`
- `@CompletedDate`
- `@LastComment`
- `@Size`

---

## ✅ Solução Implementada

### **1. Correção da Chamada da SP**

**Arquivo:** `backend/app/api/v1/kanban.py` (linhas 1881-1912)

**ANTES:**
```python
EXEC [core].[sp_UpsertCardFromImport]
    @ExternalCardID = :external_card_id,
    @Title = :title,
    @OwnerName = :owner_name,
    @Deadline = :deadline,
    @Priority = :priority,
    @ColumnName = :column_name,
    @Description = :description,
    @ActualEndDate = :actual_end_date,
    @LastEndDate = :last_end_date,
    @LastStartDate = :last_start_date,
    @PlannedStart = :planned_start,
    @CardURL = :card_url,
    @LastComment = :last_comment,
    @CompanyID = :company_id,
    @DefaultUserID = :user_id
```

**DEPOIS:**
```python
EXEC [core].[UpsertCardFromImport]
    @CompanyID = :company_id,
    @UserID = :user_id,
    @ExternalCardID = :external_card_id,
    @Title = :title,
    @Description = :description,
    @ColumnName = :column_name,
    @Priority = :priority,
    @Deadline = :deadline,
    @StartDate = :start_date,
    @CompletedDate = :completed_date,
    @LastComment = :last_comment,
    @Size = :size
```

### **2. Mapeamento de Dados**

**Conversões aplicadas:**
```python
{
    "company_id": current_user.company_id,
    "user_id": current_user.id,
    "external_card_id": external_card_id,
    "title": title,
    "description": description,
    "column_name": column_name,
    "priority": priority,
    "deadline": deadline if deadline else None,
    "start_date": last_start_date if last_start_date else planned_start,  # Prioriza last_start_date
    "completed_date": actual_end_date if actual_end_date else last_end_date,  # Prioriza actual_end_date
    "last_comment": last_comment,  # ✅ COLUNA Q - Classificação ITIL
    "size": None  # Pode ser extraído depois se necessário
}
```

### **3. Correção da Leitura do Resultado**

**ANTES:**
```python
sp_result = result.fetchone()
if sp_result:
    action = sp_result[1]  # 'CREATED' ou 'UPDATED'
    if action == 'CREATED':
        created += 1
    elif action == 'UPDATED':
        updated += 1
```

**DEPOIS:**
```python
sp_result = result.fetchone()
if sp_result and sp_result[0]:
    card_id = sp_result[0]  # SP retorna apenas CardID
    print(f"✅ Card processado: ID={card_id}")
    processed += 1
    created += 1  # Simplificado - SP faz upsert
else:
    print("⚠️ SP não retornou CardID")
    errors += 1
```

---

## 🔍 Como a Classificação ITIL Funciona

### **Fluxo de Dados:**

1. **Importação XLSX**
   - Coluna Q (`last_comment`) é lida do arquivo
   - Enviada para SP como `@LastComment`

2. **Stored Procedure** (`core.UpsertCardFromImport`)
   - Concatena: `Title + Description + LastComment`
   - Aplica regras de classificação via LIKE:
     ```sql
     DECLARE @TextBlob NVARCHAR(MAX) = CONCAT(
         ISNULL(@Title, ''), ' ',
         ISNULL(@Description, ''), ' ',
         ISNULL(@LastComment, '')
     );
     
     DECLARE @ITILCategory VARCHAR(30) =
         CASE
             WHEN @TextBlob LIKE '%GMUD%' OR @TextBlob LIKE '%RDM%' 
                  OR @TextBlob LIKE '%CHG%' OR @TextBlob LIKE '%Deploy%' 
                  OR @TextBlob LIKE '%Janela%' OR @TextBlob LIKE '%CAB%' 
                  THEN 'Change'
             WHEN @TextBlob LIKE '%Falha%' OR @TextBlob LIKE '%Erro%' 
                  OR @TextBlob LIKE '%Incidente%' OR @TextBlob LIKE '%Indisponibilidade%' 
                  THEN 'Incident'
             WHEN @TextBlob LIKE '%Solicitar%' OR @TextBlob LIKE '%Criar grupo%' 
                  OR @TextBlob LIKE '%Permiss%' OR @TextBlob LIKE '%Acesso%' 
                  THEN 'Service Request'
             ELSE 'Operation Task'
         END;
     ```

3. **Metadados ITIL Calculados:**
   ```sql
   @HasWindow = CASE WHEN @TextBlob LIKE '%Janela%' OR @TextBlob LIKE '%window%' THEN 1 ELSE 0 END
   @HasCAB = CASE WHEN @TextBlob LIKE '%CAB%' OR @TextBlob LIKE '%Comitê%' THEN 1 ELSE 0 END
   @HasBackout = CASE WHEN @TextBlob LIKE '%backout%' OR @TextBlob LIKE '%rollback%' THEN 1 ELSE 0 END
   ```

4. **Nível de Risco:**
   ```sql
   @RiskLevel =
       CASE
           WHEN @ITILCategory = 'Change' AND @HasCAB = 1 AND @HasBackout = 1 THEN 'Low'
           WHEN @ITILCategory = 'Change' AND (@HasCAB = 0 OR @HasBackout = 0) THEN 'High'
           WHEN @ITILCategory = 'Incident' THEN 'High'
           ELSE 'Low'
       END
   ```

5. **Armazenamento:**
   - Campos salvos em `core.Cards`:
     - `ITILCategory`
     - `HasWindow`
     - `HasCAB`
     - `HasBackout`
     - `Size`
     - `RiskLevel`

---

## 📊 Estrutura do Arquivo XLSX

### **Colunas Mapeadas:**

| Índice | Nome | Parâmetro SP | Observação |
|--------|------|--------------|------------|
| 0 | Card ID | `@ExternalCardID` | Identificador único |
| 3 | Title | `@Title` | Título do card |
| 4 | Owner | - | Não usado na SP atual |
| 5 | Deadline | `@Deadline` | Data limite |
| 6 | Priority | `@Priority` | High/Average/Low |
| 7 | Column | `@ColumnName` | Nome da coluna |
| 10 | Description | `@Description` | Descrição completa |
| 12 | Actual End Date | `@CompletedDate` | Data real de conclusão |
| 13 | Last End Date | `@CompletedDate` (fallback) | Alternativa |
| 14 | Last Start Date | `@StartDate` | Data de início |
| 15 | Planned Start | `@StartDate` (fallback) | Alternativa |
| 16 | Card URL | - | Não usado na SP atual |
| **17** | **Last Comment** | **`@LastComment`** | **🔑 COLUNA Q - ITIL** |

---

## 🧪 Como Testar

### **1. Preparar Arquivo XLSX**

Adicionar dados na **Coluna Q (Last Comment)** com palavras-chave ITIL:

**Exemplos:**

| Card ID | Title | Last Comment | Categoria Esperada |
|---------|-------|--------------|-------------------|
| 1001 | Atualização | Deploy GMUD com Janela e CAB | Change |
| 1002 | Problema | Falha no servidor de produção | Incident |
| 1003 | Acesso | Solicitar permissão de acesso | Service Request |
| 1004 | Manutenção | Backup rotineiro | Operation Task |

### **2. Executar Importação**

```bash
# Iniciar backend
cd backend
python3 -m uvicorn app.main:app --reload

# Acessar Swagger
http://localhost:8000/docs

# Endpoint: POST /api/v1/kanban/import-bm-xlsx
# Upload: arquivo.xlsx
```

### **3. Validar no Banco**

```sql
-- Verificar classificação ITIL
SELECT 
    ExternalCardID,
    Title,
    ITILCategory,
    HasWindow,
    HasCAB,
    HasBackout,
    RiskLevel,
    Size
FROM core.Cards
WHERE CompanyID = 1
ORDER BY CreatedAt DESC;

-- Verificar view de relatório
SELECT * FROM analytics.vw_ITILReport
WHERE CompanyID = 1;
```

### **4. Validar no Frontend**

```
http://localhost:3000/admin/kanban/analytics
→ Aba "Relatório ITIL"
```

**Verificar:**
- ✅ Cards aparecem na tabela
- ✅ Categoria ITIL correta
- ✅ Badges de metadados (Janela, CAB, Backout)
- ✅ Nível de risco correto
- ✅ Gráficos atualizados

---

## 📝 Checklist de Validação

- [x] Parâmetros da SP corrigidos
- [x] Mapeamento de dados ajustado
- [x] Leitura do resultado corrigida
- [x] Coluna Q (LastComment) sendo enviada
- [x] Documentação atualizada
- [ ] Teste com arquivo XLSX real
- [ ] Validação no banco de dados
- [ ] Validação no frontend

---

## 🚀 Próximos Passos

1. **Testar importação** com arquivo XLSX real
2. **Validar classificação** no banco de dados
3. **Verificar relatórios** no frontend
4. **Ajustar regras ITIL** se necessário (adicionar mais palavras-chave)
5. **Documentar palavras-chave** ITIL para usuários finais

---

## 📚 Arquivos Relacionados

- **Backend:** `backend/app/api/v1/kanban.py` (linhas 1800-1950)
- **Stored Procedure:** `Database/071_Update_SP_UpsertCardFromImport_ITIL.sql`
- **View:** `Database/070_Create_View_ITILReport.sql`
- **Documentação:** `docs/CLASSIFICACAO_ITIL_KANBAN.md`

---

**Status:** ✅ Correção implementada - Pronta para testes
