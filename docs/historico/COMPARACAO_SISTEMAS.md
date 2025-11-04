# 📊 COMPARAÇÃO: Sistema Antigo vs Sistema Novo

**Data:** 21/10/2025  
**Sistema Antigo:** `/home/juliano/Projetos/pro_team_care_16` (PostgreSQL)  
**Sistema Novo:** `/home/juliano/Projetos/meu_projeto` (SQL Server)

---

## 🔍 ANÁLISE DO SISTEMA ANTIGO

### **Banco de Dados**
- **SGBD:** PostgreSQL 
- **Host:** 192.168.11.62:5432
- **Database:** pro_team_care_11
- **Schema:** master

### **Arquitetura**
- **Clean Architecture** (Domain, Application, Infrastructure, Presentation)
- **FastAPI** com estrutura modular
- **SQLAlchemy** assíncrono
- **Redis** para cache
- **Structured Logging** (structlog)
- **Rate Limiting** configurado
- **Monitoring** com métricas Prometheus

---

## 📋 ENDPOINTS DO SISTEMA ANTIGO

### **✅ Autenticação** (`/auth`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/auth/login` | POST | Login com OAuth2PasswordRequestForm | ✅ Implementado |
| `/auth/register` | POST | Registro de usuário | ✅ Implementado |
| `/auth/refresh` | POST | Refresh token | ❌ **FALTA** |
| `/auth/me` | GET | Dados do usuário logado | ✅ **CRIADO HOJE** |
| `/auth/test` | GET | Test endpoint | ⚠️ Não necessário |
| `/auth/debug-users` | GET | Debug users (DEV) | ⚠️ Não necessário |
| `/auth/reset-admin-password` | POST | Reset senha admin (DEV) | ⚠️ Não necessário |

### **🔐 Password Reset** (`/password-reset`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/password-reset/request` | POST | Solicitar reset de senha | ❌ **FALTA** |
| `/password-reset/verify` | POST | Verificar código | ❌ **FALTA** |
| `/password-reset/reset` | POST | Resetar senha | ❌ **FALTA** |

### **👥 Usuários** (`/users`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/users/` | GET | Listar usuários | ✅ Implementado |
| `/users/{id}` | GET | Obter usuário | ✅ Implementado |
| `/users/` | POST | Criar usuário | ✅ Implementado |
| `/users/{id}` | PUT | Atualizar usuário | ✅ Implementado |
| `/users/{id}` | DELETE | Deletar usuário | ✅ Implementado |
| `/users/{id}/status` | PATCH | Ativar/Inativar | ✅ Implementado |
| `/users/{id}/password` | PATCH | Alterar senha | ✅ Implementado |
| `/users/{id}/roles` | GET | Obter roles | ✅ Implementado |
| `/users/{id}/roles` | PUT | Atualizar roles | ✅ Implementado |

### **🏢 Empresas** (`/companies`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/companies/` | GET | Listar empresas | ✅ Implementado |
| `/companies/{id}` | GET | Obter empresa | ✅ Implementado |
| `/companies/` | POST | Criar empresa | ✅ Implementado |
| `/companies/{id}` | PUT | Atualizar empresa | ✅ Implementado |
| `/companies/{id}` | DELETE | Deletar empresa | ✅ Implementado |
| `/companies/{id}/stats` | GET | Estatísticas | ✅ Implementado |
| `/companies/{id}/contacts` | GET | Contatos | ✅ Implementado |
| `/companies/{id}/reactivate` | PUT | Reativar | ✅ Implementado |
| `/companies/cnpj/{cnpj}` | GET | Buscar por CNPJ | ✅ Implementado |

### **🏪 Estabelecimentos** (`/establishments`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/establishments/` | GET | Listar estabelecimentos | ✅ Implementado |
| `/establishments/{id}` | GET | Obter estabelecimento | ✅ Implementado |
| `/establishments/` | POST | Criar estabelecimento | ✅ Implementado |
| `/establishments/{id}` | PUT | Atualizar estabelecimento | ✅ Implementado |
| `/establishments/{id}` | DELETE | Deletar estabelecimento | ✅ Implementado |

### **🎭 Roles/Permissões** (`/roles`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/roles/` | GET | Listar roles | ❌ **FALTA** |
| `/roles/{id}` | GET | Obter role | ❌ **FALTA** |
| `/roles/` | POST | Criar role | ❌ **FALTA** |
| `/roles/{id}` | PUT | Atualizar role | ❌ **FALTA** |
| `/roles/{id}` | DELETE | Deletar role | ❌ **FALTA** |

