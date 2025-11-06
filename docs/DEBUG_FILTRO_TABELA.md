# 🔍 DEBUG - Filtro da Tabela Não Funciona

## 🎯 Problema Relatado:

**"Cards estão respeitando o filtro mas na tabela não"**

### Evidência (da imagem):
- **Métricas no topo**: "3 Cards Concluídos" ✅ (respeitando filtro 04/11 a 06/11)
- **Tabela abaixo**: "89 cards" ❌ (ignorando filtro)

---

## 🔍 Análise:

### **Dois Endpoints Diferentes:**

1. **Métricas (cards no topo):**
   ```javascript
   // Endpoint: /api/v1/kanban/analytics
   fetchAnalytics() {
     api.get(`/api/v1/kanban/analytics?start_date=${dateRange.start}&end_date=${dateRange.end}`)
   }
   ```
   ✅ **Funciona corretamente** - retorna 3 cards

2. **Tabela (lista de cards):**
   ```javascript
   // Endpoint: /api/v1/kanban/cards
   fetchCards() {
     api.get(`/api/v1/kanban/cards?completed_from=${startDate}&completed_to=${endDate}&column_ids=${columnIds}`)
   }
   ```
   ❌ **Não funciona** - retorna 89 cards

---

## 🔍 Possíveis Causas:

### **Hipótese 1: Parâmetros Incorretos**
```javascript
// CardsTable recebe props:
<CardsTable 
  startDate={dateRange.start}  // ← Correto
  endDate={dateRange.end}      // ← Correto
  ...
/>

// Mas pode estar usando valores antigos (cache)
```

### **Hipótese 2: useEffect Não Reage**
```javascript
React.useEffect(() => {
  if (selectedColumns.length > 0) {
    fetchCards();
  }
}, [startDate, endDate, selectedColumns]);  // ← Dependências corretas
```

### **Hipótese 3: Backend Não Filtra**
```python
# backend/app/api/v1/kanban.py
if completed_from and completed_to:
    query = query.where(
        and_(
            Card.CompletedDate.isnot(None),
            Card.CompletedDate >= date_from,
            Card.CompletedDate < date_to
        )
    )
```
✅ **Código está correto**

### **Hipótese 4: Cards Sem CompletedDate**
```sql
-- Se cards não têm CompletedDate, filtro não funciona
SELECT COUNT(*) FROM core.Cards WHERE CompletedDate IS NULL
```
⚠️ **PROVÁVEL CAUSA!**

---

## 🧪 Como Debugar:

### **1. Verificar Console do Navegador:**

Após adicionar logs de debug, recarregar a página e verificar:

```
🔍 TABELA fetchCards: {
  startDate: "2024-11-04",
  endDate: "2025-11-06",
  columnIds: "1,2,3,4,5",
  url: "/api/v1/kanban/cards?completed_from=2024-11-04&completed_to=2025-11-06&column_ids=1,2,3,4,5"
}
✅ TABELA resposta: 89 cards
```

**Se mostrar 89 cards:** Backend está retornando todos os cards (problema no backend)

**Se mostrar 3 cards:** Frontend está funcionando (problema de renderização)

### **2. Verificar Banco de Dados:**

```sql
-- Quantos cards têm CompletedDate?
SELECT 
    COUNT(*) as Total,
    SUM(CASE WHEN CompletedDate IS NOT NULL THEN 1 ELSE 0 END) as ComData,
    SUM(CASE WHEN CompletedDate IS NULL THEN 1 ELSE 0 END) as SemData
FROM core.Cards
WHERE IsDeleted = 0;

-- Resultado esperado:
-- Total: 100, ComData: 100, SemData: 0 ✅
-- Se SemData > 0: PROBLEMA! Cards sem CompletedDate
```

### **3. Testar API Diretamente:**

```bash
# Testar endpoint com curl:
curl -H "Authorization: Bearer SEU_TOKEN" \
  "http://192.168.11.83:8000/api/v1/kanban/cards?completed_from=2024-11-04&completed_to=2025-11-06&column_ids=1,2,3,4,5"

# Deve retornar JSON com 3 cards (não 89)
```

---

## ✅ Solução Provável:

### **Problema: Cards Sem CompletedDate**

Se a importação falhou ou foi feita antes da correção, os cards podem estar sem `CompletedDate`.

**Solução:**

```sql
-- 1. Verificar estado atual:
SELECT 
    cc.ColumnName,
    COUNT(*) as Total,
    SUM(CASE WHEN c.CompletedDate IS NOT NULL THEN 1 ELSE 0 END) as ComData
FROM core.Cards c
INNER JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
WHERE c.IsDeleted = 0
GROUP BY cc.ColumnName, cc.DisplayOrder
ORDER BY cc.DisplayOrder;

-- 2. Se "Concluído" tiver cards sem CompletedDate, corrigir:
UPDATE c
SET c.CompletedDate = COALESCE(c.StartDate, c.CreatedAt)
FROM core.Cards c
INNER JOIN core.CardColumns cc ON c.ColumnID = cc.ColumnID
WHERE c.IsDeleted = 0
AND LOWER(cc.ColumnName) LIKE '%conclu%'
AND c.CompletedDate IS NULL;
```

---

## 📋 Checklist de Verificação:

- [ ] Abrir console do navegador (F12)
- [ ] Recarregar página de analytics
- [ ] Verificar logs: `🔍 TABELA fetchCards`
- [ ] Anotar valores de `startDate`, `endDate`, `columnIds`
- [ ] Verificar quantos cards foram retornados
- [ ] Se 89 cards: Problema no backend (cards sem CompletedDate)
- [ ] Se 3 cards: Problema no frontend (renderização)
- [ ] Executar SQL de verificação no banco
- [ ] Corrigir CompletedDate se necessário
- [ ] Reimportar planilha com mapeamento correto

---

## 🎯 Próximos Passos:

1. **Verificar console do navegador** (logs de debug adicionados)
2. **Verificar banco de dados** (SQL acima)
3. **Corrigir CompletedDate** se necessário
4. **Reimportar planilha** com importador corrigido

---

**Status:** 🔍 DEBUG EM ANDAMENTO  
**Logs Adicionados:** ✅  
**Aguardando:** Verificação do console do navegador
