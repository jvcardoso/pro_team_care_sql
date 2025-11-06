# Pro Team Care - Sistema SaaS Multi-tenant

Sistema web full-stack com FastAPI (Python) + React (TypeScript) + SQL Server.

**Arquitetura:** Database First (tabelas criadas manualmente no SQL Server)

---

## Stack Tecnológico

### Backend
- **Framework:** FastAPI 0.109
- **Linguagem:** Python 3.11+
- **ORM:** SQLAlchemy (async)
- **Banco de Dados:** SQL Server (schema `[core]`)
- **Autenticação:** JWT (python-jose)
- **Validação:** Pydantic

### Frontend
- **Framework:** React 18
- **Linguagem:** TypeScript 5
- **Build Tool:** Vite 5
- **Estilização:** Tailwind CSS 3
- **Roteamento:** React Router DOM 6
- **HTTP Client:** Axios

---

## Características

✅ **Database First** - Controle total sobre o schema SQL
✅ **Multi-tenant** - Sistema SaaS com isolamento por empresa
✅ **Componentes Reutilizáveis** - Button, Input, Table, Modal genéricos
✅ **CRUD Genérico** - BaseRepository e BaseService
✅ **Hooks Customizados** - useApi, useCrud, useAuth
✅ **Responsive Design** - Mobile-first com Tailwind
✅ **Soft Delete** - Exclusão lógica em todas as tabelas
✅ **JWT Authentication** - Login seguro com tokens
✅ **Colunas JSON** - Flexibilidade para configurações e metadados
✅ **LGPD Ready** - Campos de consentimento e retenção de dados
✅ **Arquitetura de Logs** - Banco dedicado para auditoria
✅ **Stored Procedure Auth** - Autenticação centralizada e segura

---

## Estrutura do Banco de Dados

### Schema: `[core]`

| Tabela | Descrição |
|--------|-----------|
| **companies** | Empresas clientes (tenants) do sistema SaaS |
| **people** | Pessoas Físicas (PF) e Jurídicas (PJ) - polimórfico |
| **establishments** | Estabelecimentos/unidades de uma empresa |
| **roles** | Papéis/permissões do sistema |
| **users** | Contas de usuários |
| **user_roles** | Atribuição de papéis a usuários com contexto |
| **phones** | Telefones polimórficos (Person, Establishment, etc) |
| **emails** | Emails polimórficos (Person, Establishment, etc) |
| **addresses** | Endereços polimórficos (Person, Establishment, etc) |

Ver documentação completa: [DATABASE_STRUCTURE.md](docs/DATABASE_STRUCTURE.md)

---

## Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- SQL Server (com banco `pro_team_care` já criado)
- Git

### 1. Clonar Repositório

```bash
git clone <url-do-repo>
cd meu_projeto
```

### 2. Configurar Backend

**Windows:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Editar `backend/.env`:**
```env
DB_SERVER=192.168.11.84
DB_PORT=1433
DB_NAME=pro_team_care
DB_USER=sa
DB_PASSWORD=SuaSenha
DB_SCHEMA=core
```

### 3. Configurar Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

### 4. Iniciar Servidores

**Windows:**
```cmd
scripts\start_all.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### 5. Acessar Aplicação

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## Comandos Úteis

### Scripts Rápidos (Linux/Mac)

```bash
./start.sh              # Iniciar tudo
./start.sh -s           # Início rápido (sem cache)
./stop.sh               # Parar tudo
./clean_cache.sh        # Limpar cache
tail -f logs/backend.log   # Ver logs backend
tail -f logs/frontend.log  # Ver logs frontend

# OpenCode.ai (dev full-stack com IA)
./start_opencode.sh     # Iniciar servidor OpenCode.ai
./stop_opencode.sh      # Parar servidor OpenCode.ai
tail -f logs/opencode.log  # Ver logs OpenCode.ai
```

### Scripts Windows

```cmd
scripts\start_all.bat          # Iniciar tudo
scripts\start_backend.bat      # Apenas backend
scripts\start_frontend.bat     # Apenas frontend
```

### Backend (Manual)

```bash
cd backend
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload

# ⚡ Flag --reload = hot reload ativo
# NÃO precisa reiniciar ao alterar código!
```

### Testes Automatizados

```bash
cd backend
./run_tests.sh                # Executar todos os testes
./run_tests.sh --coverage     # Com relatório de cobertura
./run_tests.sh --verbose      # Modo verbose
```

### Frontend (Manual)

```bash
cd frontend
npm install
npm run dev    # Vite com HMR - hot reload ativo

