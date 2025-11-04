# Guia de Testes da API - Pro Team Care

Guia completo para testar os endpoints da API.

---

## 🚀 Teste Rápido de Login

### Opção 1: Script Automatizado (RECOMENDADO)

```bash
cd ~/Projetos/meu_projeto
./test_login.sh
```

**Resultado esperado:**

```
✅ LOGIN BEM-SUCEDIDO!

🎫 Token JWT recebido:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

🔐 Payload do JWT (decodificado):
{
  "sub": "1",
  "company_id": null,
  "email": "admin@proteamcare.com.br",
  "exp": 1234567890
}
```

---

### Opção 2: curl Manual

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }'
```

**Resposta esperada:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiY29tcGFueV9pZCI6bnVsbCwiZW1haWwiOiJhZG1pbkBwcm90ZWFtY2FyZS5jb20uYnIiLCJleHAiOjE3MzQ1NDYxMjB9.xxx",
  "token_type": "bearer"
}
```

---

### Opção 3: Swagger UI (Interface Gráfica)

1. Abra: http://localhost:8000/docs
2. Expanda **POST /api/v1/auth/login**
3. Clique em **"Try it out"**
4. Insira as credenciais:
   ```json
   {
     "email_address": "admin@proteamcare.com.br",
     "password": "admin123"
   }
   ```
5. Clique em **"Execute"**

---

## 🧪 Testes Completos

### 1. Teste de Login com Sucesso

**Requisição:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }'
```

**Resultado esperado:**
- ✅ HTTP 200 OK
- ✅ Token JWT retornado
- ✅ Log de sucesso gravado no banco `pro_team_care_logs`

**Validar no banco:**

```sql
-- Verificar último login
SELECT TOP 1 *
FROM pro_team_care_logs.[core].login_logs
ORDER BY created_at DESC;

-- Deve mostrar:
-- status: 'SUCCESS'
-- user_id: 1
-- email_attempted: 'admin@proteamcare.com.br'
```

---

### 2. Teste de Login com Senha Incorreta

**Requisição:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "senhaerrada"
  }'
```

**Resultado esperado:**
- ❌ HTTP 401 Unauthorized
- ❌ Mensagem: "Email ou senha inválidos"
- ✅ Log de falha gravado no banco

**Validar no banco:**

```sql
SELECT TOP 1 *
FROM pro_team_care_logs.[core].login_logs
WHERE email_attempted = 'admin@proteamcare.com.br'
ORDER BY created_at DESC;

-- Deve mostrar:
-- status: 'FAILED'
-- failure_reason: 'INVALID_CREDENTIALS'
```

---

### 3. Teste de Login com Email Inexistente

**Requisição:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "naoexiste@email.com",
    "password": "qualquer"
  }'
```

**Resultado esperado:**
- ❌ HTTP 401 Unauthorized
- ❌ Mensagem: "Email ou senha inválidos"
- ✅ Log gravado com `user_id = NULL`

**Validar no banco:**

```sql
SELECT TOP 1 *
FROM pro_team_care_logs.[core].login_logs
WHERE email_attempted = 'naoexiste@email.com'
ORDER BY created_at DESC;

-- Deve mostrar:
-- status: 'FAILED'
-- user_id: NULL
-- company_id: NULL
```

---

### 4. Teste de Login com Usuário Inativo

**Preparação:**

```sql
-- Desativar o usuário temporariamente
UPDATE [core].[users]
SET is_active = 0
WHERE email_address = 'admin@proteamcare.com.br';
```

**Requisição:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }'
```

**Resultado esperado:**
- ❌ HTTP 401 Unauthorized
- ❌ Mensagem: "Este usuário está inativo e não pode fazer login"
- ✅ Log com `status = 'INACTIVE_USER_ATTEMPT'`

**Reativar o usuário:**

```sql
UPDATE [core].[users]
SET is_active = 1
WHERE email_address = 'admin@proteamcare.com.br';
```

---