### **🔒 Sessões Seguras** (`/secure-sessions`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/secure-sessions/switch-profile` | POST | Trocar perfil | ❌ **FALTA** |
| `/secure-sessions/impersonate` | POST | Personificar usuário | ❌ **FALTA** |
| `/secure-sessions/end-impersonation` | POST | Encerrar personificação | ❌ **FALTA** |

### **📊 Dashboard** (`/dashboard`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/dashboard/stats` | GET | Estatísticas gerais | ❌ **FALTA** |
| `/dashboard/recent-activity` | GET | Atividade recente | ❌ **FALTA** |

### **🔔 Notificações** (`/notifications`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/notifications/` | GET | Listar notificações | ❌ **FALTA** |
| `/notifications/{id}/read` | PUT | Marcar como lida | ❌ **FALTA** |
| `/notifications/mark-all-read` | PUT | Marcar todas como lidas | ❌ **FALTA** |

### **🍔 Menus Dinâmicos** (`/menus`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/menus/` | GET | Listar menus | ❌ **FALTA** |
| `/menus/dynamic` | GET | Menus dinâmicos por role | ❌ **FALTA** |
| `/menus/{id}` | GET | Obter menu | ❌ **FALTA** |
| `/menus/` | POST | Criar menu | ❌ **FALTA** |
| `/menus/{id}` | PUT | Atualizar menu | ❌ **FALTA** |
| `/menus/{id}` | DELETE | Deletar menu | ❌ **FALTA** |

### **🏥 Home Care** (Módulo Completo)
| Módulo | Endpoints | Status Novo |
|--------|-----------|-------------|
| **Clientes** | `/clients/*` | ❌ **FALTA TODO** |
| **Profissionais** | `/professionals/*` | ❌ **FALTA TODO** |
| **Contratos** | `/contracts/*` | ❌ **FALTA TODO** |
| **Autorizações Médicas** | `/medical-authorizations/*` | ❌ **FALTA TODO** |
| **Controle de Limites** | `/limits-control/*` | ❌ **FALTA TODO** |

### **💰 Billing** (3 Sistemas)
| Sistema | Endpoints | Status Novo |
|---------|-----------|-------------|
| **Home Care Billing (B2C)** | `/billing/*` | ❌ **FALTA TODO** |
| **B2B Billing (Legacy)** | `/b2b-billing/*` | ❌ **FALTA TODO** |
| **SaaS Billing (Subscriptions)** | `/saas-billing/*` | ❌ **FALTA TODO** |

### **🔍 CNPJ Lookup** (`/cnpj`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/cnpj/{cnpj}` | GET | Consultar CNPJ (ReceitaWS) | ❌ **FALTA** |
| `/cnpj/enrich` | POST | Enriquecer dados | ❌ **FALTA** |

### **🌍 Geolocalização** (`/geocoding`, `/geolocation`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/geocoding/address` | POST | Geocodificar endereço | ❌ **FALTA** |
| `/geolocation/enrich` | POST | Enriquecer com lat/long | ❌ **FALTA** |

### **🔐 LGPD** (`/lgpd`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/lgpd/companies/{id}/reveal-field` | POST | Revelar campo sensível | ✅ Implementado |
| `/lgpd/companies/{id}/reveal-fields` | POST | Revelar múltiplos campos | ✅ Implementado |
| `/lgpd/companies/{id}/audit-action` | POST | Auditar ação | ✅ Implementado |
| `/lgpd/companies/{id}/audit-log` | GET | Log de auditoria | ✅ Implementado |

### **📧 Contatos** (`/emails`)
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/emails/` | GET | Listar emails | ✅ Implementado |
| `/emails/{id}` | GET | Obter email | ✅ Implementado |
| `/emails/` | POST | Criar email | ✅ Implementado |
| `/emails/{id}` | PUT | Atualizar email | ✅ Implementado |
| `/emails/{id}` | DELETE | Deletar email | ✅ Implementado |

### **🏥 Health & Monitoring**
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/health` | GET | Health check | ✅ Implementado |
| `/health/detailed` | GET | Health detalhado | ✅ Implementado |
| `/metrics` | GET | Métricas Prometheus | ❌ **FALTA** |

### **🔧 Admin & Debug**
| Endpoint | Método | Descrição | Status Novo |
|----------|--------|-----------|-------------|
| `/db-admin/*` | * | Administração DB | ❌ **FALTA** |
| `/system-optimization/*` | * | Otimização sistema | ❌ **FALTA** |
| `/program-codes/*` | * | Códigos de programa | ❌ **FALTA** |

---

## 🎯 DIFERENÇAS PRINCIPAIS

### **1. Endpoint `/auth/me` - Sistema Antigo**

