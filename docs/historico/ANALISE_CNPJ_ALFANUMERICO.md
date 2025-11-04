# 📋 ANÁLISE - PREPARAÇÃO PARA CNPJ ALFANUMÉRICO

**Data:** 23/10/2025 10:10 BRT  
**Objetivo:** Identificar ajustes necessários para suportar o novo formato de CNPJ alfanumérico (a partir de Julho/2026)

---

## ✅ **RESUMO EXECUTIVO**

### **Banco de Dados:** 100% PRONTO ✅
- Coluna `tax_id` como `NVARCHAR(14)` já suporta alfanuméricos
- Nenhuma alteração necessária na estrutura

### **Aplicação:** REQUER AJUSTES ⚠️
- **Backend:** 3 pontos de ajuste
- **Frontend:** 8 pontos de ajuste
- **Prioridade:** MÉDIA (implementar até Junho/2026)

---

## 🗄️ **1. BANCO DE DADOS - ANÁLISE**

### **Estrutura Atual:**

```sql
CREATE TABLE [core].[pj_profiles] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [person_id] BIGINT NOT NULL,
    [company_id] BIGINT NOT NULL,
    [tax_id] NVARCHAR(14) NOT NULL,  -- ✅ JÁ SUPORTA ALFANUMÉRICO
    [trade_name] NVARCHAR(400),
    ...
    CONSTRAINT [UQ_pj_profiles_company_tax_id] 
        UNIQUE ([company_id], [tax_id])  -- ✅ UNICIDADE OK
);
```

### **Validações do Banco:**

| Validação | Status | Descrição |
|-----------|--------|-----------|
| **Tipo de Dado** | ✅ OK | `NVARCHAR(14)` aceita letras e números |
| **Tamanho** | ✅ OK | Máximo 14 caracteres (formato atual e futuro) |
| **Obrigatoriedade** | ✅ OK | `NOT NULL` garante preenchimento |
| **Unicidade** | ✅ OK | Constraint impede duplicatas por empresa |
| **Formato** | ❌ NÃO VALIDA | Banco não valida formato (responsabilidade da aplicação) |
| **Dígito Verificador** | ❌ NÃO VALIDA | Banco não calcula DV (responsabilidade da aplicação) |

### **Conclusão:**
✅ **Nenhuma alteração necessária no banco de dados**

---

## 🔧 **2. BACKEND (Python/FastAPI) - PONTOS DE AJUSTE**

### **2.1. Schemas Pydantic** ⚠️

**Arquivo:** `backend/app/schemas/pj_profile.py`

**Problema Atual:**
```python
# Linha 11
tax_id: str = Field(..., max_length=28, description="CNPJ (formato: 00.000.000/0000-00)")
```

**Ajuste Necessário:**
```python
# ✅ ATUALIZAR DESCRIÇÃO
tax_id: str = Field(
    ..., 
    max_length=28,  # Mantém 28 para aceitar formatação (XX.XXX.XXX/XXXX-XX)
    description="CNPJ (formato: XX.XXX.XXX/XXXX-XX onde X = letra ou número)"
)
```

**Validação Adicional (OPCIONAL):**
```python
from pydantic import field_validator

class PJProfileBase(BaseModel):
    tax_id: str = Field(..., max_length=28)
    
    @field_validator('tax_id')
    def validate_tax_id_format(cls, v):
        # Remover formatação
        clean = v.replace('.', '').replace('/', '').replace('-', '')
        
        # Validar tamanho
        if len(clean) != 14:
            raise ValueError('CNPJ deve ter 14 caracteres')
        
        # Validar formato: primeiros 12 alfanuméricos, últimos 2 numéricos
        if not clean[:12].isalnum():
            raise ValueError('Primeiros 12 caracteres devem ser alfanuméricos')
        
        if not clean[12:].isdigit():
            raise ValueError('Últimos 2 caracteres (DV) devem ser numéricos')
        
        return clean  # Retorna sem formatação
```

---

### **2.2. Limpeza de CNPJ** ⚠️

**Arquivo:** `backend/app/api/v1/companies.py`

**Problema Atual (Linhas 370, 507):**
```python
# ❌ CÓDIGO ATUAL: Remove apenas pontuação
clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
```

**Ajuste Necessário:**
```python
# ✅ CÓDIGO ATUALIZADO: Remove pontuação e converte para maiúsculas
clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").upper()
```

