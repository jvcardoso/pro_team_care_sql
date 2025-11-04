# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pro Team Care** - Multi-tenant SaaS system for home care management
- **Architecture**: Database First (tables manually created in SQL Server)
- **Stack**: FastAPI (Python) + React (TypeScript) + SQL Server
- **Schema**: `[core]` (main database), `pro_team_care_logs` (separate logging database)

## Commands

### Starting the Application

```bash
# Start both backend and frontend
./start.sh

# Quick start (skip cache cleanup)
./start.sh --skip-cache

# Stop all services
./stop.sh

# Clean cache
./clean_cache.sh
```

### Backend Commands

```bash
cd backend
source venv/bin/activate  # Activate virtual environment

# Run server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ⚡ IMPORTANTE: Flag --reload ativa hot reload
# Não precisa reiniciar ao alterar código Python!
# Mudanças são aplicadas automaticamente.

# Run tests
pytest                              # All tests
pytest tests/test_auth.py -v       # Specific test file
pytest --cov=app --cov-report=html # With coverage report

# Code formatting
black .                             # Format code
flake8 .                            # Lint code
```

### Frontend Commands

```bash
cd frontend

# Development
npm run dev              # Start dev server (port 3000)

# ⚡ IMPORTANTE: Vite tem HMR (Hot Module Replacement)
# Não precisa reiniciar ao alterar código React/TypeScript!
# Mudanças aparecem instantaneamente no browser.

npm run build            # Production build
npm run preview          # Preview production build

# Testing
npm run test             # Jest unit tests
npm run test:e2e         # Playwright E2E tests
npm run test:e2e:ui      # Playwright UI mode
npm run test:api         # Newman API tests
npm run test:all         # All tests

# Code quality
npm run lint             # ESLint
npm run format           # Prettier
```

### OpenCode.ai Commands

This project is configured to work with OpenCode.ai as a full-stack development agent:

```bash
# Start OpenCode.ai server (recommended)
./start_opencode.sh      # Starts server in background
opencode                 # Connect client to server

# Or run OpenCode.ai directly
opencode                 # Interactive mode
opencode "task"          # Direct command

# Stop server
./stop_opencode.sh       # Stop OpenCode.ai server

# Monitor logs
tail -f logs/opencode.log

# Review mode (analyze only, don't write code)
opencode --mode review "analyze security of /auth/login endpoint"
```

**Important:** OpenCode.ai automatically loads `AGENTS.md` with project rules and patterns.

See `docs/OPENCODE_SETUP.md` for detailed setup and usage guide.

### Single Test Execution

```bash
# Backend - Run specific test
cd backend
pytest tests/test_pf_profiles.py::test_create_pf_profile -v

# Frontend - Run specific test file
cd frontend
npm run test -- --testFile=ComponentName.test.ts
```

## Architecture Patterns

### Database First Approach

**CRITICAL**: This project does NOT use migrations or auto-generate tables.

- Tables are created manually in SQL Server
- SQLAlchemy models only MAP to existing tables
- NO Alembic migrations
- NO automatic table creation/alteration

**When adding/modifying tables:**
1. Manually create/alter table in SQL Server
2. Update the corresponding SQLAlchemy model in `backend/app/models/`
3. Update Pydantic schemas in `backend/app/schemas/`

### Backend Architecture (Repository + Service Pattern)

**3-Layer Architecture:**

1. **API Layer** (`app/api/v1/*.py`) - HTTP endpoints, request/response handling
2. **Service Layer** (`app/services/*.py`) - Business logic, validation
3. **Repository Layer** (`app/repositories/*.py`) - Data access

**BaseRepository** provides generic CRUD operations:
- `get_all(skip, limit, include_deleted)` - List records with pagination
- `get_by_id(id, include_deleted)` - Fetch single record
- `create(data)` - Insert new record
- `update(id, data)` - Update existing record
- `delete(id, soft=True)` - Soft delete by default
- `count(include_deleted)` - Count records
- `exists(id)` - Check if record exists

**BaseService** wraps BaseRepository with business logic:
- Always use BaseRepository internally
- Override methods to add validation/business rules
- Handles multi-tenant isolation via company_id

**Example Usage:**
```python
# In API endpoint
from app.repositories.base import BaseRepository
from app.models.user import User

repo = BaseRepository(User, db)
users = await repo.get_all(skip=0, limit=100)
```

### Multi-Tenant Architecture

**Tenant Isolation:**
- `company_id` in most tables for data isolation
- Context-aware filtering in BaseRepository
- JWT tokens contain company_id for automatic filtering

**Session Context for LGPD:**
- Middleware sets SESSION_CONTEXT with user_id
- Used for automatic data masking
- Audit trail for sensitive data access

### Frontend Architecture (Hooks + Services Pattern)

**Structure:**
- **Services** (`src/services/`) - API calls using axios
- **Hooks** (`src/hooks/`) - Reusable stateful logic
- **Components** (`src/components/`) - UI components
- **Pages** (`src/pages/`) - Route-level components
- **Types** (`src/types/`) - TypeScript interfaces

**Common Patterns:**
- Custom hooks for data fetching (`useCrud`, `useDataTable`)
- React Hook Form + Zod for form validation
- Axios with retry logic for API calls
- Tailwind CSS for styling (no inline CSS)

