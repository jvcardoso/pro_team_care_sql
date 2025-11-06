# 🏷️ GUIA: Como Alimentar Metadados ITIL

## 🎯 Como Funciona Hoje

Os metadados ITIL são **classificados automaticamente** durante a importação XLSX baseada em palavras-chave encontradas no texto dos cards.

## 📊 Metadados Atuais

### 🪟 **HasWindow (Janela de Manutenção)**
**Detectado quando contém:**
- `Janela` (português)
- `window` (inglês)

**Exemplos que funcionam:**
```
✅ "Deploy com Janela de 22h às 23h"
✅ "Manutenção window 18:00-20:00"
❌ "Janelas do sistema" (não é janela de manutenção)
```

### 👥 **HasCAB (Change Advisory Board)**
**Detectado quando contém:**
- `CAB`
- `Comitê`

**Exemplos que funcionam:**
```
✅ "Aprovado pelo CAB"
✅ "Reunião do Comitê de Mudanças"
❌ "Cabeamento de rede" (não é CAB)
```

### 🔄 **HasBackout (Plano de Reversão)**
**Detectado quando contém:**
- `backout`
- `rollback`

**Exemplos que funcionam:**
```
✅ "Plano de backout preparado"
✅ "Rollback automático implementado"
❌ "Backup concluído" (não é backout)
```

## 💡 Como Melhorar a Detecção

### 📝 **1. Use Termos Específicos nos Títulos**
```bash
# ❌ Ruim
"Deploy versão 191"

# ✅ Bom
"[GMUD] Deploy versão 191 - Janela 22h-23h com CAB aprovado"
```

### 📋 **2. Inclua no Campo "Last Comment" do XLSX**
O sistema analisa: **Título + Descrição + Last Comment**

```
Last Comment: "Janela de manutenção: 22:00-23:00 | CAB: Aprovado | Backout: Sim"
```

### 🏷️ **3. Padrões Recomendados**
```
# Janela
"Janela: 22h-23h", "Window: 10PM-11PM", "Manutenção agendada"

# CAB
"CAB aprovado", "Comitê autorizou", "Change Board: OK"

# Backout
"Backout preparado", "Rollback plan: Yes", "Plano de reversão"
```

## 📊 Impacto nos Relatórios

### 🎯 **Relatório ITIL Atual**
```json
{
  "itilCategory": "Change",
  "withWindow": 0,    // Nenhum card detectado
  "withCAB": 0,       // Nenhum card detectado
  "withBackout": 0    // Nenhum card detectado
}
```

### 🎯 **Relatório ITIL com Metadados**
```json
{
  "itilCategory": "Change",
  "withWindow": 3,    // Cards com janela
  "withCAB": 2,       // Cards com CAB
  "withBackout": 1    // Cards com backout
}
```

## 🔧 Possíveis Melhorias Futuras

### **Opção 1: Interface Manual**
- Checkbox nos cards para marcar metadados
- Edição manual após importação

### **Opção 2: Campos Específicos no XLSX**
- Coluna "HasWindow" (S/N)
- Coluna "HasCAB" (S/N)
- Coluna "HasBackout" (S/N)

### **Opção 3: IA Melhorada**
- Análise de contexto mais inteligente
- Detecção de padrões complexos

## 📋 Checklist para Usuários

### ✅ **Para Cards de CHANGE:**
- [ ] Mencionar "Janela" se houver manutenção agendada
- [ ] Confirmar "CAB" se aprovado pelo comitê
- [ ] Descrever "backout" se plano de reversão existe

### ✅ **Exemplo Completo:**
```
Título: "[GMUD] Deploy PSCD v191 - Janela 22h-23h"

Descrição: "Deploy da versão 191 do PSCD com janela de manutenção"

Last Comment: "CAB: Aprovado em 05/11 | Backout: Plano preparado | Janela: 22:00-23:00"
```

---

**💡 Dica:** Quanto mais específicos forem os termos usados, melhor será a classificação automática!</content>
</xai:function_call">Criar guia completo sobre metadados ITIL