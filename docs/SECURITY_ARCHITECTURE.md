# Arquitetura de Segurança - Pro Team Care

Documentação da arquitetura de segurança e logging do sistema.

---

## 🎯 Visão Geral

O sistema implementa uma arquitetura de segurança robusta com **banco de dados dedicado para logs** e **stored procedure centralizada** para autenticação.

### Benefícios da Arquitetura

1. **Proteção contra Limite do SQL Server Express** - Logs isolados não comprometem os 10GB do banco principal
2. **Performance** - Operações de log não competem com transações de negócio
3. **Auditoria Completa** - Histórico detalhado de todas as tentativas de login
4. **Segurança Centralizada** - Lógica de autenticação no banco de dados (stored procedure)
5. **Desacoplamento** - Políticas de retenção independentes para cada banco

---

## 🗄️ Arquitetura de Bancos de Dados

### Banco Principal: `pro_team_care`

**Propósito:** Dados operacionais e transacionais

**Tabelas:**
- `[core].companies` - Empresas (tenants)
- `[core].people` - Pessoas físicas e jurídicas
- `[core].establishments` - Estabelecimentos
- `[core].roles` - Papéis e permissões
- `[core].users` - Usuários do sistema
- `[core].user_roles` - Atribuição de papéis
- `[core].phones` - Telefones polimórficos
- `[core].emails` - Emails polimórficos
- `[core].addresses` - Endereços polimórficos

**Stored Procedures:**
- `[core].sp_execute_login` - Autenticação centralizada

### Banco de Logs: `pro_team_care_logs`

**Propósito:** Auditoria e logs de alto volume

**Tabelas:**
- `[core].login_logs` - Histórico de tentativas de login

**Características:**
- Append-only (apenas inserções)
- Sem foreign keys (desacoplamento)
- Índices otimizados para consultas de auditoria
- Políticas de retenção independentes

---

## 🔐 Fluxo de Autenticação

### 1. Requisição de Login

```
POST /api/v1/auth/login
{
  "email_address": "usuario@example.com",
  "password": "senha123"
}
```

### 2. Processamento no Backend (FastAPI)

```python
# backend/app/api/v1/auth.py

1. Extrai IP e User-Agent da requisição
2. Chama AuthService.execute_login()
3. AuthService executa a stored procedure
4. Processa resultado da SP
5. Gera JWT token se sucesso
6. Retorna resposta HTTP
```

### 3. Stored Procedure `[core].[sp_execute_login]`

**Localização:** Banco `pro_team_care`

**Parâmetros:**
- `@email_attempted` - Email fornecido
- `@password_attempted` - Senha em texto plano
- `@ip_address` - IP de origem
- `@user_agent` - User-Agent do cliente

**Lógica:**

```sql
BEGIN TRANSACTION;

1. Busca usuário por email
   - Se não encontrado → Log de FAILED (company_id NULL)

2. Se usuário encontrado mas INATIVO
   - Log de INACTIVE_USER_ATTEMPT

3. Compara senha usando PWDCOMPARE (seguro)
   - Se incorreta → Log de FAILED

4. Se tudo OK
   - Atualiza last_login_at
   - Log de SUCCESS

COMMIT TRANSACTION;

RETURN {user_id, company_id, status, message}
```

### 4. Registro de Log

**Banco:** `pro_team_care_logs`
**Tabela:** `[core].login_logs`

**Campos registrados:**
```sql
{
  id: 1,
  company_id: 5,           -- NULL se email não encontrado
  user_id: 42,             -- NULL se email não encontrado
  email_attempted: "usuario@example.com",
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  status: "SUCCESS",       -- SUCCESS | FAILED | INACTIVE_USER_ATTEMPT
  failure_reason: NULL,    -- INVALID_CREDENTIALS | USER_INACTIVE
  session_id: NULL,
  created_at: "2025-10-19 14:30:00"
}
```

---

## 💻 Implementação no Backend

### Conexões de Banco de Dados

#### Conexão Principal

```python
# backend/app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(settings.DATABASE_URL)
# Conecta em: pro_team_care
```

#### Conexão de Logs

```python
# backend/app/core/database_logs.py

from sqlalchemy.ext.asyncio import create_async_engine

logs_engine = create_async_engine(settings.DATABASE_LOGS_URL)
# Conecta em: pro_team_care_logs
```

### Model LoginLog

```python
# backend/app/models/login_log.py

class LoginLog(LogsBase):
    __tablename__ = "login_logs"
    __table_args__ = {"schema": "core"}

    # Aponta para o banco pro_team_care_logs via LogsBase
```

### Service de Autenticação

