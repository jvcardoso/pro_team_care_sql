# 💾 MEMORIES - PRO TEAM CARE

**Contexto persistente do projeto para Cascade**

---

## 🏥 Domínio do Negócio

**Sistema:** SaaS Multi-tenant para gestão de Home Care
**Modelo:** B2B - Empresas de cuidados domiciliares são clientes
**Usuários finais:** Profissionais de saúde, pacientes, administradores

---

## 🎯 Decisões Arquiteturais (Por quê?)

### Database First (não Code First)
- **Por quê:** DBA gerencia schema, stored procedures críticas, índices otimizados
- **Impacto:** NUNCA criar migrations, tabelas criadas manualmente no SQL Server
- **Quando mudar DB:** Alterar no SSMS → Atualizar model SQLAlchemy → Atualizar schema Pydantic

### Multi-tenant com company_id
- **Por quê:** Isolamento de dados, billing separado, escalabilidade horizontal
- **Impacto:** Todas queries filtram por company_id automaticamente
- **Contexto JWT:** Token contém company_id do usuário logado

### BaseRepository/BaseService Pattern
- **Por quê:** Elimina 90% do código CRUD duplicado
- **Onde usar:** SEMPRE para novas entidades
- **Exceção:** Queries muito complexas (usar raw SQL)

### Soft Delete Obrigatório
- **Por quê:** LGPD, auditoria, recuperação de dados
- **Implementação:** Campo deleted_at em TODAS tabelas
- **Nunca:** Hard delete (DELETE FROM)

### Autenticação via Stored Procedure
- **Por quê:** Performance crítica, validações centralizadas no DB
- **SP:** `sp_authenticate_user` valida credenciais
- **Retorno:** user_id, company_id, role → JWT token

---

## 📊 Entidades Core (Modelo de Dados)

### Company (Tenant)
- Cliente do SaaS
- Status: `pending_contract`, `active`, `suspended`
- Settings JSON: configurações personalizadas por cliente

### Person (Polimórfico PF/PJ)
- `person_type`: 'PF' (pessoa física) ou 'PJ' (pessoa jurídica)
- Base para: Patient, Professional, Client
- Relacionamento 1:1 com PF_Profile ou PJ_Profile

### User (Autenticação)
- Vinculado a Person e Company
- `context`: system, admin, professional, patient
- Password hash bcrypt, JWT 30min

### Establishment
- Unidades/filiais de uma Company
- Vinculado a Person (como entidade jurídica)

### Polymorphic (Phone, Email, Address)
- Reutilizáveis: ligam a Person, Company, Establishment
- Campos: `entity_type`, `entity_id`

---

## 🔒 LGPD (Específico do Projeto)

### Mascaramento Automático
- PF_Profile: CPF, RG mascarados por VIEW
- PJ_Profile: CNPJ mascarado
- SESSION_CONTEXT: user_id define quem acessa

### Revelação Controlada
- Endpoint `/reveal` para dados completos
- Auditoria em banco `pro_team_care_logs`
- Apenas roles autorizados

### Campos LGPD
- `lgpd_consent_date`: quando aceitou
- `data_retention_consent`: quanto tempo manter
- `consent_withdrawn_at`: revogou consentimento

---

## 📁 Estrutura Crítica

### Backend
```
backend/app/
├── core/
│   ├── config.py          # Settings (DB_SERVER, SECRET_KEY, CORS)
│   ├── database.py        # AsyncSessionLocal, get_db()
│   └── security.py        # JWT encode/decode
├── models/                # SQLAlchemy (mapeia tabelas existentes)
├── schemas/               # Pydantic (validação request/response)
├── repositories/          # BaseRepository (CRUD genérico)
│   └── base.py           # get_all(), get_by_id(), create(), update(), delete()
├── services/              # BaseService (lógica negócio)
│   └── base.py           # Usa BaseRepository internamente
└── api/v1/
    ├── router.py         # Registra todos routers
    └── [recurso].py      # Endpoints específicos
```

