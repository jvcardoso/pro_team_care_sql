# AGENTS.md - Pro Team Care Development Guide

## Comunicação
- **SEMPRE** responda em português brasileiro (pt-BR)
- Use português para comentários de negócio e commits
- Use inglês apenas para docstrings e documentação técnica

## ⚡ Hot Reload (IMPORTANTE!)
- **NÃO REINICIE** desnecessariamente - hot reload está ATIVO!
- Backend: Uvicorn --reload detecta mudanças em .py automaticamente
- Frontend: Vite HMR atualiza instantaneamente no browser
- **SOMENTE** reinicie se mudou .env ou instalou dependências
- Salve arquivo (Ctrl+S) → mudança aplicada em 1-2 segundos

## Build/Lint/Test Commands

### Backend (Python/FastAPI)
- **Single test**: `cd backend && source venv/bin/activate && pytest tests/test_file.py::test_function -v`
- **All tests**: `cd backend && source venv/bin/activate && pytest -v`
- **Lint**: `cd backend && source venv/bin/activate && flake8 .`
- **Format**: `cd backend && source venv/bin/activate && black .`

### Frontend (React/TypeScript)
- **Single test**: `cd frontend && npm test -- --testNamePattern="test name" --testPathPattern=file.test.tsx`
- **All tests**: `cd frontend && npm run test`
- **E2E tests**: `cd frontend && npm run test:e2e`
- **Lint**: `cd frontend && npm run lint`
- **Format**: `cd frontend && npm run format`

## Workflows de Desenvolvimento

### Backend - Novo Endpoint
1. Criar schemas Pydantic (Create/Update/Response)
2. Criar endpoint usando BaseRepository
3. Adicionar dependência `get_current_active_user`
4. Adicionar paginação (skip/limit)
5. Adicionar tratamento de erros (HTTPException)
6. Registrar rota em router.py
7. Criar testes (casos de sucesso + erro)
8. Documentar com docstring em português

### Frontend - Novo Componente
1. Verificar se componente similar já existe
2. Criar interface TypeScript para props
3. Usar apenas Tailwind CSS (sem estilos inline)
4. Tornar reutilizável (aceitar prop className)
5. Manter abaixo de 200 linhas
6. Criar service se precisar de API (usar instância api)
7. Criar hook customizado se lógica complexa
8. Criar testes (renderização + interações)

### Refatoração de Código
1. Identificar código duplicado
2. Criar componente/função reutilizável
3. Substituir todas ocorrências
4. Remover código comentado antigo
5. Limpar imports não utilizados
6. Executar linter (black/prettier)
7. Executar testes para garantir que nada quebrou

## Code Style Guidelines

### Backend (Python)
- **Imports**: Standard library first, then third-party, then local imports (alphabetical within groups)
- **Formatting**: Black (88 chars), 4 spaces indentation
- **Types**: Full type hints on all functions/parameters/returns
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Error handling**: HTTPException with proper status codes, descriptive messages
- **Docstrings**: English, describe what function does, parameters, returns, raises

### Frontend (TypeScript)
- **Imports**: Group by external libraries, then internal modules (relative paths with @/ aliases)
- **Formatting**: Prettier (120 chars), 2 spaces indentation
- **Types**: Strict typing, no `any`, use interfaces for props/objects
- **Naming**: camelCase for variables/functions, PascalCase for components/hooks, UPPER_SNAKE_CASE for constants
- **Error handling**: Try/catch blocks, user-friendly error messages via toast notifications
- **Components**: Functional components with TypeScript interfaces, accept className for styling customization

### General Rules
- **NEVER** use `SELECT *` in SQL queries
- **NEVER** hard delete records (always soft delete with deleted_at)
- **NEVER** create/alter database tables via code (Database First approach)
- **ALWAYS** use BaseRepository for CRUD operations
- **ALWAYS** filter queries by company_id for multi-tenant isolation
- **ALWAYS** remove unused imports and commented code after refactoring

## Tratamento de Dados Sensíveis (LGPD)
- **SEMPRE** implementar mascaramento e formatação na camada de BANCO DE DADOS (SQL Server Views)
- **NUNCA** implementar mascaramento na camada de aplicação (Python/FastAPI)
- Seguir padrão "Database-First Presentation": Views devem retornar dados já formatados/mascarados
- Aplicação deve consumir apenas Views, não tabelas base (para segurança)
- Dados brutos ficam nas tabelas; dados de apresentação ficam nas Views
- Scripts SQL devem ser salvos na pasta `Database/` com numeração sequencial (ex: `035_Fix_Company_View_JSON_Masking.sql`)

## Estrutura de Scripts SQL
- Scripts localizados em: `Database/`
- Numeração sequencial: `001_`, `002_`, etc.
- Nome descritivo em inglês com underscores
- Sempre incluir testes de validação no próprio script
- Usar `FOR JSON PATH` para arrays JSON nativos
- Implementar mascaramento LGPD diretamente no SQL
