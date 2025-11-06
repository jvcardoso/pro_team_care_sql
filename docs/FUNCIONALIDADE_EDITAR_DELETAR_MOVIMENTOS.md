# ✅ Funcionalidade de Editar e Deletar Movimentos

## 🎯 Implementado

Adicionada funcionalidade completa para **editar e deletar movimentos** do Kanban.

---

## 🔧 O Que Foi Feito

### **1. Backend (COMPLETO):**

#### **Endpoints Criados:**
```python
# Editar movimento
PUT /api/v1/kanban/movements/{movement_id}

# Deletar movimento
DELETE /api/v1/kanban/movements/{movement_id}
```

#### **Repository:**
```python
# backend/app/repositories/kanban_repository.py

async def update(
    self,
    movement_id: int,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    time_spent: Optional[int] = None
) -> Optional[CardMovement]:
    """Atualiza movimento"""
    # Implementação completa

async def delete(self, movement_id: int) -> bool:
    """Deleta movimento"""
    # Implementação completa
```

#### **API Endpoints:**
```python
# backend/app/api/v1/kanban.py

@router.put("/movements/{movement_id}", response_model=CardMovementResponse)
async def update_movement(
    movement_id: int,
    data: CardMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza movimento/lançamento existente."""
    # Implementação completa

@router.delete("/movements/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movement(
    movement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deleta movimento/lançamento."""
    # Implementação completa
```

### **2. Frontend Service (COMPLETO):**

```typescript
// frontend/src/services/kanbanService.ts

/**
 * Atualiza movimento/lançamento
 */
export const updateMovement = async (
  movementId: number,
  data: MovementCreateData
): Promise<CardMovement> => {
  const response = await api.put(`/api/v1/kanban/movements/${movementId}`, data);
  return response.data;
};

/**
 * Deleta movimento/lançamento
 */
export const deleteMovement = async (movementId: number): Promise<void> => {
  await api.delete(`/api/v1/kanban/movements/${movementId}`);
};

// Exportado no kanbanService
export const kanbanService = {
  // ...
  updateMovement,
  deleteMovement,
  // ...
};
```

### **3. Frontend UI (PENDENTE):**

#### **O Que Falta Implementar:**

1. **Botões de Editar e Deletar em Cada Movimento:**
```tsx
// Em cada movimento na lista, adicionar:
<div className="flex items-center gap-2">
  <button
    onClick={() => handleEditMovement(movement.MovementID, movement)}
    className="text-blue-600 hover:text-blue-700"
    title="Editar movimento"
  >
    <svg>...</svg> {/* Ícone de editar */}
  </button>
  <button
    onClick={() => setMovementToDelete(movement.MovementID)}
    className="text-red-600 hover:text-red-700"
    title="Deletar movimento"
  >
    <svg>...</svg> {/* Ícone de deletar */}
  </button>
</div>
```

2. **Formulário de Edição:**
```tsx
// Reutilizar o formulário de adicionar movimento
// Quando editingMovementId !== null, mostrar "Atualizar" ao invés de "Salvar"
{(showAddMovement || editingMovementId) && (
  <form onSubmit={editingMovementId ? handleUpdateMovement : handleAddMovement}>
    {/* Campos do formulário */}
    <button type="submit">
      {editingMovementId ? 'Atualizar' : 'Salvar'}
    </button>
  </form>
)}
```

3. **Modal de Confirmação de Exclusão:**
```tsx
{movementToDelete && (
  <div className="modal">
    <h3>Confirmar Exclusão</h3>
    <p>Tem certeza que deseja deletar este movimento?</p>
    <button onClick={handleDeleteMovement}>Deletar</button>
    <button onClick={() => setMovementToDelete(null)}>Cancelar</button>
  </div>
)}
```

4. **Estados Necessários:**
```tsx
const [editingMovementId, setEditingMovementId] = useState<number | null>(null);
const [movementToDelete, setMovementToDelete] = useState<number | null>(null);
```

5. **Funções de Handler:**
```tsx
const handleEditMovement = (movementId: number, movement: any) => {
  setEditingMovementId(movementId);
  setMovementForm({
    Subject: movement.Subject,
    Description: movement.Description || '',
    TimeSpent: movement.TimeSpent || undefined
  });
};

const handleUpdateMovement = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!editingMovementId) return;
  
  await kanbanService.updateMovement(editingMovementId, movementForm);
  setEditingMovementId(null);
  setMovementForm({ Subject: '', Description: '', TimeSpent: undefined });
  await loadCardDetails();
};

const handleDeleteMovement = async () => {
  if (!movementToDelete) return;
  
  await kanbanService.deleteMovement(movementToDelete);
  setMovementToDelete(null);
  await loadCardDetails();
};
```

---

## 🚀 Como Testar (Backend)

### **1. Testar Edição via cURL:**
```bash
# Atualizar movimento
curl -X PUT "http://192.168.11.83:8000/api/v1/kanban/movements/123" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Subject": "Reunião atualizada",
    "Description": "Descrição atualizada",
    "TimeSpent": 60
  }'
```

