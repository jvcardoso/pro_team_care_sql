# 📋 Valores Aceitos pelas Constraints do Banco

## 🔍 Constraints de CHECK

### 📞 **Phones (core.phones)**
**Constraint:** `phones_type_check`

**Valores aceitos para `type`:**
- `'landline'` - Telefone fixo
- `'mobile'` - Celular
- `'whatsapp'` - WhatsApp
- `'commercial'` - Comercial
- `'emergency'` - Emergência
- `'fax'` - Fax

**❌ NÃO use:** `'billing'`, `'work'`, `'personal'`

---

### 📧 **Emails (core.emails)**
**Constraint:** `emails_type_check`

**Valores aceitos para `type`:**
- `'personal'` - Pessoal
- `'work'` - Trabalho
- `'billing'` - Faturamento
- `'contact'` - Contato

**❌ NÃO use:** `'commercial'`, `'emergency'`

---

### 📍 **Addresses (core.addresses)**
**Constraint:** `addresses_type_check`

**Valores aceitos para `type`:**
- `'residential'` - Residencial
- `'commercial'` - Comercial
- `'correspondence'` - Correspondência
- `'billing'` - Faturamento
- `'delivery'` - Entrega

**❌ NÃO use:** `'work'`, `'personal'`

---

### 🏥 **Establishments (core.establishments)**

**Constraint:** `establishments_type_check`

**Valores aceitos para `type`:**
- `'matriz'` - Matriz
- `'filial'` - Filial
- `'unidade'` - Unidade
- `'posto'` - Posto

**❌ NÃO use:** `'hospital'`, `'commercial'`

---

**Constraint:** `establishments_category_check`

**Valores aceitos para `category`:**
- `'clinica'` - Clínica
- `'hospital'` - Hospital
- `'laboratorio'` - Laboratório
- `'farmacia'` - Farmácia
- `'consultorio'` - Consultório
- `'upa'` - UPA
- `'ubs'` - UBS
- `'outro'` - Outro

**❌ NÃO use:** `'hospital_geral'`, `'matriz'`

---

## ✅ Exemplo de JSON Correto

```json
{
    "access_status": "contract_signed",
    "pj_profile": {
        "name": "Clinica Saúde e Vida LTDA",
        "trade_name": "Clínica Viva Bem",
        "tax_id": "11222333000144",
        "incorporation_date": "2015-08-22",
        "tax_regime": "Simples Nacional",
        "legal_nature": "Sociedade Empresária Limitada",
        "municipal_registration": "987654"
    },
    "addresses": [
        {
            "street": "Rua das Flores",
            "number": "123",
            "details": "Sala 10",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01001000",
            "country": "BR",
            "type": "commercial",  ✅ CORRETO
            "is_principal": true
        }
    ],
    "phones": [
        {
            "country_code": "55",
            "number": "1155551234",
            "type": "landline",  ✅ CORRETO (não 'commercial')
            "is_principal": true,
            "is_whatsapp": true,
            "phone_name": "Recepção Principal"
        },
        {
            "country_code": "55",
            "number": "1155555678",
            "type": "mobile",  ✅ CORRETO (não 'billing')
            "is_principal": false,
            "is_whatsapp": false,
            "phone_name": "Financeiro"
        }
    ],
    "emails": [
        {
            "email_address": "contato@vivabem.com.br",
            "type": "work",  ✅ CORRETO
            "is_principal": true
        },
        {
            "email_address": "financeiro@vivabem.com.br",
            "type": "billing",  ✅ CORRETO
            "is_principal": false
        }
    ]
}
```

## ❌ Erros Comuns

### Erro: `phones_type_check`
```
The INSERT statement conflicted with the CHECK constraint "phones_type_check"
```
**Causa:** Valor inválido em `phones.type`
**Solução:** Use apenas: `landline`, `mobile`, `whatsapp`, `commercial`, `emergency`, `fax`

### Erro: `emails_type_check`
```
The INSERT statement conflicted with the CHECK constraint "emails_type_check"
```
**Causa:** Valor inválido em `emails.type`
**Solução:** Use apenas: `personal`, `work`, `billing`, `contact`

### Erro: `addresses_type_check`
```
The INSERT statement conflicted with the CHECK constraint "addresses_type_check"
```
**Causa:** Valor inválido em `addresses.type`
**Solução:** Use apenas: `residential`, `commercial`, `correspondence`, `billing`, `delivery`

### Erro: `establishments_type_check`
```
The INSERT statement conflicted with the CHECK constraint "establishments_type_check"
```
**Causa:** Valor inválido em `establishments.type`
**Solução:** Use apenas: `matriz`, `filial`, `unidade`, `posto`

### Erro: `establishments_category_check`
```
The INSERT statement conflicted with the CHECK constraint "establishments_category_check"
```
**Causa:** Valor inválido em `establishments.category`
**Solução:** Use apenas: `clinica`, `hospital`, `laboratorio`, `farmacia`, `consultorio`, `upa`, `ubs`, `outro`

---

## 📚 Referência Rápida

| Entidade | Campo | Valores Válidos |
|----------|-------|-----------------|
| **Phone** | type | landline, mobile, whatsapp, commercial, emergency, fax |
| **Email** | type | personal, work, billing, contact |
| **Address** | type | residential, commercial, correspondence, billing, delivery |
| **Establishment** | type | matriz, filial, unidade, posto |
| **Establishment** | category | clinica, hospital, laboratorio, farmacia, consultorio, upa, ubs, outro |

---

**💡 Dica:** Sempre consulte este documento antes de criar JSONs para evitar erros de constraint!