# ⚡ Vite HMR = NÃO precisa reiniciar!
# Mudanças aparecem instantaneamente.

npm run build
```

---

## Estrutura do Projeto

```
meu_projeto/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── core/        # Config, database, security
│   │   ├── models/      # SQLAlchemy models (schema [core])
│   │   │   ├── company.py
│   │   │   ├── person.py
│   │   │   ├── establishment.py
│   │   │   ├── role.py
│   │   │   ├── user.py
│   │   │   └── user_role.py
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── repositories/ # Data access layer (BaseRepository)
│   │   ├── services/    # Business logic (BaseService)
│   │   ├── api/v1/      # REST endpoints
│   │   └── main.py      # Entry point
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── components/  # Componentes reutilizáveis
│   │   ├── pages/       # Páginas
│   │   ├── services/    # API services
│   │   ├── hooks/       # Custom hooks (useCrud, useApi, useAuth)
│   │   └── types/       # TypeScript types
│   └── package.json
│
├── docs/                # Documentação
│   ├── DATABASE_STRUCTURE.md
│   ├── SETUP.md
│   └── PROJETO_IA.md
│
├── scripts/             # Scripts Windows (.bat)
├── start.sh             # Script Linux/Mac para iniciar
├── stop.sh              # Script para parar
└── clean_cache.sh       # Script para limpar cache
```

---

## Documentação

- **[DATABASE_STRUCTURE.md](docs/DATABASE_STRUCTURE.md)** - Estrutura completa do banco
- **[SECURITY_ARCHITECTURE.md](docs/SECURITY_ARCHITECTURE.md)** - Arquitetura de segurança e logs
- **[API_TESTING.md](docs/API_TESTING.md)** - Guia de testes da API
- **[SETUP.md](docs/SETUP.md)** - Guia de instalação detalhado
- **[PROJETO_IA.md](docs/PROJETO_IA.md)** - Documentação para IAs

---

## ⚠️ Database First - Importante

Este projeto usa a abordagem **Database First**:

1. ✅ Tabelas foram criadas **manualmente** no SQL Server
2. ✅ Models SQLAlchemy apenas **mapeiam** as tabelas existentes
3. ✅ **NENHUM** código cria ou altera tabelas automaticamente
4. ❌ **NÃO HÁ** migrations (Alembic)
5. ❌ **NÃO HÁ** scripts SQL no código

**Se precisar adicionar/alterar tabelas:**
1. Altere no SQL Server manualmente
2. Atualize o model SQLAlchemy correspondente
3. Atualize os schemas Pydantic

---

## API Endpoints

### Autenticação

```
POST /api/v1/auth/login     - Login
POST /api/v1/auth/register  - Registro
```

### Usuários

```
GET    /api/v1/users        - Listar usuários
GET    /api/v1/users/{id}   - Buscar usuário
POST   /api/v1/users        - Criar usuário
PUT    /api/v1/users/{id}   - Atualizar usuário
DELETE /api/v1/users/{id}   - Deletar usuário (soft delete)
```

### Companies

```
GET    /api/v1/companies/complete-list     - Listar companies (dados completos com LGPD)
GET    /api/v1/companies                   - Listar companies (dados básicos) ⚠️ DEPRECATED
GET    /api/v1/companies/{id}              - Buscar company detalhada
GET    /api/v1/companies/{id}/contacts     - Buscar contatos da empresa (telefones/emails)
POST   /api/v1/companies/complete          - Criar company completa (JSON aninhado)
POST   /api/v1/companies                   - Criar company básica ⚠️ DEPRECATED
PUT    /api/v1/companies/{id}/complete     - Atualizar company completa
PUT    /api/v1/companies/{id}              - Atualizar company básica ⚠️ DEPRECATED
DELETE /api/v1/companies/{id}              - Deletar company (soft delete)
```

### LGPD (Auditoria e Dados Sensíveis)

```
POST   /api/v1/lgpd/companies/{id}/reveal-field     - Revelar campo sensível único
POST   /api/v1/lgpd/companies/{id}/reveal-fields    - Revelar múltiplos campos sensíveis
POST   /api/v1/lgpd/companies/{id}/audit-action     - Auditar ação sensível
GET    /api/v1/lgpd/companies/{id}/audit-log        - Listar logs de auditoria LGPD
```

### Telefones

```
GET    /api/v1/phones        - Listar telefones
GET    /api/v1/phones/{id}   - Buscar telefone
POST   /api/v1/phones        - Criar telefone
PUT    /api/v1/phones/{id}   - Atualizar telefone
DELETE /api/v1/phones/{id}   - Deletar telefone (soft delete)
```

### Emails

```
GET    /api/v1/emails        - Listar emails
GET    /api/v1/emails/{id}   - Buscar email
POST   /api/v1/emails        - Criar email
PUT    /api/v1/emails/{id}   - Atualizar email
DELETE /api/v1/emails/{id}   - Deletar email (soft delete)
```

### Endereços

```
GET    /api/v1/addresses        - Listar endereços
GET    /api/v1/addresses/{id}   - Buscar endereço
POST   /api/v1/addresses        - Criar endereço
PUT    /api/v1/addresses/{id}   - Atualizar endereço
DELETE /api/v1/addresses/{id}   - Deletar endereço (soft delete)
```

Documentação completa em: http://localhost:8000/docs

---

## Código Reutilizável

### Backend - CRUD Genérico

```python
# Funciona para QUALQUER tabela!
from app.repositories.base import BaseRepository
from app.models.user import User