### Soft Delete Pattern

**All tables have `deleted_at` column:**
- Default queries exclude soft-deleted records
- Use `include_deleted=True` to include them
- NEVER use hard delete unless explicitly required
- BaseRepository handles this automatically

### LGPD/Data Privacy

**Automatic Data Masking:**
- Sensitive fields (CPF, RG, etc.) are masked by default
- Use `/reveal` endpoints with audit logging to unmask
- SESSION_CONTEXT tracks who accesses sensitive data
- Logging database (`pro_team_care_logs`) stores audit trails

**Models with LGPD:**
- `pf_profile` (Pessoa Física) - CPF, RG, etc.
- `pj_profile` (Pessoa Jurídica) - CNPJ, etc.
- Consent fields: `lgpd_consent_date`, `data_retention_consent`

## Key Models & Relationships

### Core Entities

**Company** - SaaS tenant
- Status: `pending_contract`, `active`, `suspended`
- Settings stored in JSON column

**Person** - Polymorphic (PF or PJ)
- `person_type`: 'PF' (individual) or 'PJ' (company)
- Base for patients, professionals, clients
- Links to PF_Profile or PJ_Profile

**User** - System accounts
- Links to Person via `person_id`
- Belongs to Company via `company_id`
- Authentication via stored procedure `sp_authenticate_user`

**Establishment** - Company locations/units
- Links to Company and Person (as legal entity)

**Polymorphic Entities:**
- Phone, Email, Address link to multiple entity types via `entity_type` + `entity_id`

### Authentication Flow

1. User submits email + password to `/api/v1/auth/login`
2. Backend calls stored procedure `sp_authenticate_user`
3. If valid, returns JWT token with `user_id` and `company_id`
4. Frontend stores token and includes in Authorization header
5. Middleware extracts token and sets SESSION_CONTEXT

## Configuration

### Backend (.env)

Required variables:
```env
DB_SERVER=192.168.11.84
DB_PORT=1433
DB_NAME=pro_team_care
DB_USER=sa
DB_PASSWORD=YourPassword
DB_SCHEMA=core

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=http://localhost:3000,http://192.168.11.83:3000
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## Code Style & Conventions

### Backend (Python)
- Variables/functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Indentation: 4 spaces
- Formatter: Black (88 chars)
- Linter: Flake8

### Frontend (TypeScript)
- Components: `PascalCase`
- Variables/functions: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Hooks: `use` + `PascalCase`
- Indentation: 2 spaces
- Formatter: Prettier + ESLint

### Documentation
- Docstrings/JSDoc: English
- Business logic comments: Portuguese
- Technical comments: English

## Important Constraints

### What NOT to Do - Backend
- Never create/alter tables via code (Database First!)
- Never use `SELECT *` queries
- Never hard delete (always soft delete via `deleted_at`)
- Never expose sensitive data without LGPD masking
- Never use Alembic or any migration tool

### What NOT to Do - Frontend
- Never hard-code mock data in production
- Never ignore API errors
- Never use `any` in TypeScript
- Never create components over 300 lines
- Never use inline CSS (use Tailwind classes)

## Testing

### Backend Tests
- Location: `backend/tests/`
- Framework: pytest + httpx
- Fixtures: `client`, `auth_token`, `auth_headers`, `db`
- LGPD validation: automatic masking and reveal endpoint tests

### Frontend Tests
- Unit: Jest (`npm run test`)
- E2E: Playwright (`npm run test:e2e`)
- API: Newman/Postman (`npm run test:api`)

## Common Workflows

### Adding a New API Endpoint

1. Create/update Pydantic schema in `backend/app/schemas/[resource].py`
2. Create endpoint in `backend/app/api/v1/[resource].py`
3. Register route in `backend/app/api/v1/router.py`
4. Create tests in `backend/tests/test_[resource].py`
5. Run tests: `pytest tests/test_[resource].py -v`

### Adding a New React Component

1. Create TypeScript types in `frontend/src/types/[name].ts`
2. Create service in `frontend/src/services/[name]Service.ts`
3. Create custom hook in `frontend/src/hooks/use[Name].ts`
4. Create component in `frontend/src/components/[Name].tsx`
5. Create page in `frontend/src/pages/[Name]Page.tsx`
6. Register route in `frontend/src/App.jsx`

### Adding a New Database Table

1. **Manually** create table in SQL Server (schema `[core]`)
2. Create SQLAlchemy model in `backend/app/models/[name].py`
3. Add to `backend/app/models/__init__.py`
4. Create Pydantic schemas (see "Adding a New API Endpoint")

## Security

- JWT tokens expire after 30 minutes
- Passwords hashed with bcrypt
- LGPD automatic masking for sensitive fields
- Multi-tenant isolation via company_id
- Audit logs stored in separate database

## Troubleshooting

### Backend won't start
- Check SQL Server connection in `backend/.env`
- Verify tables exist in database
- Check logs: `tail -f logs/backend.log`

### Frontend won't start
- Verify Node.js 18+ installed
- Check `frontend/.env` has correct `VITE_API_URL`
- Check logs: `tail -f logs/frontend.log`

### Tests failing
- Ensure test database has required tables
- Check fixtures in `backend/tests/conftest.py`
- Verify token generation for auth tests