### Frontend
```
frontend/src/
├── services/             # API calls (axios)
│   └── api.ts           # Instância axios com interceptors
├── hooks/                # Custom hooks
│   ├── useCrud.ts       # CRUD genérico (reutilizar!)
│   └── useAuth.ts       # Autenticação
├── components/shared/    # Componentes reutilizáveis
└── types/               # TypeScript interfaces
```

---

## 🛠️ Padrões de Código do Projeto

### Backend - Novo Endpoint
```python
# SEMPRE usar BaseRepository
from app.repositories.base import BaseRepository
from app.models.resource import Resource

repo = BaseRepository(Resource, db)
items = await repo.get_all(skip=0, limit=100)
```

### Frontend - Novo Service
```typescript
// SEMPRE usar instância api (tem interceptors)
import { api } from './api';

export const resourceService = {
  async getAll() {
    const { data } = await api.get('/api/v1/resource');
    return data;
  }
};
```

### Frontend - CRUD Reutilizável
```typescript
// JÁ EXISTE useCrud - usar ao invés de duplicar!
import { useCrud } from '@/hooks/useCrud';

const resources = useCrud<Resource>('/resources');
// Tem: list(), create(), update(), remove()
```

---

## ⚠️ Problemas Comuns (Tribal Knowledge)

### "Table not found"
- Causa: Tabela não existe no SQL Server
- Solução: Criar manualmente no SSMS antes de mapear model

### "FOREIGN KEY constraint failed"
- Causa: company_id ou person_id não existe
- Solução: Criar Company/Person primeiro

### "JWT token expired"
- Causa: 30 minutos de expiração
- Solução: Implementar refresh token (pendente)

### Stored Procedure não encontrada
- Causa: Schema errado (usar [core].[sp_name])
- Solução: `await db.execute(text("EXEC [core].[sp_authenticate_user] ..."))`

### CORS error
- Causa: Frontend URL não em CORS_ORIGINS
- Solução: Adicionar em backend/.env

---

## 🚀 Comandos Projeto-Específicos

### Iniciar tudo
```bash
./start.sh              # Backend + Frontend
./start.sh --skip-cache # Pula limpeza cache (mais rápido)
```

### ⚡ Hot Reload (NÃO precisa reiniciar!)
```bash
# Backend: uvicorn --reload ativo
# Altere .py → salva → recarrega automaticamente

# Frontend: Vite HMR ativo
# Altere .tsx → salva → atualiza instantaneamente no browser

# ÚNICO motivo para reiniciar:
# - Mudança em .env
# - Mudança em requirements.txt
# - Mudança em package.json
```

### Debugar erro backend
```bash
tail -f logs/backend.log | grep -i error
```

### Testar endpoint específico
```bash
cd backend && source venv/bin/activate
pytest tests/test_auth.py::test_login -v
```

### Ver queries SQL executadas
```python
# Adicionar em endpoint temporariamente
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

---

## 🔍 Onde Buscar Código Similar

Antes de criar novo código, verificar:

**Formulário de endereço?** → Verificar `AddressForm.tsx`
**Validação CPF/CNPJ?** → Verificar `utils/validators.ts` ou `validators.py`
**Hook de listagem?** → Usar `useCrud` existente
**Endpoint CRUD?** → Copiar padrão de `api/v1/companies.py`
**Formatação de dado?** → Verificar `utils/formatters.ts`

---

## 📌 Convenções Específicas

### Naming
- Tabelas DB: `snake_case` (users, pf_profiles)
- Models Python: `PascalCase` (User, PfProfile)
- Schemas: `[Model]Create`, `[Model]Update`, `[Model]Response`
- Componentes React: `PascalCase` (UserCard)
- Hooks: `use[Name]` (useAuth, useCrud)

### Paths
- API base: `http://localhost:8000/api/v1/`
- Frontend: `http://localhost:3000`
- Swagger: `http://localhost:8000/docs`

### Database
- Schema principal: `[core]`
- Schema logs: `[core]` no DB `pro_team_care_logs`
- Conexão: SQL Server na `192.168.11.84:1433`

---

**Limite:** 6000 caracteres | **Atual:** ~4900 caracteres | **Status:** ✅ OK