repo = BaseRepository(User, db)
users = await repo.get_all()
user = await repo.get_by_id(1)
await repo.create({...})
await repo.update(1, {...})
await repo.delete(1)  # soft delete
```

### Frontend - Hook CRUD

```typescript
// Funciona para QUALQUER endpoint!
import { useCrud } from './hooks/useCrud';

const users = useCrud<User>('/users');
await users.list();
await users.create({...});
await users.update(1, {...});
await users.remove(1);
```

---

## Testes Automatizados

### Configuração de Testes

O projeto inclui testes automatizados com **pytest + httpx** para validar endpoints da API.

#### 1. Instalação das Dependências de Teste

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt  # Já inclui pytest e httpx
```

#### 2. Executar Todos os Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Modo verbose
pytest -v

# Executar testes específicos
pytest tests/test_auth.py -v
pytest tests/test_pf_profiles.py -v
```

#### 3. Estrutura de Testes

```
backend/tests/
├── __init__.py
├── conftest.py          # Configuração global (fixtures)
├── test_auth.py         # Testes de autenticação
├── test_pf_profiles.py  # Testes PF com LGPD
└── test_pj_profiles.py  # Testes PJ com LGPD
```

#### 4. Fixtures Disponíveis

- **`client`**: Cliente HTTP para testar endpoints
- **`auth_token`**: Token JWT válido (mock para desenvolvimento)
- **`auth_headers`**: Headers com Authorization Bearer
- **`db`**: Sessão de banco para testes

#### 5. Testes LGPD

Os testes incluem validação específica da segurança LGPD:

- **Mascaramento automático**: Verifica se dados sensíveis vêm mascarados
- **Revelação controlada**: Testa endpoints `/reveal` com auditoria
- **Controle de acesso**: Valida isolamento por empresa e permissões

#### 6. Executar Testes em CI/CD

```yaml
# Exemplo GitHub Actions
- name: Run Tests
  run: |
    cd backend
    python -m pytest --cov=app --cov-report=xml
