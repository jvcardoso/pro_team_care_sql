# ✅ Correção: CSV com Campos Multilinha

## 🎯 Problema Identificado

### **Resultado da Importação:**
```json
{
  "total": 99,
  "processed": 1,
  "created": 1,
  "updated": 0,
  "errors": 98
}
```

**Apenas 1 de 99 cards foi importado!**

---

## 🔍 Causa Raiz

### **CSV com Descrições Multilinha:**

```csv
Card ID;Title;Description;...
337860;[GMUD] - Deploy;Demandas em Pronto;...
336695;[PSCD] - Workflow;"Objetivo: Solicitar criação
                        
Criação do grupo para o portal";...  ❌ QUEBRA AQUI
```

**Problema:**
- Campo `Description` contém quebras de linha
- Parser CSV padrão interpreta como múltiplas linhas
- Linha 3 é lida como 3 linhas separadas
- Validação `len(row) < 17` falha
- 98 linhas são rejeitadas

---

## 🔧 Solução Implementada

### **Parser CSV com Suporte a Multilinha:**

**Antes:**
```python
# ❌ Parser simples - não suporta multilinha
csv_reader = csv.reader(io.StringIO(decoded), delimiter=';')
```

**Depois:**
```python
# ✅ Parser com quoting - suporta multilinha
csv_reader = csv.reader(
    io.StringIO(decoded), 
    delimiter=';',
    quotechar='"',              # Campos entre aspas
    quoting=csv.QUOTE_MINIMAL,  # Apenas campos com caracteres especiais
    skipinitialspace=True       # Remove espaços após delimitador
)
```

---

## 📊 Como Funciona

### **CSV com Aspas:**
```csv
Card ID;Title;Description
337860;"[GMUD]";"Linha 1
Linha 2
Linha 3"
```

**Parser lê como:**
```python
row = ['337860', '[GMUD]', 'Linha 1\nLinha 2\nLinha 3']
# ✅ 3 colunas (correto)
```

### **CSV sem Aspas (problema original):**
```csv
Card ID;Title;Description
337860;[GMUD];Linha 1
Linha 2
Linha 3
```

**Parser lê como:**
```python
row1 = ['337860', '[GMUD]', 'Linha 1']  # 3 colunas
row2 = ['Linha 2']                       # 1 coluna ❌
row3 = ['Linha 3']                       # 1 coluna ❌
```

---

## ⚠️ Limitação Atual

### **BusinessMap não exporta com aspas:**

O CSV exportado do BusinessMap não coloca aspas nos campos multilinha:

```csv
336695;[PSCD] - Workflow;Objetivo: Solicitar criação

Criação do grupo para o portal;...
```

**Resultado:**
- Parser ainda vai falhar
- Campos multilinha sem aspas não são suportados

---

## 🎯 Soluções Possíveis

### **Opção 1: Pré-processar CSV (Recomendado)**

Adicionar aspas nos campos antes de processar:

```python
def preprocess_csv(content: str) -> str:
    """Adiciona aspas em campos que contêm quebras de linha"""
    lines = content.split('\n')
    processed = []
    
    for line in lines:
        # Se linha não tem número correto de delimitadores
        if line.count(';') < 17:
            # Juntar com linha anterior
            if processed:
                processed[-1] += '\n' + line
        else:
            processed.append(line)
    
    return '\n'.join(processed)
```

### **Opção 2: Parser Customizado**

Implementar parser que detecta linhas incompletas:

```python
def parse_multiline_csv(content: str, delimiter: str = ';') -> list:
    """Parser customizado para CSV multilinha"""
    lines = content.split('\n')
    rows = []
    current_row = []
    expected_columns = None
    
    for line in lines:
        parts = line.split(delimiter)
        
        if expected_columns is None:
            # Primeira linha = cabeçalho
            expected_columns = len(parts)
            rows.append(parts)
        elif len(parts) == expected_columns:
            # Linha completa
            if current_row:
                rows.append(current_row)
            current_row = parts
        else:
            # Linha incompleta - parte de campo multilinha
            if current_row:
                # Adicionar à última coluna da linha anterior
                current_row[-1] += '\n' + line
    
    if current_row:
        rows.append(current_row)
    
    return rows
```

### **Opção 3: Exportar CSV Corrigido**

Pedir para exportar CSV com aspas no BusinessMap:

```
Settings → Export → Quote all fields: ✓
```

---

## 🚀 Implementação Recomendada

### **Adicionar Pré-processamento:**

```python
@router.post("/import-bm")
async def import_businessmap_csv(...):
    # Ler arquivo
    contents = await file.read()
    decoded = contents.decode('utf-8')
    
    # PRÉ-PROCESSAR: Juntar linhas incompletas
    decoded = preprocess_multiline_csv(decoded)
    
    # Processar normalmente
    csv_reader = csv.reader(io.StringIO(decoded), delimiter=';')
    ...
```

**Função de pré-processamento:**

```python
def preprocess_multiline_csv(content: str, expected_columns: int = 18) -> str:
    """
    Junta linhas que fazem parte de campos multilinha.
    
    Detecta linhas com menos delimitadores que o esperado
    e as junta com a linha anterior.
    """
    lines = content.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        delimiter_count = line.count(';')
        
        if i == 0:
            # Cabeçalho - sempre adicionar
            processed_lines.append(line)
        elif delimiter_count >= expected_columns - 1:
            # Linha completa
            processed_lines.append(line)
        else:
            # Linha incompleta - juntar com anterior
            if processed_lines:
                processed_lines[-1] += ' ' + line.strip()
    
    return '\n'.join(processed_lines)
```

---

## 🧪 Teste

### **Antes da Correção:**
```
Total: 99
Processados: 1
Criados: 1
Erros: 98
```

### **Depois da Correção (Esperado):**
```
Total: 99
Processados: 99
Criados: 99
Erros: 0
```

---

## 📁 Arquivo Modificado

```
✅ backend/app/api/v1/kanban.py
   - Parser CSV com quoting
   - Suporte a campos entre aspas
   - (Ainda precisa pré-processamento)
```

---

## ✅ Próximos Passos

1. **Implementar pré-processamento** de linhas incompletas
2. **Testar com CSV real** do BusinessMap
3. **Validar 99/99 cards** importados
4. **Documentar** limitações conhecidas

---

**Data:** 2025-11-05 15:04  
**Status:** ⚠️ PARCIALMENTE CORRIGIDO  
**Pendente:** Pré-processamento de multilinha  
**Taxa de Sucesso:** 1/99 (1%)