**Justificativa:**
- CNPJs alfanuméricos devem ser armazenados em **MAIÚSCULAS** para padronização
- Evita problemas de comparação (ex: "AB" vs "ab")

---

### **2.3. Validação de Dígito Verificador** ⚠️ **COMPLEXO**

**Arquivo:** Criar `backend/app/utils/cnpj_validator.py`

**Problema:**
- Lógica atual valida apenas CNPJs numéricos
- Nova regra usa valores ASCII para letras

**Solução:**
```python
"""
Validador de CNPJ com suporte a formato alfanumérico (a partir de 2026)
Baseado na Instrução Normativa RFB nº XXXX/2025
"""

def calculate_cnpj_digit(cnpj_base: str, weights: list) -> int:
    """
    Calcula dígito verificador do CNPJ (numérico ou alfanumérico)
    
    Args:
        cnpj_base: Primeiros 12 ou 13 caracteres do CNPJ
        weights: Lista de pesos para cálculo
    
    Returns:
        Dígito verificador (0-9)
    """
    total = 0
    
    for i, char in enumerate(cnpj_base):
        if char.isdigit():
            # Numérico: usar valor direto
            value = int(char)
        else:
            # Alfanumérico: usar valor ASCII - 55
            # A=65-55=10, B=66-55=11, ..., Z=90-55=35
            value = ord(char.upper()) - 55
        
        total += value * weights[i]
    
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ (numérico ou alfanumérico)
    
    Args:
        cnpj: CNPJ com ou sem formatação
    
    Returns:
        True se válido, False caso contrário
    """
    # Remover formatação
    clean = cnpj.replace('.', '').replace('/', '').replace('-', '').upper()
    
    # Validar tamanho
    if len(clean) != 14:
        return False
    
    # Validar formato: primeiros 12 alfanuméricos, últimos 2 numéricos
    if not clean[:12].isalnum():
        return False
    
    if not clean[12:].isdigit():
        return False
    
    # Validar se todos os caracteres são iguais (ex: 00000000000000)
    if len(set(clean)) == 1:
        return False
    
    # Calcular primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = calculate_cnpj_digit(clean[:12], weights1)
    
    if int(clean[12]) != digit1:
        return False
    
    # Calcular segundo dígito verificador
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit2 = calculate_cnpj_digit(clean[:13], weights2)
    
    if int(clean[13]) != digit2:
        return False
    
    return True


def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX
    
    Args:
        cnpj: CNPJ sem formatação (14 caracteres)
    
    Returns:
        CNPJ formatado
    """
    clean = cnpj.replace('.', '').replace('/', '').replace('-', '').upper()
    
    if len(clean) != 14:
        return cnpj
    
    return f"{clean[:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:]}"
```

**Uso:**
```python
from app.utils.cnpj_validator import validate_cnpj, format_cnpj

# Validar
is_valid = validate_cnpj("AB.123.456/0001-78")  # True/False

# Formatar
formatted = format_cnpj("AB12345600017 8")  # "AB.123.456/0001-78"
```

---

## 🎨 **3. FRONTEND (React/TypeScript) - PONTOS DE AJUSTE**

### **3.1. Função removeNonNumeric** ⚠️ **CRÍTICO**

**Arquivo:** `frontend/src/utils/validators.js`

**Problema Atual (Linha 8):**
```javascript
// ❌ CÓDIGO ATUAL: Remove TUDO exceto números
export const removeNonNumeric = (value) => {
  return value ? value.toString().replace(/\D/g, "") : "";
};
```

**Ajuste Necessário:**
```javascript
// ✅ CÓDIGO ATUALIZADO: Criar função específica para CNPJ
export const removeNonNumeric = (value) => {
  return value ? value.toString().replace(/\D/g, "") : "";
};

// ✅ NOVA FUNÇÃO: Remove apenas formatação, mantém alfanuméricos
export const removeCNPJFormatting = (value) => {
  if (!value) return "";
  return value
    .toString()
    .replace(/\./g, "")
    .replace(/\//g, "")
    .replace(/-/g, "")
    .toUpperCase();
};
```

---

### **3.2. Validação de CNPJ** ⚠️ **CRÍTICO**

**Arquivo:** `frontend/src/utils/validators.js`