```python
@router.get("/me", response_model=None)
async def read_users_me(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """Get current user profile with database connection"""
    
    # Retorna dados COMPLETOS:
    return {
        "id": user_row.id,
        "email_address": user_row.email_address,
        "full_name": user_row.full_name,  # ⚠️ JOIN com people
        "is_active": user_row.is_active,
        "is_system_admin": user_row.is_system_admin,
        "created_at": user_row.created_at,
        "updated_at": user_row.updated_at,
        "company_id": user_row.company_id,
        "establishment_id": user_row.establishment_id,
        "context_type": user_row.context_type,  # ⚠️ Novo campo
        "company_name": user_row.company_name,  # ⚠️ JOIN com companies
        "establishment_name": user_row.establishment_name,  # ⚠️ JOIN com establishments
        "establishments": establishments,  # ⚠️ Lista de estabelecimentos da empresa
    }
```

### **2. Endpoint `/auth/me` - Sistema Novo (Criado Hoje)**

```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint para obter dados do usuário logado."""
    return current_user  # ⚠️ Retorna apenas dados da tabela users
```

**❌ FALTA:**
- `full_name` (JOIN com people)
- `company_name` (JOIN com companies)
- `establishment_name` (JOIN com establishments)
- `context_type` (campo novo)
- `establishments` (lista de estabelecimentos)

---

## 🔧 FUNCIONALIDADES CRÍTICAS FALTANDO

### **1. Refresh Token** ⚠️ **CRÍTICO**
- Sistema antigo: `/auth/refresh` funcional
- Sistema novo: Endpoint não existe
- **Impacto:** Usuário precisa fazer login novamente quando token expira

### **2. Password Reset** ⚠️ **CRÍTICO**
- Sistema antigo: Fluxo completo (request → verify → reset)
- Sistema novo: Não existe
- **Impacto:** Usuário não consegue recuperar senha

### **3. Roles/Permissões** ⚠️ **CRÍTICO**
- Sistema antigo: Sistema completo de roles e permissões
- Sistema novo: Não existe
- **Impacto:** Controle de acesso limitado (apenas is_system_admin)

### **4. Sessões Seguras** ⚠️ **IMPORTANTE**
- Sistema antigo: Troca de perfil, personificação
- Sistema novo: Não existe
- **Impacto:** Suporte técnico não consegue personificar usuários

### **5. Dashboard** ⚠️ **IMPORTANTE**
- Sistema antigo: Estatísticas e atividade recente
- Sistema novo: Não existe
- **Impacto:** Falta visão geral do sistema

### **6. Notificações** ⚠️ **IMPORTANTE**
- Sistema antigo: Sistema completo de notificações
- Sistema novo: Não existe
- **Impacto:** Usuários não recebem alertas

### **7. Menus Dinâmicos** ⚠️ **IMPORTANTE**
- Sistema antigo: Menus baseados em roles
- Sistema novo: Não existe
- **Impacto:** Menu estático, sem controle por perfil

### **8. Home Care (Módulo Completo)** ⚠️ **NEGÓCIO**
- Sistema antigo: Clientes, Profissionais, Contratos, Autorizações, Limites
- Sistema novo: Não existe
- **Impacto:** Funcionalidade principal do negócio ausente

### **9. Billing (3 Sistemas)** ⚠️ **NEGÓCIO**
- Sistema antigo: B2C, B2B, SaaS
- Sistema novo: Não existe
- **Impacto:** Sem faturamento

### **10. CNPJ Lookup** ⚠️ **ÚTIL**
- Sistema antigo: Integração com ReceitaWS
- Sistema novo: Não existe
- **Impacto:** Cadastro manual de empresas

### **11. Geolocalização** ⚠️ **ÚTIL**
- Sistema antigo: Geocodificação automática
- Sistema novo: Não existe
- **Impacto:** Sem lat/long automático

### **12. Monitoring/Metrics** ⚠️ **OPS**
- Sistema antigo: Prometheus metrics, system monitoring
- Sistema novo: Não existe
- **Impacto:** Sem monitoramento de performance

---

## 📊 RESUMO ESTATÍSTICO

### **Endpoints Implementados**
| Categoria | Antigo | Novo | % Implementado |
|-----------|--------|------|----------------|
| **Autenticação** | 7 | 3 | 43% |
| **Usuários** | 9 | 9 | 100% ✅ |
| **Empresas** | 9 | 9 | 100% ✅ |
| **Estabelecimentos** | 5 | 5 | 100% ✅ |
| **Pessoas** | 5 | 5 | 100% ✅ |
| **LGPD** | 4 | 4 | 100% ✅ |
| **Contatos (Emails)** | 5 | 5 | 100% ✅ |
| **Roles/Permissões** | 5 | 0 | 0% ❌ |
| **Password Reset** | 3 | 0 | 0% ❌ |
| **Sessões Seguras** | 3 | 0 | 0% ❌ |
| **Dashboard** | 2 | 0 | 0% ❌ |
| **Notificações** | 3 | 0 | 0% ❌ |
| **Menus** | 6 | 0 | 0% ❌ |
| **Home Care** | ~30 | 0 | 0% ❌ |
| **Billing** | ~20 | 0 | 0% ❌ |
| **CNPJ** | 2 | 0 | 0% ❌ |
| **Geolocalização** | 2 | 0 | 0% ❌ |
| **Monitoring** | 2 | 0 | 0% ❌ |