### 5. Teste de Uso do Token JWT

**Passo 1: Fazer login e obter token**

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"
```

**Passo 2: Usar o token em uma requisição autenticada**

```bash
# Exemplo: Listar usuários (endpoint protegido)
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado esperado:**
- ✅ HTTP 200 OK
- ✅ Lista de usuários retornada

---

## 🔍 Verificações no Banco de Dados

### Ver todos os logs de login

```sql
SELECT
    id,
    email_attempted,
    status,
    failure_reason,
    ip_address,
    created_at
FROM pro_team_care_logs.[core].login_logs
ORDER BY created_at DESC;
```

### Ver tentativas falhadas

```sql
SELECT
    email_attempted,
    COUNT(*) as tentativas,
    MAX(created_at) as ultima_tentativa
FROM pro_team_care_logs.[core].login_logs
WHERE status = 'FAILED'
GROUP BY email_attempted
ORDER BY tentativas DESC;
```

### Ver logins por IP

```sql
SELECT
    ip_address,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as sucessos,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as falhas
FROM pro_team_care_logs.[core].login_logs
GROUP BY ip_address
ORDER BY total DESC;
```

### Verificar last_login_at do usuário

```sql
SELECT
    id,
    email_address,
    is_active,
    is_system_admin,
    last_login_at,
    created_at
FROM [core].[users]
WHERE email_address = 'admin@proteamcare.com.br';
```

---

## 🐛 Troubleshooting

### Erro: "Connection refused"

**Causa:** Backend não está rodando

**Solução:**
```bash
cd ~/Projetos/meu_projeto
./start.sh
```

---

### Erro: "Email ou senha inválidos" (mas estão corretos)

**Causa 1:** Stored procedure não foi criada

**Verificar:**
```sql
SELECT * FROM sys.procedures
WHERE name = 'sp_execute_login';
```

**Solução:** Execute o script de criação da SP

---

**Causa 2:** Banco de logs não existe

**Verificar:**
```sql
SELECT name FROM sys.databases
WHERE name = 'pro_team_care_logs';
```

**Solução:** Execute o script de criação do banco de logs

---

**Causa 3:** Hash de senha diferente

**Verificar:**
```sql
SELECT password FROM [core].[users]
WHERE email_address = 'admin@proteamcare.com.br';
```

**Solução:** Deve ser: `$2b$12$s.0a0SfkOP61AI.mYS4kMOgGm4V8/aF9eCAhwDfTjx6dn0fzvcrZ.`

---

### Erro: "500 Internal Server Error"

**Causa:** Erro na stored procedure ou conexão com banco

**Verificar logs:**
```bash
tail -f ~/Projetos/meu_projeto/logs/backend.log
```

**Soluções comuns:**
1. Verificar se ambos os bancos estão acessíveis
2. Verificar se a SP existe e está correta
3. Verificar se a tabela `login_logs` existe

---

## 📊 Métricas de Performance

### Tempo de resposta esperado

- **Login bem-sucedido:** < 200ms
- **Login falhado:** < 150ms

### Verificar performance

```bash
time curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }'
```

---

## 🔐 Segurança

### O que é registrado no log

**Sucesso:**
- ✅ Email usado
- ✅ IP de origem
- ✅ User-Agent
- ✅ Timestamp
- ✅ user_id e company_id

**Falha:**
- ✅ Email tentado
- ✅ IP de origem
- ✅ Motivo da falha
- ✅ Timestamp
- ❌ Senha NÃO é registrada

### Dados sensíveis

- **Senha:** Nunca trafega ou é armazenada em texto plano
- **Token JWT:** Expira em 30 minutos (configurável)
- **Logs:** Armazenados em banco separado

---

## 📚 Próximos Passos

Após validar o login:

1. ✅ Testar criação de companies
2. ✅ Testar criação de usuários de company
3. ✅ Testar endpoints protegidos com JWT
4. ✅ Implementar rate limiting
5. ✅ Implementar 2FA (futuro)
