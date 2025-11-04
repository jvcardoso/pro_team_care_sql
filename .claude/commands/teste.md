---
description: Criar testes completos (sucesso, erro, edge cases) com boa cobertura
---

# Criar Testes

Criar testes unitários e de integração completos seguindo TDD.

## Comandos Disponíveis
**Uso:** `/teste [componente|função|endpoint] [caminho]`
**Exemplo:** `/teste endpoint backend/app/api/v1/companies.py`

## Workflow

### 1. Análise
Identificar o que testar:
- Componente React
- Função utilitária
- Endpoint API
- Hook customizado
- Service/Repository

### 2. Criar Estrutura de Teste

#### Para Componente React:
```typescript
// [Nome].test.tsx
describe('[Nome]', () => {
  it('deve renderizar corretamente', () => { /* ... */ });
  it('deve chamar callback ao clicar', () => { /* ... */ });
  it('deve lidar com valores vazios', () => { /* ... */ });
  it('deve mostrar loading', () => { /* ... */ });
  it('deve mostrar erro', () => { /* ... */ });
});
```

#### Para Endpoint API:
```python
# test_[recurso].py
@pytest.mark.asyncio
class Test[Recurso]:
    async def test_create_success(self, client, auth_headers): ...
    async def test_create_invalid_data(self, client, auth_headers): ...
    async def test_create_unauthorized(self, client): ...
    async def test_list_success(self, client, auth_headers): ...
    async def test_get_not_found(self, client, auth_headers): ...
```

### 3. Casos de Teste Obrigatórios

#### Cenários de Sucesso:
- ✅ Entrada válida retorna resultado esperado
- ✅ Diferentes estados/props funcionam
- ✅ Interações do usuário funcionam

#### Casos de Erro:
- ❌ Entrada inválida lança erro
- ❌ Não autenticado retorna 401
- ❌ Não encontrado retorna 404
- ❌ Validação falha retorna 422

#### Edge Cases:
- 🔀 Valores vazios (string vazia, array vazio)
- 🔀 null/undefined
- 🔀 Valores extremos (min/max)
- 🔀 Tipos incorretos
- 🔀 Paginação

### 4. Executar Testes

#### Backend:
```bash
cd backend
pytest tests/test_[recurso].py -v
pytest tests/test_[recurso].py --cov=app.[recurso] --cov-report=term
```

#### Frontend:
```bash
cd frontend
npm test -- [Nome].test.tsx
npm test -- [Nome].test.tsx --coverage
```

### 5. Validar Cobertura
Meta: **80%+ de cobertura**

Se cobertura < 80%:
- Identificar código não coberto
- Adicionar testes faltantes
- Focar em edge cases e tratamento de erros

### 6. Resumo
Apresentar:
- Total de testes criados
- Casos de sucesso/erro/edge cases
- Cobertura alcançada
- Status (passaram/falharam)

## Padrões Obrigatórios
- ✅ Testar sucesso + erro + edge cases
- ✅ Nomes descritivos (deve fazer X quando Y)
- ✅ Arrange-Act-Assert pattern
- ✅ Mockar dependências externas
- ✅ Cobertura > 80%
- ❌ NUNCA testar apenas caso feliz
- ❌ NUNCA ignorar edge cases
- ❌ NUNCA testes sem assertions