```

---

## Licença

MIT

---

## Suporte

Para dúvidas ou problemas, consulte a documentação em `docs/`.

## Claude
claude --dangerously-skip-permissions

## gemini (somente)
Prompt de Atuação: Arquiteto de Banco de Dados e Software - Pro Team Care

  1. Papel Principal

  Atuarei como Arquiteto de Software Sênior e de Banco de Dados para o projeto "Pro Team Care". Minha responsabilidade abrange a integridade, performance
   e segurança da arquitetura de dados e sua interação com a aplicação (FastAPI, React).

  2. Diretriz Arquitetônica Central

  Aderir rigorosamente ao padrão "Database-First Presentation". O banco de dados SQL Server é a única fonte da verdade e o cérebro do sistema. Toda a
  lógica de negócio, regras de validação, e especialmente a lógica de apresentação e mascaramento de dados (para conformidade com a LGPD), devem ser
  implementadas diretamente no banco de dados através de Stored Procedures, Views, Functions e Triggers. A aplicação deve ser uma consumidora passiva
  dos dados já processados e seguros.

  3. Responsabilidades como "Dono do Banco de Dados"

   * Integridade Absoluta: Sou o guardião final do schema do banco de dados. Minha palavra e minhas verificações determinam a estrutura correta.
   * Centralização da Lógica: Vetar ativamente qualquer tentativa de implementar lógica de negócio crítica ou manipulação de dados sensíveis nas camadas
     de aplicação (Python/React).
   * Performance e Otimização: Garantir que as queries, views e procedures sejam performáticas e escaláveis.

  4. Regras de Ouro Operacionais (Lições Aprendidas)

   * REGRA #1: INSPECIONAR ANTES DE CODIFICAR. Antes de escrever ou modificar qualquer script SQL (DDL ou DML), a primeira ação obrigatória é inspecionar
      o schema real das tabelas envolvidas usando queries de sistema (sys.tables, sys.columns). Nunca assumirei a estrutura de uma tabela.
   * REGRA #2: NÃO CONFIAR, VERIFICAR. Documentação, planos e até mesmo scripts anteriores são guias, não a verdade absoluta. A verdade reside no schema
     atual do banco de dados. Devo verificar ativamente para evitar a repetição de erros baseados em informações desatualizadas.
   * REGRA #3: CONEXÃO CORRETA E SEGURA. Para executar scripts SQL, utilizarei o comando sqlcmd com as credenciais e flags que estabelecemos funcionarem,
      garantindo a conexão bem-sucedida:

   1     sqlcmd -S 192.168.11.84,1433 -U sa -P "Jvc@1702" -d pro_team_care -N -C

  5. Fluxo de Trabalho Padrão para Tarefas de Banco de Dados

  Para toda nova demanda que envolva o banco de dados, seguirei este processo:

   1. Análise da Solicitação: Entender o objetivo de negócio.
   2. Inspeção do Schema: Executar queries para verificar os tipos de dados, nomes de colunas, chaves e constraints das tabelas relevantes.
   3. Elaboração do Script: Escrever o script SQL com base na verdade fundamental do schema.
   4. Execução Controlada: Executar o script no ambiente de desenvolvimento.
   5. Verificação e Validação: Confirmar que a alteração foi aplicada corretamente e não introduziu efeitos colaterais, executando queries de verificação

## solictar commit 
Execute o fluxo de "Commit Assistido". Siga estes passos rigorosamente:

   1. Análise Silenciosa: Execute git status --short e git diff para analisar todas as alterações de código pendentes. Não mostre o output bruto destes comandos.

   2. Geração da Mensagem: Com base na sua análise do diff, formule uma mensagem de commit concisa e informativa, seguindo o padrão de Commits Semânticos (ex: feat(escopo): 
      descrição). A mensagem deve incluir um título e, se aplicável, um corpo com os principais pontos da mudança.

   3. Pedido de Validação: Apresente ao usuário um resumo claro contendo:
       * A lista de arquivos que foram alterados.
       * A mensagem de commit que você sugeriu.
       * Uma pergunta direta pedindo aprovação para criar o commit (ex: "Posso prosseguir com o commit?").

   4. Execução Pós-Aprovação:
       * NÃO FAÇA NADA sem a aprovação explícita do usuário.
       * Se o usuário aprovar, execute git add . e git commit com a mensagem aprovada.
       * Após o commit ser bem-sucedido, pergunte se um git push também deve ser executado.

**REGRAS OBRIGATÓRIAS (Padrão Pro Team Care):**

1.  **MASCARAMENTO (Consulta):**
    * Toda lógica de mascaramento de dados sensíveis (LGPD) DEVE ser implementada usando **Funções T-SQL** (ex: `[core].[fn_MaskEmail]`).
    * Todas as APIs de `GET` (listagem/consulta) DEVERÃO consumir **Views T-SQL** (ex: `[core].[vw_complete_company_data]` ou `[core].[vw_addresses]`).
    * Essas `Views` DEVEM usar as `Funções` de mascaramento para que os dados já saiam do banco mascarados.
    * O usuário da API (`app_user`) NUNCA deve ter permissão de `SELECT` direto nas tabelas base (ex: `core.emails`, `core.addresses`).

2.  **REVELAÇÃO (Desmascarar):**
    * A revelação de um dado sensível é um evento controlado e auditado.
    * A API (FastAPI) NÃO deve fazer `SELECT` direto. Ela DEVE chamar um **Stored Procedure T-SQL** (ex: `[core].[sp_RevealAndLog]`) para buscar o dado bruto.

3.  **AUDITORIA (O Pilar do Log):**
    * O `Stored Procedure` de revelação DEVE, obrigatoriamente, executar um `INSERT` na tabela `[core].[lgpd_audit_log]` *ANTES* de executar o `SELECT` que retorna o dado bruto. A auditoria é atômica e inseparável da revelação.

4.  **FRONTEND (React):**
    * O Frontend é "burro" (thin client). Ele NUNCA implementa lógica de mascaramento. Ele apenas exibe os dados (que já vêm mascarados da View) ou chama os endpoints de revelação (que ativam o Stored Procedure) quando necessário.
