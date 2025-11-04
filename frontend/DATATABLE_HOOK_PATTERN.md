# 📋 Padrão de Hooks para DataTable

## ⚠️ Problema Identificado

Após ajustes e melhorias, vários hooks que usam `DataTableTemplate` estavam com estrutura incompleta, causando erro:

```
TypeError: Cannot convert undefined or null to object at Object.values()
```

**Causa:** Hook não retornava todas as propriedades obrigatórias do `UseDataTableReturn`.

---

## ✅ Estrutura Obrigatória

Todo hook que retorna `UseDataTableReturn<T>` **DEVE** ter:

### 1. Interface `DataTableState` Completa

```typescript
const state: DataTableState = {
  // Dados
  data: paginatedData,           // ✅ Dados da página atual
  filteredData: filteredData,    // ✅ Todos os dados filtrados
  loading: boolean,              // ✅ Estado de carregamento
  error: string | null,          // ✅ Mensagem de erro
  
  // Paginação
  currentPage: number,           // ✅ Página atual
  pageSize: number,              // ✅ Tamanho da página
  totalPages: number,            // ✅ Total de páginas
  
  // Filtros e Busca
  searchTerm: string,            // ✅ Termo de busca
  activeFilters: Record<string, any>,  // ✅ CRÍTICO: Filtros ativos
  
  // Seleção
  selectedItems: number[],       // ✅ IDs selecionados
  
  // UI State
  showDetailedMetrics: boolean,  // ✅ Mostrar métricas detalhadas
  showExportDropdown: boolean,   // ✅ Mostrar dropdown de export
  selectedItemForModal: any | null,  // ✅ Item selecionado para modal
  isModalOpen: boolean,          // ✅ Modal aberto
};
```

### 2. Interface `DataTableCallbacks` Completa

```typescript
const callbacks: DataTableCallbacks<T> = {
  // Paginação
  onPageChange: (page: number) => void,
  onPageSizeChange: (size: number) => void,
  
  // Busca e Filtros
  onSearch: (term: string) => void,
  onFilter: (key: string, value: any) => void,
  onClearFilters: () => void,
  
  // Seleção
  onSelectItem: (id: number, selected: boolean) => void,
  onSelectAll: (selected: boolean) => void,
  
  // Ações
  onExport: (format: string, data?: T[]) => void,
  onAction: (actionId: string, item: T) => void,
  onBulkAction: (actionId: string, items: T[]) => void,
  
  // UI State
  onToggleDetailedMetrics: () => void,
  onToggleExportDropdown: () => void,
  onOpenModal: (item: T) => void,
  onCloseModal: () => void,
};
```

### 3. Retorno Completo

```typescript
return {
  state,                    // ✅ Estado completo
  callbacks,                // ✅ Callbacks completos
  metrics: [],              // ✅ Métricas (pode ser vazio)
  detailedMetrics: undefined, // ✅ Métricas detalhadas (pode ser undefined)
};
```

---

## 🔧 Hooks Corrigidos

### ✅ useCompaniesDataTable.ts
- Adicionado `activeFilters`, `searchTerm`, `selectedItems` ao state
- Adicionado `filteredData`, `currentPage`, `totalPages`
- Adicionado todos callbacks obrigatórios
- Retorna `metrics` e `detailedMetrics`

### ✅ useLgpdAuditLogsDataTable.ts
- Corrigido callback `onFilter` para aceitar `(key, value)`
- Adicionado `filteredData`, `totalPages` ao state
- Adicionado todos callbacks faltantes
- Retorna `metrics` e `detailedMetrics`

### ✅ useCompanyBillingData.ts
- Já estava correto, apenas adicionados callbacks faltantes
- `onAction`, `onBulkAction`, `onToggleDetailedMetrics`, etc.

### ✅ useSubscriptionPlans.ts
- Já estava correto, apenas adicionados callbacks faltantes
- `onAction`, `onBulkAction`, `onToggleDetailedMetrics`, etc.

---

## 📝 Checklist para Novos Hooks

Ao criar um novo hook para DataTable:

- [ ] Estado tem todas as 14 propriedades obrigatórias
- [ ] `activeFilters` é `Record<string, any>` (não `undefined`)
- [ ] `searchTerm` é `string` (não `undefined`)
- [ ] `filteredData` contém todos os dados filtrados
- [ ] `totalPages` é calculado corretamente
- [ ] Callbacks tem todas as 14 funções obrigatórias
- [ ] `onFilter` aceita `(key: string, value: any)`
- [ ] Retorna `state`, `callbacks`, `metrics`, `detailedMetrics`

---

## ⚠️ Erro Comum

```typescript
// ❌ ERRADO: activeFilters undefined
const state = {
  data: [],
  loading: false,
  // activeFilters: FALTANDO!
};

// ✅ CORRETO: activeFilters sempre definido
const state = {
  data: [],
  loading: false,
  activeFilters: {},  // Objeto vazio se não houver filtros
};
```

---

## 🎯 Resultado

Após aplicar este padrão:

- ✅ Página de Empresas carrega sem erros
- ✅ DataTableTemplate recebe todas propriedades necessárias
- ✅ Filtros funcionam corretamente
- ✅ Paginação funciona
- ✅ Busca funciona
- ✅ Seleção funciona

---

**Última atualização:** 28/10/2025 22:51 BRT
**Aplicado em:** useCompaniesDataTable, useLgpdAuditLogsDataTable, useCompanyBillingData, useSubscriptionPlans
