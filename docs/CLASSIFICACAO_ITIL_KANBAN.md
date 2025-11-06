# 📊 Classificação ITIL Automática no Sistema Kanban

**Versão:** 1.0  
**Data:** 06/11/2025  
**Autor:** Sistema Pro Team Care  
**Status:** 📋 Planejamento

---

## 🎯 Objetivo

Implementar classificação automática de cards do Kanban segundo categorias ITIL 4, enriquecendo os dados no momento da importação do Businessmap para facilitar geração de relatórios executivos e auditorias.

---

## 📋 Categorias ITIL

| Categoria | Descrição | Palavras-chave | Exemplo |
|-----------|-----------|----------------|---------|
| **Change** | Mudanças planejadas (GMUD/RDM) | GMUD, RDM, CHG, Deploy, Janela, CAB | [PSCD] Deploy Programas Sprint 45 |
| **Incident** | Falhas não planejadas | Falha, Erro, Incidente, Indisponibilidade | Falha envio e-mails SMTP |
| **Service Request** | Solicitações padrão | Solicitar, Criar grupo, Permissão, Acesso | Criar grupo AD projeto |
| **Operation Task** | Manutenções operacionais | (padrão) | Manutenção preventiva BD |

---

## 🗂️ Estrutura de Dados

### **Campos Novos em `core.Cards`**

```sql
ALTER TABLE core.Cards ADD ITILCategory VARCHAR(30) NULL;
ALTER TABLE core.Cards ADD HasWindow BIT DEFAULT 0;
ALTER TABLE core.Cards ADD HasCAB BIT DEFAULT 0;
ALTER TABLE core.Cards ADD HasBackout BIT DEFAULT 0;
ALTER TABLE core.Cards ADD Size VARCHAR(20) NULL;
ALTER TABLE core.Cards ADD RiskLevel VARCHAR(20) NULL;
```

| Campo | Tipo | Valores | Descrição |
|-------|------|---------|-----------|
| `ITILCategory` | VARCHAR(30) | Change, Incident, Service Request, Operation Task | Categoria ITIL |
| `HasWindow` | BIT | 0/1 | Tem janela de manutenção |
| `HasCAB` | BIT | 0/1 | Passou por CAB |
| `HasBackout` | BIT | 0/1 | Tem plano de backout |
| `Size` | VARCHAR(20) | XS, S, M, L, XL | Tamanho estimado |
| `RiskLevel` | VARCHAR(20) | Low, Medium, High | Nível de risco |

---

## 📥 Mapeamento Businessmap → Banco

| Campo BM | Coluna | Índice | Campo Banco | Uso |
|----------|--------|--------|-------------|-----|
| Title | D | 3 | Title | ✅ Classificação |
| Description | K | 10 | Description | ✅ Classificação |
| Last Comment | Q | 16 | OriginalText | ✅ Classificação |
| Last End Date | N | 13 | CompletedDate | Data conclusão |
| Last Start Date | O | 14 | StartDate | Início trabalho |
| Priority | G | 6 | Priority | High/Medium/Low |
| Column Name | H | 7 | ColumnID | Via CardColumns |

---

## 🔍 Lógica de Classificação

### **1. Concatenação**
```sql
DECLARE @TextBlob NVARCHAR(MAX) = CONCAT(
    ISNULL(@Title, ''), ' ',
    ISNULL(@Description, ''), ' ',
    ISNULL(@LastComment, '')
);
```

### **2. Classificação**
```sql
DECLARE @ITILCategory VARCHAR(30) = 
    CASE 
        WHEN @TextBlob LIKE '%GMUD%' OR @TextBlob LIKE '%RDM%' 
            THEN 'Change'
        WHEN @TextBlob LIKE '%Falha%' OR @TextBlob LIKE '%Erro%' 
            THEN 'Incident'
        WHEN @TextBlob LIKE '%Solicitar%' OR @TextBlob LIKE '%Acesso%' 
            THEN 'Service Request'
        ELSE 'Operation Task'
    END;
```

### **3. Metadados**
```sql
DECLARE @HasWindow BIT = CASE WHEN @TextBlob LIKE '%Janela%' THEN 1 ELSE 0 END;
DECLARE @HasCAB BIT = CASE WHEN @TextBlob LIKE '%CAB%' THEN 1 ELSE 0 END;
DECLARE @HasBackout BIT = CASE WHEN @TextBlob LIKE '%backout%' THEN 1 ELSE 0 END;
```

### **4. Nível de Risco**
```sql
DECLARE @RiskLevel VARCHAR(20) = 
    CASE 
        WHEN @ITILCategory = 'Change' AND @HasCAB = 1 AND @HasBackout = 1 
            THEN 'Low'
        WHEN @ITILCategory = 'Change' AND (@HasCAB = 0 OR @HasBackout = 0) 
            THEN 'High'
        WHEN @ITILCategory = 'Incident' 
            THEN 'High'
        ELSE 'Low'
    END;
```

---

## 🔧 Implementação

### **Fase 1: Banco (30 min)**
1. Executar `Database/069_Add_ITIL_Classification_Columns.sql`
2. Executar `Database/070_Create_View_ITILReport.sql`
3. Executar `Database/071_Update_SP_UpsertCardFromImport_ITIL.sql`

### **Fase 2: Backend (1h)**
1. Modificar `import_businessmap_xlsx` para passar `last_comment`
2. Criar endpoint `/analytics/itil-summary`
3. Criar endpoint `/analytics/itil-cards`

### **Fase 3: Frontend (1h)**
1. Adicionar aba "Relatório ITIL" em `KanbanAnalyticsPage.jsx`
2. Criar componente `ITILSummaryChart`
3. Criar componente `ITILCardsTable`

### **Fase 4: Testes (30 min)**
1. Reimportar planilha e verificar classificação
2. Testar endpoints no Swagger
3. Validar relatório no frontend

---

## 📊 Relatório Gerado

### **Métricas por Categoria**
- Total de cards
- Tempo médio de ciclo
- SLA Compliance (%)
- Cards de alto risco
- Cards com janela/CAB/backout

### **Detalhamento**
- Lista de cards por categoria
- Filtros por período e tipo
- Exportação para PDF/Excel

---

## 🎯 Benefícios

✅ **Classificação automática** - Sem intervenção manual  
✅ **Rastreabilidade** - Metadados de Change (CAB, janela, backout)  
✅ **Auditoria** - Relatórios alinhados ITIL 4  
✅ **Gestão de risco** - Identificação automática de alto risco  
✅ **Métricas** - SLA, Lead Time, Cycle Time por categoria

---

## 📝 Próximos Passos

1. ✅ Documentação criada
2. ⏳ Criar scripts SQL (Fase 1)
3. ⏳ Atualizar backend (Fase 2)
4. ⏳ Atualizar frontend (Fase 3)
5. ⏳ Testes e validação (Fase 4)

---

**Documentos Relacionados:**
- `Database/069_Add_ITIL_Classification_Columns.sql` (a criar)
- `Database/070_Create_View_ITILReport.sql` (a criar)
- `Database/071_Update_SP_UpsertCardFromImport_ITIL.sql` (a criar)