```python
# backend/app/services/auth_service.py

class AuthService:
    async def execute_login(self, email, password, ip, user_agent):
        # Executa EXEC [core].[sp_execute_login]
        # Processa resultado
        # Gera JWT token se sucesso
        # Retorna dict com resultado
```

### Endpoint de Login

```python
# backend/app/api/v1/auth.py

@router.post("/login")
async def login(credentials, request, db):
    # Obtém IP e User-Agent
    auth_service = AuthService(db)
    result = await auth_service.execute_login(...)

    # Retorna token JWT ou erro HTTP
```

---

## 📊 Queries de Auditoria

### Listar Tentativas de Login por Usuário

```sql
SELECT
    email_attempted,
    status,
    ip_address,
    created_at
FROM pro_team_care_logs.[core].login_logs
WHERE user_id = 42
ORDER BY created_at DESC;
```

### Analisar Tentativas Falhadas por IP

```sql
SELECT
    ip_address,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_attempts
FROM pro_team_care_logs.[core].login_logs
WHERE created_at >= DATEADD(hour, -24, GETDATE())
GROUP BY ip_address
HAVING SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) > 5;
```

### Logins por Empresa (últimas 24h)

```sql
SELECT
    c.id as company_id,
    p.name as company_name,
    COUNT(*) as login_count
FROM pro_team_care_logs.[core].login_logs ll
JOIN pro_team_care.[core].users u ON ll.user_id = u.id
JOIN pro_team_care.[core].companies c ON u.company_id = c.id
JOIN pro_team_care.[core].people p ON c.person_id = p.id
WHERE ll.status = 'SUCCESS'
  AND ll.created_at >= DATEADD(hour, -24, GETDATE())
GROUP BY c.id, p.name
ORDER BY login_count DESC;
```

---

## 🛡️ Boas Práticas de Segurança

### ✅ Implementado

1. **Senha hashada no banco** - Nunca armazenada em texto plano
2. **Comparação segura** - `PWDCOMPARE()` do SQL Server
3. **Log completo** - Todas as tentativas registradas
4. **Rastreamento de IP** - Identificação de origem
5. **User-Agent** - Identificação de cliente
6. **Transação atômica** - Login e log em uma única transação
7. **Isolamento de dados** - Banco separado para logs

### 🔜 Melhorias Futuras

1. **Rate Limiting** - Limitar tentativas por IP
2. **Bloqueio temporário** - Bloquear IP após N falhas
3. **Two-Factor Authentication (2FA)** - Autenticação de dois fatores
4. **Session Management** - Controle de sessões ativas
5. **Password Policy** - Política de senhas fortes
6. **Expiração de senhas** - Renovação periódica
7. **Alertas de segurança** - Notificações de tentativas suspeitas

---

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Banco Principal
DB_SERVER=192.168.11.84
DB_NAME=pro_team_care
DB_SCHEMA=core

# Banco de Logs
DB_LOGS_NAME=pro_team_care_logs
DB_LOGS_SCHEMA=core
```

### Scripts SQL Necessários

1. `001_create_logs_database.sql` - Cria banco pro_team_care_logs
2. `002_create_login_logs_table.sql` - Cria tabela login_logs
3. `003_create_sp_execute_login.sql` - Cria stored procedure

---

## 📈 Métricas de Performance

### Vantagens da Stored Procedure

1. **Menos round-trips** - 1 chamada vs 3-4 queries separadas
2. **Transação atômica** - Garantia de consistência
3. **Execução no servidor** - Processamento mais rápido
4. **Compilação otimizada** - Plano de execução em cache

### Impacto no Banco de Logs

- **Crescimento estimado:** ~500 bytes por login
- **Volume mensal (1000 usuários):** ~15 MB/mês
- **Limite de 10GB:** ~666 meses de dados (55 anos)

---

## 🔍 Troubleshooting

### Erro: "Could not connect to logs database"

**Causa:** Banco `pro_team_care_logs` não existe

**Solução:**
```sql
-- Execute o script de criação do banco
USE master;
CREATE DATABASE pro_team_care_logs;
```

### Erro: "Stored procedure not found"

**Causa:** SP `sp_execute_login` não foi criada

**Solução:**
```sql
-- Execute o script de criação da SP no banco principal
USE pro_team_care;
-- (executar script 011_Create_Login_Stored_Procedure.sql)
```

### Erro: "Login failed but no log entry"

**Causa:** Transação foi revertida (ROLLBACK)

**Solução:** Verificar logs de erro do SQL Server
```sql
SELECT * FROM sys.messages WHERE severity > 16;
```

---

## 📚 Referências

- [SQL Server Stored Procedures Best Practices](https://docs.microsoft.com/sql/relational-databases/stored-procedures/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [JWT Authentication](https://jwt.io/introduction)
