# 🛡️ Padrões de Proteção Contra Erros de `undefined`

## 📋 Objetivo
Documentar padrões para prevenir erros `Cannot read properties of undefined` em todo o projeto.

---

## 🎯 Regra de Ouro

**SEMPRE** proteger acessos a propriedades que podem ser `undefined` ou `null`.

---

## 🔧 Padrões de Proteção

### 1. **Optional Chaining (`?.`)**
Use para acessar propriedades aninhadas:

```typescript
// ❌ RUIM - Pode crashar
const length = data.items.length;
const name = user.profile.name;

// ✅ BOM - Seguro
const length = data?.items?.length;
const name = user?.profile?.name;
```

---

### 2. **Nullish Coalescing (`??` ou `||`)**
Use para fornecer valores padrão:

```typescript
// ❌ RUIM - Pode ser undefined
const total = response.total;
const page = response.page;

// ✅ BOM - Sempre tem valor
const total = response.total ?? 0;
const page = response.page || 1;
```

**Diferença:**
- `||` → Retorna valor padrão se falsy (0, '', false, null, undefined)
- `??` → Retorna valor padrão APENAS se null ou undefined

---

### 3. **Array Map Protection**
SEMPRE proteja arrays antes de usar `.map()`:

```typescript
// ❌ RUIM - Crasha se data for undefined
data.map(item => ...)

// ✅ BOM - Seguro
(data || []).map(item => ...)
(data ?? []).map(item => ...)
```

---

### 4. **Array Length Protection**
Proteja acessos a `.length`:

```typescript
// ❌ RUIM
if (items.length > 0) { ... }
const count = items.length;

// ✅ BOM
if ((items?.length || 0) > 0) { ... }
const count = items?.length ?? 0;
```

---

### 5. **Filter Before Map (React Keys)**
Evite retornar `null` dentro de `.map()`:

```typescript
// ❌ RUIM - React warning sobre keys
{items.map(item => {
  if (!item.active) return null;
  return <div key={item.id}>{item.name}</div>;
})}

// ✅ BOM - Filtra antes
{items
  .filter(item => item.active)
  .map(item => (
    <div key={item.id}>{item.name}</div>
  ))}
```

---

### 6. **Estado Inicial Completo**
Sempre inicialize estados com valores completos:

```typescript
// ❌ RUIM - Propriedades podem ficar undefined
const [state, setState] = useState({});

// ✅ BOM - Todas propriedades definidas
const [state, setState] = useState({
  data: [],
  loading: false,
  error: null,
  total: 0,
  currentPage: 1,
  pageSize: 10
});
```

---

### 7. **API Response Protection**
Sempre proteja respostas de API:

```typescript
// ❌ RUIM
setState({
  data: response.items,
  total: response.total,
  page: response.page
});

// ✅ BOM
setState({
  data: response.items || [],
  total: response.total ?? 0,
  page: response.page || 1
});
```

---

### 8. **Console.log Protection**
Proteja até logs de debug:

```typescript
// ❌ RUIM - Pode crashar
console.log(`Total: ${data.length}`);

// ✅ BOM
console.log(`Total: ${data?.length || 0}`);
```

---

## 📝 Checklist de Revisão

Ao revisar código, verificar:

- [ ] Todos os `.map()` têm proteção `(array || [])`?
- [ ] Todos os `.length` têm proteção `?.length || 0`?
- [ ] Estados iniciais estão completos?
- [ ] Respostas de API têm valores padrão?
- [ ] Não há `return null` dentro de `.map()`?
- [ ] Optional chaining usado em acessos aninhados?
- [ ] Console.logs protegidos?

---

## 🚨 Erros Comuns Resolvidos

### Erro 1: `Cannot read properties of undefined (reading 'map')`
```typescript
// ❌ Causa
state.data.map(...)

// ✅ Solução
(state.data || []).map(...)
```

### Erro 2: `Cannot read properties of undefined (reading 'length')`
```typescript
// ❌ Causa
if (items.length > 0)

// ✅ Solução
if ((items?.length || 0) > 0)
```

### Erro 3: `Each child in a list should have a unique "key" prop`
```typescript
// ❌ Causa
{items.map(item => {
  if (!item.active) return null;
  return <div key={item.id}>...</div>;
})}

// ✅ Solução
{items
  .filter(item => item.active)
  .map(item => <div key={item.id}>...</div>)}
```

---

## 🎓 Quando Aplicar

**SEMPRE** que:
1. Acessar propriedades de objetos vindos de API
2. Usar `.map()`, `.filter()`, `.reduce()` em arrays
3. Acessar `.length` de arrays
4. Trabalhar com estado do React
5. Fazer operações matemáticas com valores que podem ser undefined
6. Renderizar listas no React

---

## 💡 Benefícios

✅ **Zero crashes** por undefined  
✅ **Código defensivo** e robusto  
✅ **Melhor UX** (sem telas brancas)  
✅ **Menos bugs** em produção  
✅ **Manutenção** mais fácil  

---

**Última atualização:** 28/10/2025  
**Versão:** 1.0