### **2. Testar Exclusão via cURL:**
```bash
# Deletar movimento
curl -X DELETE "http://192.168.11.83:8000/api/v1/kanban/movements/123" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### **3. Verificar no Banco:**
```sql
-- Ver movimento antes de editar
SELECT * FROM core.CardMovements WHERE MovementID = 123;

-- Após editar, verificar mudanças
SELECT * FROM core.CardMovements WHERE MovementID = 123;

-- Após deletar, verificar que não existe mais
SELECT * FROM core.CardMovements WHERE MovementID = 123;
-- Resultado: 0 rows
```

---

## ⚠️ Regras de Negócio

### **Movimentos que NÃO Podem Ser Editados/Deletados:**
```typescript
// Movimentos do sistema não devem ter botões de editar/deletar
movement.MovementType === 'Created'      // Card criado
movement.MovementType === 'ColumnChange' // Mudança de coluna
movement.MovementType === 'Completed'    // Card concluído
```

**Apenas movimentos manuais (tipo 'Update' ou 'Comment') podem ser editados/deletados.**

### **Validação:**
```tsx
{movement.MovementType !== 'Created' && 
 movement.MovementType !== 'ColumnChange' && 
 movement.MovementType !== 'Completed' && (
  <>
    <button onClick={() => handleEditMovement(...)}>Editar</button>
    <button onClick={() => setMovementToDelete(...)}>Deletar</button>
  </>
)}
```

---

## 📊 Fluxo Completo

### **Editar Movimento:**
```
1. Usuário clica em "Editar" no movimento
2. Formulário é preenchido com dados atuais
3. Usuário modifica campos
4. Clica em "Atualizar"
5. API PUT /movements/{id} é chamada
6. Movimento atualizado no banco
7. Lista de movimentos recarregada
```

### **Deletar Movimento:**
```
1. Usuário clica em "Deletar" no movimento
2. Modal de confirmação aparece
3. Usuário confirma exclusão
4. API DELETE /movements/{id} é chamada
5. Movimento removido do banco
6. Lista de movimentos recarregada
```

---

## 🔐 Segurança

### **Permissões:**
- ✅ Requer autenticação (JWT token)
- ✅ Valida que movimento existe
- ✅ Retorna 404 se não encontrado

### **Validações Backend:**
```python
# Verifica se movimento existe
movement = await service.movement_repo.update(...)
if not movement:
    raise HTTPException(404, "Movimento não encontrado")
```

---

## 📁 Arquivos Modificados

```
✅ backend/app/api/v1/kanban.py
   - Endpoint PUT /movements/{movement_id}
   - Endpoint DELETE /movements/{movement_id}
   
✅ backend/app/repositories/kanban_repository.py
   - Método update() no CardMovementRepository
   - Método delete() no CardMovementRepository
   
✅ frontend/src/services/kanbanService.ts
   - Função updateMovement()
   - Função deleteMovement()
   - Export no kanbanService
   
⏳ frontend/src/components/kanban/CardDetailModal.tsx (PENDENTE)
   - Botões de editar/deletar
   - Modal de confirmação
   - Handlers de edição/exclusão
   
✅ docs/FUNCIONALIDADE_EDITAR_DELETAR_MOVIMENTOS.md (NOVO)
```

---

## 🎯 Próximos Passos

### **Para Completar a Implementação:**

1. **Adicionar Botões nos Movimentos:**
   - Editar arquivo `CardDetailModal.tsx`
   - Adicionar ícones de editar e deletar em cada movimento
   - Aplicar regra: só mostrar para movimentos manuais

2. **Implementar Modal de Confirmação:**
   - Similar ao modal de deletar card
   - Mostrar informações do movimento
   - Botões: Cancelar / Deletar

3. **Testar Fluxo Completo:**
   - Criar movimento manual
   - Editar movimento
   - Deletar movimento
   - Verificar que movimentos do sistema não têm botões

---

## 📝 Exemplo de Uso

### **Cenário: Corrigir Tempo Gasto**

```
Problema: Registrou 30 minutos mas foram 60
Solução:
1. Abrir card
2. Ir em "Movimentos Internos"
3. Clicar em "Editar" no movimento
4. Alterar "Tempo gasto" de 30 para 60
5. Clicar em "Atualizar"
6. ✅ Movimento atualizado
```

### **Cenário: Remover Movimento Duplicado**

```
Problema: Criou movimento duplicado por engano
Solução:
1. Abrir card
2. Ir em "Movimentos Internos"
3. Clicar em "Deletar" no movimento duplicado
4. Confirmar exclusão
5. ✅ Movimento removido
```

---

## 📊 Status Atual

### **✅ Completo:**
- Backend API (PUT e DELETE)
- Repository (update e delete)
- Frontend Service (updateMovement e deleteMovement)
- Documentação

### **⏳ Pendente:**
- UI do frontend (botões e modais)
- Testes de integração
- Validação de permissões por usuário

---

**Backend 100% pronto! Falta apenas a interface do usuário.** 🎉

**API testável via cURL ou Postman agora!** 🚀
