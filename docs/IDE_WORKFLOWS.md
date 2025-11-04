# 🔄 WORKFLOWS - PRO TEAM CARE

## Workflow 1: Criar Nova API Rota

**Trigger:** "Criar endpoint [MÉTODO] /api/v1/[recurso]"

### Passos:

1. **Criar Schema Pydantic** (`backend/app/schemas/[recurso].py`)
   - Criar classes de Request e Response
   - Usar Field() para validações
   - Herdar de BaseModel

2. **Criar Endpoint** (`backend/app/api/v1/[recurso].py`)
   - Usar BaseRepository(Model, db) para CRUD
   - Decorar com @router.get/post/put/delete
   - Adicionar dependency get_current_active_user
   - Documentar com docstrings

3. **Registrar Rota** (`backend/app/api/v1/router.py`)
   - Adicionar: `router.include_router(recurso_router)`

4. **Criar Testes** (`backend/tests/test_[recurso].py`)
   - Testar CRUD completo
   - Usar fixtures: client, auth_headers
   - Testar casos de erro (404, 401, 422)

5. **Executar Testes**
   ```bash
   cd backend
   source venv/bin/activate
   pytest tests/test_[recurso].py -v
   ```

---

## Workflow 2: Criar Componente React

**Trigger:** "Criar componente [Nome]"

### Passos:

1. **Criar Types** (`frontend/src/types/[nome].ts`)
   - Definir interfaces TypeScript
   - Exportar tipos de Request/Response
   - Usar tipos do backend como referência

2. **Criar Service** (`frontend/src/services/[nome]Service.ts`)
   - Importar api instance do axios
   - Criar métodos: getAll, getById, create, update, delete
   - Usar tipos TypeScript nos retornos

3. **Criar Hook** (`frontend/src/hooks/use[Nome].ts`)
   - useState para data, loading, error
   - useEffect para carregar dados
   - Funções para CRUD
   - Retornar { data, loading, error, refresh, create, update, delete }

4. **Criar Componente** (`frontend/src/components/[Nome].tsx`)
   - Componente funcional com TypeScript
   - Props tipadas com interface
   - Usar Tailwind CSS para estilo
   - Componente reutilizável (<300 linhas)

5. **Criar Página** (`frontend/src/pages/[Nome]Page.tsx`)
   - Usar o hook customizado
   - Integrar componentes
   - Adicionar tratamento de erros

6. **Registrar Rota** (`frontend/src/App.jsx`)
   - Adicionar <Route path="/[nome]" element={<[Nome]Page />} />

---

## Workflow 3: Refatorar Código

**Trigger:** "Refatorar [arquivo/função]"

### Passos:

1. **Analisar** code smells (complexidade, nomes ruins)
2. **Criar/Atualizar Testes** (garantir cobertura)
3. **Aplicar Refatoração** (extrair métodos, renomear)
4. **Executar Testes** (validar comportamento)
5. **Documentar Mudanças** (atualizar comentários)

---

## Workflow 4: Adicionar Nova Tabela

**Trigger:** "Adicionar tabela [nome]"

### Passos:

1. **⚠️ CRÍTICO: Criar tabela MANUALMENTE no SQL Server**
   - Conectar no SQL Server Management Studio
   - Criar tabela no schema [core]
   - Incluir: id, created_at, updated_at, deleted_at
   - Incluir company_id para multi-tenant
   - Criar índices necessários

2. **Criar Model SQLAlchemy** (`backend/app/models/[nome].py`)
   - Herdar de Base
   - __tablename__ = '[nome]'
   - __table_args__ = {'schema': 'core'}
   - Mapear TODAS as colunas existentes
   - NUNCA criar colunas novas aqui
   - Adicionar relationships se necessário

3. **Registrar Model** (`backend/app/models/__init__.py`)
   - Importar o novo model

4. **Criar Schemas Pydantic** (ver Workflow 1)
   - [Nome]Create, [Nome]Update, [Nome]Response

5. **Criar Endpoints e Testes** (ver Workflow 1)
   - Endpoints CRUD completos
   - Testes unitários

---

## Workflow 5: Documentar Código

**Trigger:** "Documentar [arquivo]"

### Passos:

1. **Ler Código** (analisar métodos públicos)
2. **Gerar Docstrings** (Backend - Google Style)
3. **Gerar JSDoc** (Frontend)
4. **Atualizar README** (se necessário)
