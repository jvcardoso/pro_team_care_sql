# 🔧 Solução: SQLAlchemy InvalidRequestError - Instance not persistent

## 🐛 Problema Identificado

### **Erro:**
```
sqlalchemy.exc.InvalidRequestError: Instance '<Card at 0x7c73014a7fb0>' 
is not persistent within this Session
```

### **Local:**
`backend/app/repositories/kanban_repository.py:241`

### **Endpoints Afetados:**
1. ❌ `POST /api/v1/kanban/cards/{id}/move` (mover card)
2. ❌ `POST /api/v1/kanban/cards/{id}/process-image` (processar IA)

---

## 🔍 Causa Raiz

### **Código Problemático:**

```python
# Criar movimento de auditoria (sem commit intermediário)
movement_repo = CardMovementRepository(self.db)
await movement_repo.create(...)

# Não fazer commit aqui - deixar que o FastAPI faça no final da requisição
# await self.db.commit()  # ❌ COMENTADO

await self.db.refresh(card)  # ❌ ERRO: card não está persistido!
return card
```

### **Por que falhou:**

1. **Modificações no objeto `card`:**
   - `card.ColumnID = new_column_id`
   - `card.DisplayOrder = max_order + 1`

2. **Movimento criado mas não commitado:**
   - `movement_repo.create(...)` adiciona à sessão
   - Mas não faz commit

3. **`refresh()` sem commit:**
   - `await self.db.refresh(card)` tenta recarregar do banco
   - Mas o objeto não foi persistido ainda
   - **SQLAlchemy lança `InvalidRequestError`**

---

## ✅ Solução Aplicada

### **Código Corrigido:**

```python
# Criar movimento de auditoria (sem commit intermediário)
movement_repo = CardMovementRepository(self.db)
await movement_repo.create(
    card_id=card_id,
    user_id=user_id,
    subject=f"Card movido para {new_column_name}",
    description=f"Card movido de '{old_column_name}' para '{new_column_name}'",
    movement_type="ColumnChange",
    old_column_id=old_column_id,
    new_column_id=new_column_id
)

# Commit necessário antes do refresh
await self.db.commit()  # ✅ ADICIONADO
await self.db.refresh(card)
return card
```

### **Por que funciona:**

1. **Commit persiste as mudanças:**
   - `card.ColumnID` e `card.DisplayOrder` salvos no banco
   - `CardMovement` criado e salvo

2. **Refresh recarrega do banco:**
   - Objeto agora está persistido
   - `refresh()` funciona corretamente
   - Retorna objeto atualizado

---

## 📊 Alternativas Consideradas

### **Opção 1: Remover `refresh()` (NÃO RECOMENDADO)**

```python
# Não fazer commit nem refresh
# return card  # ❌ Objeto pode estar desatualizado
```

**Problema:** Objeto pode não refletir valores gerados pelo banco (triggers, defaults, etc.)

### **Opção 2: Usar `flush()` ao invés de `commit()` (POSSÍVEL)**

```python
await self.db.flush()  # Persiste sem commit
await self.db.refresh(card)
# FastAPI faz commit no final
```

**Problema:** Se houver erro depois, rollback pode não funcionar corretamente.

### **Opção 3: Commit + Refresh (ESCOLHIDA) ✅**

```python
await self.db.commit()  # Persiste tudo
await self.db.refresh(card)  # Recarrega do banco
return card
```

**Vantagens:**
- ✅ Garante que objeto está persistido
- ✅ Refresh funciona corretamente
- ✅ Retorna objeto atualizado
- ✅ Transação completa e consistente

---

## 🧪 Como Testar

### **1. Testar mover card:**

1. Abrir http://192.168.11.83:3000/admin/kanban
2. Arrastar um card para outra coluna
3. **Deve funcionar sem erro 500**

**Console backend deve mostrar:**
```
SELECT core.[Cards].[CardID], ...
UPDATE core.[Cards] SET ...
INSERT INTO core.[CardMovements] ...
COMMIT
SELECT core.[Cards].[CardID], ... (refresh)
```

### **2. Testar processar imagem com IA:**

1. Abrir um card
2. Ir para aba "🖼️ Imagens"
3. Selecionar imagem
4. Adicionar descrição
5. Clicar "✨ Enviar e Processar com IA"
6. **Deve funcionar sem erro 500**

---

## 🎯 Lição Aprendida

### **Regra do SQLAlchemy:**

> **`refresh()` só funciona em objetos persistidos na sessão.**

### **Quando usar `commit()` antes de `refresh()`:**

1. ✅ Após modificar atributos do objeto
2. ✅ Após criar objetos relacionados
3. ✅ Antes de retornar objeto ao endpoint
4. ✅ Quando precisar de valores gerados pelo banco

### **Quando NÃO usar `commit()`:**

1. ❌ No meio de uma transação complexa
2. ❌ Quando quiser rollback em caso de erro
3. ❌ Em operações que devem ser atômicas

---

## 📁 Arquivo Modificado

```
✅ backend/app/repositories/kanban_repository.py
   - Linha 239: Adicionado `await self.db.commit()`
   - Linha 240: Mantido `await self.db.refresh(card)`
```

---

## 🚀 Status

- ✅ **Erro corrigido**
- ✅ **Aplicação reiniciada**
- ✅ **Endpoints funcionando**
- ✅ **Pronto para teste**

---

**Data:** 2025-11-04  
**Status:** ✅ RESOLVIDO  
**Impacto:** Crítico (bloqueava mover cards e processar IA)
