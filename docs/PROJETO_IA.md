# Documentação para IAs - Meu Projeto

Documentação simplificada para IAs entenderem e trabalharem com este projeto.

---

## Visão Geral do Projeto

**Sistema web full-stack com arquitetura Database First:**
- Backend: FastAPI + Python + SQLAlchemy (async)
- Frontend: React + TypeScript + Tailwind CSS
- Banco: SQL Server 2025
- Abordagem: **Database First** (tabelas criadas manualmente)

---

## Arquitetura - Database First

### ⚠️ REGRA FUNDAMENTAL

**O CÓDIGO NUNCA CRIA TABELAS AUTOMATICAMENTE**

- Tabelas são criadas manualmente no SQL Server via scripts `.sql`
- Os models SQLAlchemy apenas MAPEIAM tabelas existentes
- Se uma tabela não existir, o código retorna erro (proposital)

### Workflow

```
1. DBA/Dev cria tabela no SQL Server (scripts sql_scripts/)
2. Dev cria model SQLAlchemy correspondente (app/models/)
3. Dev cria schema Pydantic (app/schemas/)
4. Dev cria endpoint FastAPI (app/api/)
5. Frontend usa endpoint via hooks reutilizáveis
```

---

## Estrutura de Código Reutilizável

### Backend: Classes Base

**BaseRepository** (`app/repositories/base.py`):
```python
# CRUD genérico para QUALQUER tabela
repo = BaseRepository(User, db)
users = await repo.get_all()
user = await repo.get_by_id(1)
await repo.create({...})
await repo.update(1, {...})
await repo.delete(1)  # soft delete automático
```

**BaseService** (`app/services/base.py`):
```python
# Lógica de negócio genérica
service = BaseService(BaseRepository, User, db)
users = await service.list_all()
```

### Frontend: Hooks Reutilizáveis

**useCrud** (`hooks/useCrud.ts`):
```typescript
// CRUD completo para QUALQUER endpoint
const users = useCrud<User>('/users');

await users.list();           // GET /users
await users.get(1);           // GET /users/1
await users.create({...});    // POST /users
await users.update(1, {...}); // PUT /users/1
await users.remove(1);        // DELETE /users/1

// States automáticos
users.data      // Array de itens
users.loading   // Boolean
users.error     // String ou null
users.total     // Contagem total
```

**useApi** (`hooks/useApi.ts`):
```typescript
// Wrapper genérico para chamadas API
const api = useApi<User>();
await api.execute(() => axios.get('/users'));
// api.data, api.loading, api.error
```

**useAuth** (`hooks/useAuth.ts`):
```typescript
// Autenticação
const { login, logout, isAuthenticated } = useAuth();
await login({ email, password });
```

### Frontend: Componentes Genéricos

**Table** (`components/shared/Table.tsx`):
```typescript
// Tabela genérica com loading, empty state, actions
<Table
  data={users.data}
  columns={[
    { key: 'id', header: 'ID' },
    { key: 'name', header: 'Nome' },
    { key: 'email', header: 'Email' }
  ]}
  loading={users.loading}
  actions={(user) => <Button onClick={() => delete(user.id)}>Excluir</Button>}
/>
```

**Button, Input, Modal, Card** - Todos reutilizáveis e estilizados.

---

## Como Adicionar Nova Funcionalidade

### Exemplo: Adicionar CRUD de "Produtos"

#### 1. Criar tabela no SQL Server

```sql
-- backend/sql_scripts/004_create_products.sql
CREATE TABLE dbo.products (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    deleted_at DATETIME2 NULL
);
```

Executar no SSMS.

#### 2. Criar Model

```python
# backend/app/models/product.py
from sqlalchemy import Column, String, Numeric
from .base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    __table_args__ = {"schema": "dbo"}

    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
```

#### 3. Criar Schema

```python
# backend/app/schemas/product.py
from pydantic import BaseModel
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    price: Decimal

class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True
```

#### 4. Criar Endpoint

```python
# backend/app/api/v1/products.py
from fastapi import APIRouter, Depends
from app.repositories.base import BaseRepository
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Produtos"])

@router.get("", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(Product, db)
    return await repo.get_all()

@router.post("", response_model=ProductResponse)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(Product, db)
    return await repo.create(data.model_dump())
```

Adicionar ao router principal:
```python
# backend/app/api/v1/router.py
from . import products
api_router.include_router(products.router)
```

#### 5. Usar no Frontend

