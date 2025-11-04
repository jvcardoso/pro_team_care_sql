---
description: Refatorar código identificando duplicação e criando componentes reutilizáveis
---

# Refatorar Código

Refatorar código seguindo princípios DRY (Don't Repeat Yourself).

## Comandos Disponíveis
**Uso:** `/refatorar [arquivo|diretório]`
**Exemplo:** `/refatorar src/components/forms/`

## Workflow

### 1. Análise de Duplicação
Identificar:
- [ ] Código duplicado entre arquivos
- [ ] Lógica repetida em componentes
- [ ] Funções similares que podem ser generalizadas
- [ ] Padrões que aparecem múltiplas vezes

### 2. Apresentar Diagnóstico
```
🔍 Análise de Duplicação:

Encontrei:
- [N] blocos de código duplicado
- [N] funções similares
- [N] componentes que podem ser unificados

Locais:
1. [arquivo:linha] - [descrição]
2. [arquivo:linha] - [descrição]

Proposta:
- Criar [Nome] reutilizável
- Substituir [N] ocorrências
- Remover [X] linhas duplicadas
```

Aguardar aprovação.

### 3. Criar Componente/Função Reutilizável

#### Para Componentes React:
```typescript
// src/components/shared/[Nome].tsx
interface [Nome]Props {
  // Props generalizadas
  data: T;
  onAction: (item: T) => void;
  className?: string;
}

export const [Nome] = <T,>({ data, onAction, className }: [Nome]Props<T>) => {
  // Lógica reutilizável
};
```

#### Para Funções Utilitárias:
```typescript
// src/utils/[categoria].ts
export function [nomeFuncao]<T>(
  input: T,
  options?: Options
): Result {
  // Lógica generalizada
}
```

### 4. Substituir Todas Ocorrências
Para cada local duplicado:
1. Importar novo componente/função
2. Substituir código duplicado
3. Passar props/argumentos necessários
4. Remover código antigo comentado

### 5. Limpeza Automática
SEMPRE remover:
- ❌ Código comentado (usar git history)
- ❌ Imports não usados
- ❌ Variáveis não usadas
- ❌ Funções não usadas
- ❌ TODOs sem contexto

### 6. Executar Linter e Formatter

#### Backend:
```bash
cd backend
black .
flake8 .
```

#### Frontend:
```bash
cd frontend
npm run format
npm run lint
```

### 7. Executar Testes
Garantir que nada quebrou:

#### Backend:
```bash
pytest
```

#### Frontend:
```bash
npm test
```

### 8. Apresentar Resumo
```
✅ Refatoração concluída!

📊 Métricas:
- Linhas eliminadas: [N]
- Duplicações removidas: [N]
- Imports limpos: [N]
- Código reutilizável criado: [Nome]
- Usado em [N] lugares

🎯 Benefícios:
- Código mais limpo e manutenível
- DRY aplicado
- Facilita testes

🧹 Limpeza:
- Imports não usados: [N] removidos
- Código comentado: [X] linhas removidas
- Linter: ✅ Sem warnings
- Testes: ✅ Todos passaram
```

## Padrões Obrigatórios
- ✅ Buscar duplicação ANTES de criar
- ✅ Criar componente/função reutilizável
- ✅ Substituir TODAS ocorrências
- ✅ Remover código comentado
- ✅ Limpar imports não usados
- ✅ Executar linter
- ✅ Rodar testes
- ❌ NUNCA deixar código comentado
- ❌ NUNCA ignorar warnings de linter

## Checklist
- [ ] Duplicação identificada
- [ ] Componente/função reutilizável criado
- [ ] Todas ocorrências substituídas
- [ ] Código comentado removido
- [ ] Imports limpos
- [ ] Linter passou
- [ ] Testes passaram
- [ ] Resumo apresentado
