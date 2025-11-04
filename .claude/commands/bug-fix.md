---
description: Corrigir bugs seguindo metodologia TDD e análise de causa raiz
---

# Corrigir Bug

Workflow sistemático para identificar, reproduzir e corrigir bugs com testes.

## Comandos Disponíveis
**Uso:** `/bug-fix [descrição]`
**Exemplo:** `/bug-fix Erro ao salvar endereço com CEP vazio`

## Workflow

### 1. Reproduzir o Bug
Coletar informações:
- Descrição do erro
- Passos para reproduzir
- Comportamento esperado vs atual
- Mensagem de erro completa
- Ambiente (dev/prod)

### 2. Localizar o Código
- Buscar arquivo/função relacionada
- Analisar stack trace
- Verificar logs relacionados
- Mostrar código suspeito ao usuário

### 3. Identificar Causa Raiz
Analisar:
- Lógica incorreta
- Validações faltando
- Edge cases não cobertos
- Dependências com problemas

### 4. Criar Teste que Falha (TDD)
ANTES de corrigir, criar teste que reproduz o bug:
```typescript
it('deve [comportamento esperado] quando [condição do bug]', () => {
  const result = funcaoComBug(inputProblematico);
  expect(result).toBe(valorEsperado);
});
```

### 5. Propor Solução
Mostrar:
- Código ANTES (com bug)
- Código DEPOIS (corrigido)
- Explicação da mudança
- Possíveis efeitos colaterais

Aguardar aprovação do usuário.

### 6. Implementar Correção
- Aplicar mudança
- Remover código comentado
- Adicionar validações necessárias
- Documentar se não óbvio

### 7. Validar Correção
Rodar testes:
```bash
# Backend
pytest tests/test_[arquivo].py -v

# Frontend
npm test -- [Arquivo].test.tsx
```

Verificar que:
- ✅ Teste específico passa
- ✅ Todos os testes continuam passando
- ✅ Linter sem warnings

### 8. Adicionar Testes Preventivos
Cobrir edge cases:
- String vazia
- null/undefined
- Valores extremos
- Tipos incorretos

### 9. Documentar
Adicionar comentário se necessário:
```typescript
// IMPORTANTE: Validação crítica para prevenir bug #123
```

## Checklist
- [ ] Bug reproduzido
- [ ] Causa raiz identificada
- [ ] Teste que falha criado (TDD)
- [ ] Solução implementada
- [ ] Teste específico passa
- [ ] Todos os testes passam
- [ ] Edge cases cobertos
- [ ] Documentado se necessário
- [ ] Código comentado removido
- [ ] Linter passou
