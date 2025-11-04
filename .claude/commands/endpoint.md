---
description: Criar endpoint FastAPI completo com BaseRepository, validação e testes
---

# Criar Endpoint REST API

Siga este workflow para criar um endpoint FastAPI seguindo os padrões do projeto.

## Comandos Disponíveis
**Uso:** `/endpoint [recurso] [método]`
**Exemplo:** `/endpoint companies GET,POST,PUT,DELETE`

## Workflow

### 1. Verificação
- Verificar se endpoint similar já existe em `backend/app/api/v1/`
- Se encontrar, perguntar se deve reutilizar ou criar novo
- Aguardar confirmação do usuário

### 2. Criar Schema Pydantic
Criar em `backend/app/schemas/[recurso].py`:
- `[Recurso]Create` - Schema para criar (POST)
- `[Recurso]Update` - Schema para atualizar (PUT/PATCH)
- `[Recurso]Response` - Schema de resposta
- Validações com Field() e validators

### 3. Criar Endpoint
Criar em `backend/app/api/v1/[recurso].py`:
- Usar BaseRepository para operações CRUD
- Adicionar dependência `get_current_active_user`
- Implementar paginação (skip/limit) para listas
- Tratamento de erros com HTTPException
- Documentação com docstrings em português

### 4. Registrar Rota
Adicionar em `backend/app/api/v1/router.py`

### 5. Criar Testes
Criar em `backend/tests/test_[recurso].py`:
- Casos de sucesso (201, 200)
- Casos de erro (401, 404, 422)
- Edge cases (paginação, validações)

### 6. Executar e Validar
```bash
cd backend
pytest tests/test_[recurso].py -v
```

## Padrões Obrigatórios
- ✅ Usar BaseRepository (NUNCA queries diretas)
- ✅ Soft delete (deleted_at), NUNCA hard delete
- ✅ Type hints completos
- ✅ Autenticação em endpoints protegidos
- ✅ Paginação em endpoints de listagem
- ✅ HTTPException para erros com status codes corretos
- ❌ NUNCA usar `SELECT *`
- ❌ NUNCA criar/alterar tabelas (Database First)
