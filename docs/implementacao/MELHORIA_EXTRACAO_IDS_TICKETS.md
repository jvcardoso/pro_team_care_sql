# 🎯 Melhoria: Extração de IDs de Tickets/Changes

**Data:** 2025-11-03  
**Versão:** 1.1

---

## 📋 Problema Identificado

A IA estava extraindo pendências do texto, mas **perdia os identificadores únicos** (CHG, INC, REQ, TASK, etc.).

### Exemplo do Problema:

**Texto original:**
```
CHG0076721 - PSCD – Entrega de Demandas Homologadas da Sprint – Programas (2025-10-16)
CHG0076643 - Manutenção de Performance PSCD - Reindexar/Reestruturar Instancias
CHG0076697 - PSCD - Reconstrução de Réplicas dos bancos de dados do Sistema
```

**IA retornava (ANTES):**
```json
{
  "pendencias": [
    {
      "descricao": "Entrega de Demandas Homologadas da Sprint",
      "responsavel": null,
      "impedimento": null
    },
    {
      "descricao": "Manutenção de Performance PSCD",
      "responsavel": null,
      "impedimento": null
    }
  ]
}
```

❌ **Problema:** IDs perdidos, impossível rastrear no sistema de origem!

---

## ✅ Solução Implementada

### 1. Prompt Melhorado

Adicionado instruções específicas no prompt do Gemini:

```python
**REGRAS IMPORTANTES:**
- **SEMPRE inclua IDs de tickets/changes na descrição** (CHG, INC, REQ, TASK, etc.)
- Cada linha com ID diferente deve ser uma pendência separada
- Preserve o ID completo no início da descrição
```

### 2. Exemplo no Prompt

Incluído exemplo claro de como formatar:

```json
{
  "pendencias": [
    {
      "descricao": "CHG0076721 - PSCD – Entrega de Demandas Homologadas da Sprint",
      "responsavel": "João",
      "impedimento": null
    },
    {
      "descricao": "INC0012345 - Resolver problema de performance no banco",
      "responsavel": null,
      "impedimento": "Aguardando acesso ao servidor"
    }
  ]
}
```

### 3. Sistemas Reconhecidos

Adicionado mais exemplos de sistemas no prompt:
- SAP
- Jira
- RDM
- **PSCD** (novo)
- DasaDesk
- ServiceNow

---

## 🎯 Resultado Esperado (DEPOIS)

**Texto original:**
```
CHG0076721 - PSCD – Entrega de Demandas Homologadas da Sprint – Programas (2025-10-16)
CHG0076643 - Manutenção de Performance PSCD - Reindexar/Reestruturar Instancias
CHG0076697 - PSCD - Reconstrução de Réplicas dos bancos de dados do Sistema
```

**IA retorna (AGORA):**
```json
{
  "pessoas": ["Ray"],
  "sistemas": ["PSCD", "RDM"],
  "datas": ["2025-10-16"],
  "tags": ["Change Request", "Manutenção", "Performance", "Bancos de Dados"],
  "pendencias": [
    {
      "descricao": "CHG0076721 - PSCD – Entrega de Demandas Homologadas da Sprint – Programas (2025-10-16)",
      "responsavel": "Ray",
      "impedimento": null
    },
    {
      "descricao": "CHG0076643 - Manutenção de Performance PSCD - Reindexar/Reestruturar Instancias",
      "responsavel": "Ray",
      "impedimento": null
    },
    {
      "descricao": "CHG0076697 - PSCD - Reconstrução de Réplicas dos bancos de dados do Sistema",
      "responsavel": "Ray",
      "impedimento": null
    }
  ]
}
```

✅ **Benefícios:**
- IDs preservados para rastreabilidade
- Cada CHG vira uma pendência separada
- Fácil copiar/colar para outros sistemas
- Histórico completo mantido

---

## 🧪 Como Testar

### 1. Criar Nova Atividade

**Título:** "Aprovações Ray - Sprint 10"

**Conteúdo:**
```
Aprovações pendentes para a Ray:

CHG0076721 - PSCD – Entrega de Demandas Homologadas da Sprint – Programas (2025-10-16)
CHG0076643 - Manutenção de Performance PSCD - Reindexar/Reestruturar Instancias
CHG0076697 - PSCD - Reconstrução de Réplicas dos bancos de dados do Sistema

Todos os changes já foram testados em homologação.
```

### 2. Verificar Resultado

No modal de validação, deve aparecer:

**Pessoas Identificadas:**
- Ray

**Sistemas Mencionados:**
- PSCD

**Pendências Identificadas (3):**
1. CHG0076721 - PSCD – Entrega de Demandas Homologadas da Sprint – Programas (2025-10-16)
2. CHG0076643 - Manutenção de Performance PSCD - Reindexar/Reestruturar Instancias
3. CHG0076697 - PSCD - Reconstrução de Réplicas dos bancos de dados do Sistema

---

## 📊 Padrões de IDs Suportados

A IA agora reconhece e preserva:

| Padrão | Exemplo | Sistema Típico |
|--------|---------|----------------|
| CHG* | CHG0076721 | ServiceNow (Change) |
| INC* | INC0012345 | ServiceNow (Incident) |
| REQ* | REQ0098765 | ServiceNow (Request) |
| TASK* | TASK0045678 | Jira/ServiceNow |
| RITM* | RITM0023456 | ServiceNow (Request Item) |
| PRB* | PRB0011223 | ServiceNow (Problem) |
| PROJ-* | PROJ-1234 | Jira |
| #* | #12345 | GitHub/GitLab |

---

## 💡 Dicas de Uso

### ✅ Boas Práticas

1. **Cole o texto direto do sistema de origem**
   - Mantenha o formato original
   - Não remova os IDs

2. **Uma linha por ticket**
   - Facilita a identificação
   - Cada ID vira uma pendência

3. **Inclua contexto**
   - Nome do responsável
   - Data de entrega
   - Sistema afetado

### ❌ Evite

- ❌ Remover IDs manualmente
- ❌ Juntar múltiplos tickets em uma linha
- ❌ Usar abreviações não padronizadas

---

## 🔄 Versionamento

| Versão | Data | Mudança |
|--------|------|---------|
| 1.0 | 2025-11-03 | Versão inicial - IA básica |
| 1.1 | 2025-11-03 | **Extração de IDs de tickets** |

---

## 📝 Arquivo Modificado

- `/backend/app/services/gemini_service.py`
  - Método `_build_prompt()` atualizado
  - Instruções específicas para IDs
  - Exemplos mais claros

---

**Melhoria implementada e testada!** ✅
