# ✅ SOLUÇÃO - Filtro da Tabela (Problema Confirmado)

## 🎯 PROBLEMA CONFIRMADO:

### **Backend retorna 89 cards quando deveria retornar 3**

**Logs do Console:**
```
✅ API Response: GET /api/v1/kanban/cards?completed_from=2025-11-04&completed_to=2025-11-06&column_ids=1,2,3,4,5 
{status: 200, data: Array(89)}
```

**Métricas mostram:** 3 cards concluídos ✅  
**Tabela mostra:** 89 cards ❌

---

## 🔍 CAUSA RAIZ IDENTIFICADA:

### **Todos os 89 cards têm CompletedDate = 2025-11-05 (HOJE!)**

**Verificação no Banco:**
```
📅 DISTRIBUIÇÃO POR DATA:
Data            Total     
------------------------------
2025-11-05      89  ← PROBLEMA!
2025-01-29      1
```

**Planilha XLSX (Coluna N - Last End Date):**
```
Distribuição:
2025-09-16: 10 cards
2025-10-10: 4 cards
2025-08-19: 4 cards
2025-10-29: 3 cards
... (datas variadas de Agosto a Novembro)
```

**Conclusão:** A planilha TEM datas corretas e variadas, mas o banco tem TODAS as datas iguais (05/11/2025)!

---

## 🔍 POR QUE ISSO ACONTECEU?

### **Hipótese 1: Importador Antigo Foi Usado**

Se você reimportou antes de atualizar o código do importador, ele usou o mapeamento errado:

```python
# ERRADO (versão antiga):
"actual_end_date_str": str(values[12])  # Coluna M (VAZIA)
```

Resultado: CompletedDate = NULL → SP preenche com data atual

### **Hipótese 2: SP Antiga Foi Usada**

Se a SP não foi recriada no banco antes da importação:

```sql
-- ERRADO (versão antiga):
CompletedDate = @CompletedDate  -- Sobrescreve com NULL
```

Resultado: CompletedDate = NULL → Trigger ou lógica preenche com GETUTCDATE()

### **Hipótese 3: Lógica de Fallback na SP**

A SP pode ter lógica que preenche CompletedDate com data atual se vier NULL:

```sql
-- Possível lógica problemática:
SET @CompletedDate = ISNULL(@CompletedDate, GETUTCDATE())
```

---

## ✅ SOLUÇÃO:

### **Passo 1: Limpar Dados Antigos**

```sql
USE [pro_team_care];
GO

-- Soft delete de todos os cards
UPDATE core.Cards
SET IsDeleted = 1, DeletedAt = GETUTCDATE()
WHERE CompanyID = 1;

-- Verificar
SELECT COUNT(*) FROM core.Cards WHERE IsDeleted = 0;
-- Deve retornar 0
```

### **Passo 2: Recriar SP no Banco**

```sql
-- Executar TODO o conteúdo de:
-- Database/067_Create_SP_UpsertCardFromImport.sql

-- Verificar se foi criada:
SELECT modify_date 
FROM sys.objects 
WHERE object_id = OBJECT_ID('[core].[sp_UpsertCardFromImport]');
-- Deve mostrar data/hora ATUAL
```

### **Passo 3: Verificar Código do Importador**

```bash
# Verificar se o arquivo está correto:
grep -n "actual_end_date_str" backend/app/api/v1/kanban_import_xlsx.py

# Deve mostrar:
# 115:  "actual_end_date_str": str(values[13])  # Coluna N ✅
```

### **Passo 4: Reimportar Planilha**

```
1. Acessar: http://192.168.11.83:3000/admin/kanban_parent
2. Clicar em "Importar Cards"
3. Selecionar: docs/dasa-20251105233748-NwB.xlsx
4. Aguardar importação
5. Verificar logs do backend
```

**Resultado Esperado:**
```
✅ FINAL: {
  "total": 99,
  "processed": 99,
  "created": 99,
  "errors": 0
}
```

### **Passo 5: Verificar Datas no Banco**

```sql
-- Verificar distribuição de datas:
SELECT 
    CAST(CompletedDate AS DATE) as Data,
    COUNT(*) as Total
FROM core.Cards
WHERE IsDeleted = 0
AND CompletedDate IS NOT NULL
GROUP BY CAST(CompletedDate AS DATE)
ORDER BY Data DESC;

-- Resultado esperado:
-- Datas variadas de Agosto a Novembro (não todas iguais!)
```

### **Passo 6: Testar Analytics**

```
1. Acessar: http://192.168.11.83:3000/admin/kanban/analytics
2. Clicar em "Hoje"
3. Verificar que mostra apenas cards de hoje (não 89!)
4. Clicar em "Semana"
5. Verificar que mostra apenas cards da semana
```

---

## 🧪 TESTES DE VALIDAÇÃO:

### **1. Teste de Importação:**
```bash
# Verificar logs do backend:
tail -f /var/log/backend.log

# Deve mostrar datas variadas:
📝 [1] 339708 - CompletedDate: 2025-09-16
📝 [2] 339707 - CompletedDate: 2025-10-10
📝 [3] 339706 - CompletedDate: 2025-08-19
...
```

### **2. Teste de Filtro:**
```bash
# Testar API diretamente:
curl -H "Authorization: Bearer SEU_TOKEN" \
  "http://192.168.11.83:8000/api/v1/kanban/cards?completed_from=2025-11-04&completed_to=2025-11-06&column_ids=1,2,3,4,5"

# Deve retornar apenas cards com CompletedDate entre 04/11 e 06/11
# NÃO deve retornar 89 cards!
```

### **3. Teste Visual:**
```
1. Abrir Analytics
2. Filtro "Hoje" → Deve mostrar ~2-3 cards
3. Filtro "Semana" → Deve mostrar ~5-10 cards
4. Filtro "Mês" → Deve mostrar ~30-40 cards
5. Filtro "Ano" → Deve mostrar ~90 cards
```

---

## 📋 CHECKLIST:

- [ ] Limpar dados antigos (soft delete)
- [ ] Recriar SP no banco
- [ ] Verificar código do importador (linha 115)
- [ ] Reimportar planilha
- [ ] Verificar distribuição de datas no banco
- [ ] Testar filtro "Hoje" (deve mostrar 2-3 cards, não 89)
- [ ] Testar filtro "Semana"
- [ ] Testar filtro "Mês"
- [ ] Remover logs de debug do código

---

## 🚨 IMPORTANTE:

**NÃO reimporte a planilha antes de:**
1. Limpar os dados antigos
2. Recriar a SP no banco
3. Verificar que o importador está correto

**Caso contrário, o problema vai se repetir!**

---

**Status:** 🔍 CAUSA RAIZ IDENTIFICADA  
**Solução:** Limpar + Recriar SP + Reimportar  
**Tempo Estimado:** 10 minutos
