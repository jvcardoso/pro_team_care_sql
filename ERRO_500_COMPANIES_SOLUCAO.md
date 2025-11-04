# 🚨 ERRO 500: GET /api/v1/companies/164

## 📊 Diagnóstico

### Sintoma
- Endpoint `GET /api/v1/companies/164` retorna **500 Internal Server Error**
- Frontend faz múltiplas tentativas (retry) mas todas falham
- Listagem de empresas funciona (`GET /complete-list`)
- Detalhes de empresa específica falha

### Causa Raiz
O endpoint `GET /api/v1/companies/{id}` (linha 211 de `companies.py`) tenta acessar o campo `row.PrincipalAddressId` da View `vw_complete_company_data`, mas **esse campo não existe** na View atual do banco de dados.

```python
# Linha 211 em companies.py
"addresses": [{
    "id": row.PrincipalAddressId,  # ❌ ERRO: Campo não existe na View
    "street": row.PrincipalStreet,
    ...
}]
```

### Por Que Aconteceu?
Durante a consolidação do CRUD, foi criado o script SQL `037_Add_Address_ID_To_Company_View.sql` para adicionar o campo `PrincipalAddressId` à View, mas **o script não foi executado no banco de dados**.

---

## ✅ Solução

### Opção 1: Executar Script SQL (RECOMENDADO)

**1. Abrir Azure Data Studio ou SQL Server Management Studio**

**2. Conectar ao banco `pro_team_care`**

**3. Executar o script:**
```
Database/EXECUTE_037.sql
```

Este script:
- ✅ Verifica se a coluna já existe
- ✅ Atualiza a View se necessário
- ✅ Testa a View após atualização
- ✅ É idempotente (pode executar múltiplas vezes)

**4. Reiniciar o backend FastAPI**
```bash
# O backend detectará a mudança automaticamente (hot reload)
# Ou reinicie manualmente se necessário
```

---

### Opção 2: Correção Temporária no Backend (NÃO RECOMENDADO)

Se não puder executar o script SQL imediatamente, pode fazer uma correção temporária no backend:

**Arquivo:** `backend/app/api/v1/companies.py` (linha 210-220)

```python
# ❌ ANTES (quebra se PrincipalAddressId não existe)
"addresses": [{
    "id": row.PrincipalAddressId,
    "street": row.PrincipalStreet,
    ...
}] if row.PrincipalStreet else []

# ✅ DEPOIS (usa getattr com fallback)
"addresses": [{
    "id": getattr(row, 'PrincipalAddressId', None),  # Fallback para None
    "street": row.PrincipalStreet,
    ...
}] if row.PrincipalStreet else []
```

**⚠️ IMPORTANTE:** Esta é apenas uma solução temporária. O correto é executar o script SQL para adicionar o campo à View.

---

## 🔍 Verificação

### Após executar o script SQL:

**1. Testar a View diretamente no SQL:**
```sql
SELECT TOP 1 
    CompanyId, 
    PrincipalAddressId,
    PrincipalStreet
FROM [core].[vw_complete_company_data]
WHERE CompanyId = 164;
```

**Resultado esperado:**
```
CompanyId | PrincipalAddressId | PrincipalStreet
164       | 123                | Rua ***
```

**2. Testar o endpoint no navegador:**
```
http://192.168.11.83:3000/admin/companies/164?tab=information
```

**Resultado esperado:**
- ✅ Página carrega sem erros
- ✅ Dados da empresa são exibidos
- ✅ Endereço aparece mascarado
- ✅ Botão "Revelar" funciona

---

## 📋 Checklist de Resolução

- [ ] Executar `Database/EXECUTE_037.sql` no SQL Server
- [ ] Verificar que coluna `PrincipalAddressId` existe na View
- [ ] Reiniciar backend FastAPI (se necessário)
- [ ] Testar endpoint `GET /api/v1/companies/164`
- [ ] Verificar que página de detalhes carrega
- [ ] Testar funcionalidade de revelar endereço

---

## 🎯 Prevenção Futura

### Para evitar esse tipo de problema:

1. **Sempre executar scripts SQL após criá-los**
   - Criar script → Executar → Testar → Commitar

2. **Manter log de scripts executados**
   - Criar arquivo `Database/EXECUTED_SCRIPTS.md` com lista de scripts executados

3. **Validar estrutura antes de usar**
   - Backend deve validar se campos existem antes de acessá-los
   - Usar `getattr(row, 'campo', None)` para campos opcionais

4. **Testes de integração**
   - Criar testes que validam estrutura da View
   - Alertar se campos esperados estão faltando

---

## 📊 Impacto

### Antes da Correção:
- ❌ Detalhes de empresa retornam 500
- ❌ Não é possível visualizar dados completos
- ❌ Não é possível revelar endereços
- ✅ Listagem de empresas funciona

### Depois da Correção:
- ✅ Detalhes de empresa carregam corretamente
- ✅ Todos os dados são exibidos
- ✅ Revelação de endereços funciona
- ✅ Sistema 100% funcional

---

## 🔗 Arquivos Relacionados

- `Database/037_Add_Address_ID_To_Company_View.sql` - Script original
- `Database/EXECUTE_037.sql` - Script de execução com verificação
- `backend/app/api/v1/companies.py` - Endpoint que usa a View
- `frontend/src/components/contacts/AddressRevealCard.tsx` - Componente que revela endereços

---

**Prioridade:** 🔴 CRÍTICA  
**Tempo Estimado:** 5 minutos  
**Complexidade:** Baixa  
**Risco:** Baixo (script é idempotente)