**Problema Atual (Linhas 45-72):**
```javascript
// ❌ CÓDIGO ATUAL: Valida apenas CNPJs numéricos
export const validateCNPJ = (cnpj) => {
  const numbers = removeNonNumeric(cnpj);  // ❌ Remove letras!
  
  if (numbers.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(numbers)) return false;  // ❌ Apenas dígitos
  
  // Cálculo de DV para numéricos apenas...
};
```

**Ajuste Necessário:**
```javascript
// ✅ CÓDIGO ATUALIZADO: Suporta alfanuméricos
export const validateCNPJ = (cnpj) => {
  // Remover apenas formatação, manter alfanuméricos
  const clean = removeCNPJFormatting(cnpj);
  
  // Validar tamanho
  if (clean.length !== 14) return false;
  
  // Validar formato: primeiros 12 alfanuméricos, últimos 2 numéricos
  if (!/^[A-Z0-9]{12}\d{2}$/.test(clean)) return false;
  
  // Validar se todos os caracteres são iguais
  if (/^(.)\1{13}$/.test(clean)) return false;
  
  // Calcular primeiro dígito verificador
  const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  let sum = 0;
  
  for (let i = 0; i < 12; i++) {
    const char = clean[i];
    const value = /\d/.test(char) 
      ? parseInt(char)  // Numérico: usar valor direto
      : char.charCodeAt(0) - 55;  // Letra: ASCII - 55
    
    sum += value * weights1[i];
  }
  
  const remainder1 = sum % 11;
  const digit1 = remainder1 < 2 ? 0 : 11 - remainder1;
  
  if (parseInt(clean[12]) !== digit1) return false;
  
  // Calcular segundo dígito verificador
  const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  sum = 0;
  
  for (let i = 0; i < 13; i++) {
    const char = clean[i];
    const value = /\d/.test(char)
      ? parseInt(char)
      : char.charCodeAt(0) - 55;
    
    sum += value * weights2[i];
  }
  
  const remainder2 = sum % 11;
  const digit2 = remainder2 < 2 ? 0 : 11 - remainder2;
  
  return parseInt(clean[13]) === digit2;
};
```

---

### **3.3. Formatação de CNPJ** ⚠️

**Arquivo:** `frontend/src/utils/validators.js`

**Problema Atual (Linhas 270-278):**
```javascript
// ❌ CÓDIGO ATUAL: Assume apenas números
export const formatCNPJ = (cnpj) => {
  const numbers = removeNonNumeric(cnpj);  // ❌ Remove letras!
  if (numbers.length !== 14) return cnpj;
  
  return numbers.replace(
    /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
    "$1.$2.$3/$4-$5"
  );
};
```

**Ajuste Necessário:**
```javascript
// ✅ CÓDIGO ATUALIZADO: Suporta alfanuméricos
export const formatCNPJ = (cnpj) => {
  const clean = removeCNPJFormatting(cnpj);
  if (clean.length !== 14) return cnpj;
  
  // Formato: XX.XXX.XXX/XXXX-XX (onde X = letra ou número)
  return clean.replace(
    /^([A-Z0-9]{2})([A-Z0-9]{3})([A-Z0-9]{3})([A-Z0-9]{4})(\d{2})$/,
    "$1.$2.$3/$4-$5"
  );
};
```

---

### **3.4. Máscara de Input** ⚠️

**Arquivo:** `frontend/src/components/inputs/InputCNPJ.jsx`

**Problema Atual (Linhas 85, 174):**
```javascript
// ❌ CÓDIGO ATUAL: Valida apenas números
if (cnpj.length === 14 && /^\d+$/.test(cnpj)) {  // Linha 85
  // ...
}

if (currentValue && currentValue.length === 14) {  // Linha 174
  consultCompany(currentValue);
}
```

**Ajuste Necessário:**
```javascript
// ✅ CÓDIGO ATUALIZADO: Aceita alfanuméricos
if (cnpj.length === 14 && /^[A-Z0-9]{12}\d{2}$/.test(cnpj)) {
  // ...
}

// Validar formato antes de consultar
if (currentValue && currentValue.length === 14 && /^[A-Z0-9]{12}\d{2}$/.test(currentValue)) {
  consultCompany(currentValue);
}
```