### **Total Geral**
- **Endpoints Antigo:** ~120+
- **Endpoints Novo:** ~50
- **% Implementado:** ~42%

---

## 🎯 PRIORIDADES PARA MVP

### **🔴 CRÍTICO (Sem isso não funciona)**
1. ✅ `/auth/me` com dados completos (full_name, company_name, etc.)
2. ❌ `/auth/refresh` - Refresh token
3. ❌ `/password-reset/*` - Recuperação de senha
4. ❌ `/roles/*` - Sistema de permissões

### **🟡 IMPORTANTE (Funcionalidade esperada)**
5. ❌ `/secure-sessions/*` - Troca de perfil
6. ❌ `/dashboard/*` - Dashboard básico
7. ❌ `/notifications/*` - Notificações
8. ❌ `/menus/*` - Menus dinâmicos

### **🟢 NEGÓCIO (Core business)**
9. ❌ `/clients/*` - Clientes Home Care
10. ❌ `/professionals/*` - Profissionais
11. ❌ `/contracts/*` - Contratos
12. ❌ `/billing/*` - Faturamento

### **🔵 ÚTIL (Nice to have)**
13. ❌ `/cnpj/*` - Lookup CNPJ
14. ❌ `/geocoding/*` - Geolocalização
15. ❌ `/metrics` - Monitoramento

---

## 🔄 MIGRAÇÃO POSTGRESQL → SQL SERVER

### **Diferenças Importantes**

| Aspecto | PostgreSQL (Antigo) | SQL Server (Novo) |
|---------|---------------------|-------------------|
| **Schema** | `master` | `core` |
| **Soft Delete** | `deleted_at IS NULL` | `deleted_at IS NULL` ✅ |
| **Timestamps** | `NOW()` | `GETDATE()` |
| **Auto Increment** | `SERIAL` | `IDENTITY` |
| **Boolean** | `BOOLEAN` | `BIT` |
| **Text** | `TEXT` | `NVARCHAR(MAX)` |
| **JSON** | `JSONB` | `NVARCHAR(MAX)` (JSON) |
| **Arrays** | `ARRAY` | `STRING_SPLIT` ou tabela relacionada |
| **Stored Procedures** | Sim | ✅ Sim (já implementadas) |

---

## 📝 PRÓXIMOS PASSOS RECOMENDADOS

### **Fase 1: Corrigir MVP Básico (1-2 dias)**
1. ✅ Corrigir `/auth/me` para retornar dados completos
2. ❌ Implementar `/auth/refresh`
3. ❌ Implementar `/password-reset/*`
4. ❌ Implementar sistema básico de roles

### **Fase 2: Funcionalidades Importantes (3-5 dias)**
5. ❌ Implementar `/secure-sessions/*`
6. ❌ Implementar `/dashboard/*`
7. ❌ Implementar `/notifications/*`
8. ❌ Implementar `/menus/*`

### **Fase 3: Core Business (2-3 semanas)**
9. ❌ Migrar módulo Home Care completo
10. ❌ Migrar sistema de Billing
11. ❌ Implementar integrações externas (CNPJ, Geocoding)

### **Fase 4: Otimização (1 semana)**
12. ❌ Implementar monitoring/metrics
13. ❌ Otimizar queries
14. ❌ Adicionar cache Redis
15. ❌ Testes E2E completos

---

## 🎉 CONCLUSÃO

**Status Atual:** MVP Básico (~42% do sistema antigo)

**O que funciona:**
- ✅ Login/Registro
- ✅ CRUD de Usuários, Empresas, Estabelecimentos, Pessoas
- ✅ LGPD/Auditoria
- ✅ Soft Delete

**O que falta:**
- ❌ Refresh token
- ❌ Password reset
- ❌ Roles/Permissões
- ❌ Dashboard
- ❌ Notificações
- ❌ Menus dinâmicos
- ❌ Módulo Home Care (core business)
- ❌ Sistema de Billing
- ❌ Integrações externas

**Recomendação:** Priorizar Fase 1 (MVP Básico) antes de adicionar novas features.

---

**Última atualização:** 21/10/2025 14:30 BRT
