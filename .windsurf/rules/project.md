# 📋 RULES - PRO TEAM CARE

## Stack Tecnológico

### Backend
- FastAPI 0.109 + Python 3.11+
- SQLAlchemy 2.0 (async) + SQL Server
- JWT Authentication + Pydantic Validation
- pytest + httpx para testes

### Frontend
- React 18 + TypeScript 5 + Vite 5
- Tailwind CSS 3 + React Router DOM 6
- Axios + React Hook Form + Zod
- Jest + Playwright para testes

## Arquitetura

- **Database First**: Tabelas criadas manualmente no SQL Server
- **Multi-tenant SaaS**: Isolamento por company_id
- **Repository Pattern**: BaseRepository para dados
- **Service Layer**: BaseService para lógica
- **Soft Delete**: Todas as tabelas têm deleted_at

## Nomenclatura

### Backend (Python)
- Variáveis/Funções: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Tabelas/Colunas DB: `snake_case`

### Frontend (TypeScript)
- Componentes: `PascalCase`
- Variáveis/Funções: `camelCase`
- Constantes: `UPPER_SNAKE_CASE`
- Hooks: `use` + `PascalCase`

## Formatação

### Backend
- Black (88 caracteres)
- Flake8 (PEP8)
- 4 espaços de indentação

### Frontend
- Prettier + ESLint
- 120 caracteres
- 2 espaços de indentação

## Comentários

- Docstrings/JSDoc em inglês
- Lógica de negócio em português
- Comentários técnicos em inglês

## O QUE NÃO FAZER

### Backend
- ❌ NUNCA criar/alterar tabelas via código
- ❌ NUNCA usar migrations (Alembic)
- ❌ NUNCA fazer SELECT *
- ❌ NUNCA hard delete (sempre soft delete)
- ❌ NUNCA expor dados sensíveis sem LGPD

### Frontend
- ❌ NUNCA hard-code dados mockados
- ❌ NUNCA ignorar erros de API
- ❌ NUNCA usar `any` em TypeScript
- ❌ NUNCA componentes com +300 linhas
- ❌ NUNCA CSS inline (usar Tailwind)

## Testes

### Backend
```bash
cd backend
source venv/bin/activate  # Ativar ambiente virtual primeiro

# Testes
pytest                              # Todos os testes
pytest tests/test_file.py -v       # Arquivo específico
pytest tests/test_auth.py::test_login -v  # Teste específico
pytest --cov=app --cov-report=html # Com cobertura
pytest -x                           # Parar no primeiro erro
pytest -k "test_create"            # Rodar testes que contém "test_create"
```

### Frontend
```bash
cd frontend
npm run test              # Jest unit tests
npm run test:e2e          # Playwright E2E
npm run test:e2e:ui       # Playwright modo UI
npm run test:api          # Newman/Postman
npm run test:all          # Todos os testes
```

## Segurança

- JWT com expiração de 30 minutos
- Password hashing com bcrypt
- Mascaramento LGPD automático
- Isolamento multi-tenant por company_id
- Stored procedure para autenticação (sp_authenticate_user)
- SESSION_CONTEXT para auditoria de acesso
- Banco de logs separado (pro_team_care_logs)

## Comandos Úteis

### Iniciar Projeto
```bash
./start.sh              # Iniciar tudo (backend + frontend)
./start.sh --skip-cache # Início rápido sem limpar cache
./stop.sh               # Parar tudo
./clean_cache.sh        # Limpar cache Python e Node
```

### Logs
```bash
tail -f logs/backend.log   # Ver logs do backend em tempo real
tail -f logs/frontend.log  # Ver logs do frontend em tempo real
```

### Backend - Desenvolvimento
```bash
cd backend
source venv/bin/activate

# Instalar/atualizar dependências
pip install -r requirements.txt

# Rodar servidor manualmente
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ⚡ Flag --reload ativa - NÃO precisa reiniciar ao alterar código!

# Formatação e linting
black .                 # Formatar código
flake8 .                # Verificar PEP8
```

### Frontend - Desenvolvimento
```bash
cd frontend

# Instalar/atualizar dependências
npm install

# Rodar servidor manualmente
npm run dev             # Porta 3000

# ⚡ Vite HMR ativo - NÃO precisa reiniciar ao alterar código!
# Mudanças em React/TypeScript aparecem instantaneamente.

# Build
npm run build           # Produção
npm run preview         # Preview do build

# Formatação e linting
npm run lint            # ESLint
npm run format          # Prettier
```
