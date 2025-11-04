# GEMINI.md - Pro Team Care Development Guide

Este arquivo configura o comportamento do Gemini Code Assist e Gemini CLI para o projeto Pro Team Care.

## Comunicação
- **SEMPRE** responda em português brasileiro (pt-BR)
- Use português para comentários de negócio e commits
- Use inglês apenas para docstrings e documentação técnica

## Contexto do Projeto

**Pro Team Care** - Sistema SaaS multi-tenant para gestão de home care
- **Arquitetura**: Database First (tabelas criadas manualmente no SQL Server)
- **Stack**: FastAPI (Python) + React (TypeScript) + SQL Server
- **Schema**: `[core]` (banco principal), `pro_team_care_logs` (banco de logs)

## ⚡ Hot Reload (IMPORTANTE!)
- **NÃO REINICIE** desnecessariamente - hot reload está ATIVO!
- Backend: Uvicorn --reload detecta mudanças em .py automaticamente
- Frontend: Vite HMR atualiza instantaneamente no browser
- **SOMENTE** reinicie se mudou .env ou instalou dependências
- Salve arquivo (Ctrl+S) → mudança aplicada em 1-2 segundos

## Estrutura de Diretórios

```
meu_projeto/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # Endpoints REST
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── repositories/# Data access layer
│   │   └── core/        # Config, database, dependencies
│   └── tests/           # Testes pytest
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # Componentes React
│       ├── pages/       # Páginas
│       ├── services/    # API clients
│       ├── hooks/       # Custom hooks
│       └── types/       # TypeScript types
└── Database/            # Scripts SQL numerados
```

## Padrões de Arquitetura

### Backend - Repository + Service Pattern

**3 Camadas:**
1. **API Layer** - Endpoints HTTP
2. **Service Layer** - Lógica de negócio
3. **Repository Layer** - Acesso a dados

**BaseRepository** (usar SEMPRE):
- `get_all(skip, limit, include_deleted)`
- `get_by_id(id, include_deleted)`
- `create(data)`
- `update(id, data)`
- `delete(id, soft=True)` - Soft delete por padrão

### Frontend - Hooks + Services Pattern

- **Services** → Chamadas API (axios)
- **Hooks** → Lógica stateful reutilizável
- **Components** → Componentes UI
- **Pages** → Componentes de rota

## Code Style Guidelines

### Backend (Python)
- **Formatação**: Black (88 chars), 4 espaços
- **Type hints**: Obrigatório em todas funções
- **Naming**:
  - `snake_case` para variáveis/funções
  - `PascalCase` para classes
  - `UPPER_SNAKE_CASE` para constantes
- **Imports**: stdlib → third-party → local (alfabético)

### Frontend (TypeScript)
- **Formatação**: Prettier (120 chars), 2 espaços
- **Types**: Strict typing, NUNCA usar `any`
- **Naming**:
  - `camelCase` para variáveis/funções
  - `PascalCase` para componentes/hooks
  - `UPPER_SNAKE_CASE` para constantes
- **Styling**: Tailwind CSS apenas (sem inline CSS)

## Regras CRÍTICAS (NUNCA fazer)

### Backend
- ❌ NUNCA criar/alterar tabelas via código (Database First!)
- ❌ NUNCA usar `SELECT *`
- ❌ NUNCA hard delete (sempre soft delete com `deleted_at`)
- ❌ NUNCA queries diretas (usar BaseRepository)
- ❌ NUNCA usar Alembic ou migrations

### Frontend
- ❌ NUNCA usar `any` em TypeScript
- ❌ NUNCA CSS inline (usar Tailwind)
- ❌ NUNCA componentes > 200 linhas
- ❌ NUNCA ignorar erros de API
- ❌ NUNCA mock data hardcoded em produção

### Geral
- ❌ NUNCA deixar código comentado (usar git history)
- ❌ NUNCA deixar imports não usados
- ❌ NUNCA ignorar warnings do linter

## Tratamento de Dados Sensíveis (LGPD)

- **SEMPRE** implementar mascaramento no **BANCO DE DADOS** (Views SQL)
- **NUNCA** implementar mascaramento na aplicação (Python/FastAPI)
- Seguir padrão "Database-First Presentation"
- Views devem retornar dados já formatados/mascarados
- Scripts SQL em `Database/` com numeração sequencial

## Workflows de Desenvolvimento

### Novo Endpoint API
1. Criar schemas Pydantic (Create/Update/Response)
2. Criar endpoint usando BaseRepository
3. Adicionar `get_current_active_user` dependency
4. Adicionar paginação (skip/limit)
5. Tratar erros (HTTPException com status codes)
6. Registrar rota em router.py
7. Criar testes (sucesso + erro + edge cases)
8. Documentar com docstring

### Novo Componente React
1. Verificar se similar já existe
2. Criar interface TypeScript para props
3. Usar Tailwind CSS (sem inline)
4. Tornar reutilizável (aceitar `className` prop)
5. Manter < 200 linhas
6. Criar service se precisar de API
7. Criar hook customizado se lógica complexa
8. Criar testes

### Refatoração
1. Identificar código duplicado
2. Criar componente/função reutilizável
3. Substituir todas ocorrências
4. Remover código comentado
5. Limpar imports não usados
6. Executar linter (black/prettier)
7. Rodar testes

## Comandos Importantes

### Backend
```bash
cd backend && source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pytest tests/test_file.py::test_function -v
black .
flake8 .
```

### Frontend
```bash
cd frontend
npm run dev
npm test -- --testNamePattern="test name"
npm run lint
npm run format
```

## Multi-Tenant & Segurança

- Isolamento via `company_id` em tabelas
- JWT tokens com `user_id` e `company_id`
- SESSION_CONTEXT para auditoria LGPD
- Soft delete obrigatório (`deleted_at`)
- Mascaramento automático de dados sensíveis

## Testes

### Backend (pytest)
- Casos de sucesso (200, 201)
- Casos de erro (401, 404, 422)
- Edge cases (valores vazios, null, extremos)
- Cobertura mínima: 80%

### Frontend (Jest + Testing Library)
- Renderização correta
- Interações do usuário
- Estados diferentes (loading, error)
- Edge cases (valores vazios, null)

## Checklist Antes de Finalizar

- [ ] Código similar reutilizado (não duplicado)?
- [ ] Imports limpos (sem não usados)?
- [ ] Código comentado removido?
- [ ] Linter passou sem warnings?
- [ ] Testes rodaram e passaram?
- [ ] Type hints completos (Python) ou types (TypeScript)?
- [ ] Documentação adequada (docstrings/JSDoc)?

## Referências Rápidas

- **Documentação completa**: `CLAUDE.md`
- **Rules do OpenCode**: `AGENTS.md`
- **Setup do OpenCode**: `docs/OPENCODE_SETUP.md`
- **Commands Claude Code**: `.claude/commands/`

---

**Versão**: 1.0
**Última atualização**: Janeiro 2025
**Objetivo**: Sincronizar comportamento entre Gemini, Claude Code e OpenCode