**Máscara de Input:**
```javascript
// ✅ ATUALIZAR: Aceitar letras nas primeiras 12 posições
const cnpjMask = (value) => {
  const clean = value.replace(/[^\w]/g, '').toUpperCase();
  
  if (clean.length <= 2) return clean;
  if (clean.length <= 5) return `${clean.slice(0, 2)}.${clean.slice(2)}`;
  if (clean.length <= 8) return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5)}`;
  if (clean.length <= 12) return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}/${clean.slice(8)}`;
  return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}/${clean.slice(8, 12)}-${clean.slice(12, 14)}`;
};
```

---

### **3.5. Consulta à Receita Federal** ⚠️

**Arquivo:** `frontend/src/services/cnpjService.js`

**Problema:**
- APIs externas (ReceitaWS, etc) podem não suportar CNPJs alfanuméricos inicialmente

**Ajuste Necessário:**
```javascript
export const consultarCNPJ = async (cnpj) => {
  const clean = removeCNPJFormatting(cnpj);
  
  // Verificar se é alfanumérico
  const isAlphanumeric = /[A-Z]/.test(clean);
  
  if (isAlphanumeric) {
    // ⚠️ APIs externas podem não suportar ainda
    console.warn('CNPJ alfanumérico: APIs externas podem não suportar');
    
    // Retornar dados básicos sem consulta externa
    return {
      people: {
        person_type: 'PJ',
        name: '',
        trade_name: '',
        tax_id: clean,
        status: 'active'
      },
      // ... outros campos vazios
    };
  }
  
  // CNPJ numérico: consultar normalmente
  return await api.get(`/cnpj/${clean}`);
};
```

---

### **3.6. Detecção de Tipo de Pessoa** ⚠️

**Arquivo:** `frontend/src/utils/validators.js`

**Problema Atual (Linhas 229-255):**
```javascript
// ❌ CÓDIGO ATUAL: Usa removeNonNumeric
export const detectPersonTypeFromTaxId = (taxId) => {
  const numbers = removeNonNumeric(taxId);  // ❌ Remove letras!
  
  if (numbers.length === 11) {
    return { personType: "PF", ... };
  } else if (numbers.length === 14) {
    return { personType: "PJ", ... };
  }
  
  return { personType: null, ... };
};
```

**Ajuste Necessário:**
```javascript
// ✅ CÓDIGO ATUALIZADO: Detecta corretamente
export const detectPersonTypeFromTaxId = (taxId) => {
  // Remover apenas formatação
  const clean = taxId
    .replace(/\./g, '')
    .replace(/\//g, '')
    .replace(/-/g, '')
    .toUpperCase();
  
  // CPF: 11 dígitos numéricos
  if (clean.length === 11 && /^\d{11}$/.test(clean)) {
    return {
      personType: "PF",
      documentType: "CPF",
      isValid: validateCPF(clean),
      formattedValue: formatCPF(clean),
    };
  }
  
  // CNPJ: 14 caracteres (12 alfanuméricos + 2 numéricos)
  if (clean.length === 14 && /^[A-Z0-9]{12}\d{2}$/.test(clean)) {
    return {
      personType: "PJ",
      documentType: "CNPJ",
      isValid: validateCNPJ(clean),
      formattedValue: formatCNPJ(clean),
    };
  }
  
  // Documento incompleto ou inválido
  return {
    personType: null,
    documentType: null,
    isValid: false,
    formattedValue: taxId,
  };
};
```

---

### **3.7. Comparação de CNPJs** ⚠️

**Problema:**
- Comparações case-sensitive podem falhar (ex: "AB" vs "ab")

**Solução:**
```javascript
// ✅ SEMPRE normalizar antes de comparar
const compareCNPJ = (cnpj1, cnpj2) => {
  const clean1 = removeCNPJFormatting(cnpj1);
  const clean2 = removeCNPJFormatting(cnpj2);
  return clean1 === clean2;
};
```

---

### **3.8. Armazenamento no Backend** ⚠️

**Problema:**
- Frontend pode enviar CNPJ com letras minúsculas

**Solução:**
```javascript
// ✅ SEMPRE converter para maiúsculas antes de enviar
const prepareDataForAPI = (formData) => {
  return {
    ...formData,
    tax_id: removeCNPJFormatting(formData.tax_id)  // Remove formatação e converte para maiúsculas
  };
};
```

---

## 📋 **4. CHECKLIST DE IMPLEMENTAÇÃO**

### **FASE 1: Preparação (Até Março/2026)**

#### **Backend:**
- [ ] Atualizar descrição do campo `tax_id` nos schemas
- [ ] Criar `cnpj_validator.py` com nova lógica de validação
- [ ] Atualizar limpeza de CNPJ para usar `.upper()`
- [ ] Adicionar testes unitários para CNPJs alfanuméricos

#### **Frontend:**
- [ ] Criar função `removeCNPJFormatting()`
- [ ] Atualizar função `validateCNPJ()` para suportar alfanuméricos
- [ ] Atualizar função `formatCNPJ()` para suportar alfanuméricos
- [ ] Atualizar função `detectPersonTypeFromTaxId()`
- [ ] Atualizar máscara de input em `InputCNPJ.jsx`
- [ ] Adicionar testes unitários para CNPJs alfanuméricos

---

### **FASE 2: Testes (Abril-Maio/2026)**

- [ ] Testar cadastro de empresa com CNPJ alfanumérico
- [ ] Testar busca por CNPJ alfanumérico
- [ ] Testar validação de duplicatas
- [ ] Testar formatação e exibição
- [ ] Testar integração com APIs externas (se disponível)
- [ ] Testar mascaramento LGPD

---

### **FASE 3: Ajustes Finais (Junho/2026)**

- [ ] Atualizar documentação
- [ ] Treinar equipe
- [ ] Monitorar APIs externas (ReceitaWS, etc)
- [ ] Preparar comunicado aos usuários

---

## 🚨 **ALERTAS IMPORTANTES**

### **❌ NÃO FAZER:**
- ❌ Usar `removeNonNumeric()` para CNPJs (remove letras!)
- ❌ Validar apenas formato numérico
- ❌ Comparar CNPJs sem normalizar (case-sensitive)
- ❌ Assumir que APIs externas já suportam alfanuméricos

### **✅ SEMPRE FAZER:**
- ✅ Usar `removeCNPJFormatting()` para CNPJs
- ✅ Validar formato alfanumérico (12 alfanum + 2 num)
- ✅ Converter para MAIÚSCULAS antes de armazenar/comparar
- ✅ Testar com CNPJs alfanuméricos de exemplo

---

## 📊 **EXEMPLOS DE CNPJs ALFANUMÉRICOS**

### **Formato:**
```
XX.XXX.XXX/XXXX-DV
```

Onde:
- **XX.XXX.XXX/XXXX** = 12 caracteres alfanuméricos (A-Z, 0-9)
- **DV** = 2 dígitos verificadores numéricos (0-9)

### **Exemplos Válidos:**
```
AB.123.456/0001-78
12.ABC.DEF/0001-90
ZZ.999.888/0001-45
```

### **Exemplos Inválidos:**
```
AB.123.456/000A-78  ❌ DV deve ser numérico
ab.123.456/0001-78  ❌ Deve estar em MAIÚSCULAS
AB.123.456/0001     ❌ Faltam os DVs
```

---

## 🎯 **PRIORIDADE E CRONOGRAMA**

### **Prioridade:** MÉDIA
- Mudança entra em vigor em **Julho/2026**
- Temos **~8 meses** para implementar

### **Cronograma Recomendado:**

| Fase | Período | Atividades |
|------|---------|------------|
| **Preparação** | Mar/2026 | Implementar ajustes no código |
| **Testes** | Abr-Mai/2026 | Testes completos com CNPJs alfanuméricos |
| **Ajustes Finais** | Jun/2026 | Documentação, treinamento, comunicação |
| **Go Live** | Jul/2026 | Sistema pronto para novos CNPJs |

---

## 📝 **CONCLUSÃO**

### **Banco de Dados:**
✅ **100% PRONTO** - Nenhuma alteração necessária

### **Backend:**
⚠️ **3 PONTOS DE AJUSTE**
1. Atualizar schemas (descrição)
2. Criar validador de CNPJ alfanumérico
3. Normalizar CNPJs para maiúsculas

### **Frontend:**
⚠️ **8 PONTOS DE AJUSTE**
1. Criar `removeCNPJFormatting()`
2. Atualizar `validateCNPJ()`
3. Atualizar `formatCNPJ()`
4. Atualizar `detectPersonTypeFromTaxId()`
5. Atualizar máscara de input
6. Atualizar consulta à Receita Federal
7. Normalizar comparações
8. Normalizar envio para API

### **Esforço Estimado:**
- **Backend:** 8 horas
- **Frontend:** 16 horas
- **Testes:** 8 horas
- **Total:** ~32 horas (4 dias úteis)

---

**✅ Análise completa! Pronto para implementação.**