```typescript
// frontend/src/types/product.types.ts
export interface Product {
  id: number;
  name: string;
  price: number;
}

// frontend/src/pages/ProductsPage.tsx
import { useCrud } from '../hooks/useCrud';

export const ProductsPage = () => {
  const products = useCrud<Product>('/products');

  useEffect(() => {
    products.list();
  }, []);

  return (
    <Table
      data={products.data}
      columns={[
        { key: 'id', header: 'ID' },
        { key: 'name', header: 'Nome' },
        { key: 'price', header: 'Preço' }
      ]}
      loading={products.loading}
    />
  );
};
```

**Pronto!** CRUD completo funcionando.

---

## Padrões de Código

### Backend

- **Models:** Apenas mapeiam tabelas (NUNCA criam)
- **Schemas:** Validação Pydantic
- **Repositories:** Acesso a dados (usa BaseRepository)
- **Services:** Lógica de negócio (usa BaseService)
- **API:** Endpoints FastAPI (chama services)

### Frontend

- **Hooks:** useApi, useCrud, useAuth
- **Components:** Reutilizáveis e genéricos
- **Pages:** Composição de components + hooks
- **Services:** Axios configurado com interceptors

### Convenções

- Soft delete em tudo (campo `deleted_at`)
- Timestamps automáticos (`created_at`, `updated_at`)
- JWT para autenticação
- Paginação em listas (skip, limit)
- Erros HTTP padronizados

---

## Arquivos Importantes

### Backend

| Arquivo | Função |
|---------|--------|
| `app/core/config.py` | Configurações e variáveis de ambiente |
| `app/core/database.py` | Engine SQLAlchemy (NÃO cria tabelas) |
| `app/core/security.py` | JWT e bcrypt |
| `app/repositories/base.py` | CRUD genérico reutilizável |
| `app/services/base.py` | Service genérico reutilizável |
| `app/main.py` | Entry point FastAPI |
| `sql_scripts/*.sql` | Scripts de criação de tabelas |

### Frontend

| Arquivo | Função |
|---------|--------|
| `hooks/useCrud.ts` | CRUD genérico reutilizável |
| `hooks/useApi.ts` | Wrapper API com states |
| `hooks/useAuth.ts` | Autenticação |
| `services/api.ts` | Axios configurado (interceptors) |
| `components/shared/*` | Componentes reutilizáveis |
| `App.tsx` | Roteamento |

---

## Comandos Rápidos

```bash
# Setup inicial
scripts\setup_env.bat

# Iniciar tudo
scripts\start_all.bat

# Backend apenas
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload

# Frontend apenas
cd frontend && npm run dev

# Executar SQL
sqlcmd -S servidor -U user -P pass -d banco -i script.sql
```

---

## Checklist para IAs

Ao modificar este projeto:

- [ ] ✅ NUNCA adicionar código que crie tabelas automaticamente
- [ ] ✅ Sempre criar script SQL primeiro (em `sql_scripts/`)
- [ ] ✅ Reutilizar BaseRepository/BaseService (não duplicar código)
- [ ] ✅ Usar hooks useCrud/useApi no frontend (não criar novos)
- [ ] ✅ Manter soft delete em todas as tabelas
- [ ] ✅ Adicionar timestamps (created_at, updated_at, deleted_at)
- [ ] ✅ Usar Pydantic schemas para validação
- [ ] ✅ Documentar endpoints no Swagger (automático)
- [ ] ✅ Componentes frontend devem ser reutilizáveis
- [ ] ✅ Manter responsividade mobile-first

---

## Filosofia do Projeto

**Princípios:**

1. **Database First** - DBA controla schema
2. **DRY (Don't Repeat Yourself)** - Código reutilizável
3. **Simplicidade** - Evitar over-engineering
4. **Manutenibilidade** - Código claro e direto
5. **Responsividade** - Funciona em todos os dispositivos

**O que EVITAR:**

- ❌ Migrations automáticas (Alembic)
- ❌ ORM que cria tabelas (type-orm auto-sync)
- ❌ Código duplicado entre CRUDs
- ❌ Componentes específicos não reutilizáveis
- ❌ Dados mockados (sempre do banco)

---

## Status do Projeto

- ✅ Backend funcional (FastAPI + SQL Server)
- ✅ Frontend funcional (React + TypeScript)
- ✅ Autenticação JWT
- ✅ CRUD de Users e Companies
- ✅ Componentes reutilizáveis
- ✅ Hooks customizados
- ✅ Scripts SQL de exemplo
- ✅ Documentação completa

**Pronto para uso e extensão!**
