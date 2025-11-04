# Scripts SQL - Pro Team Care

Scripts SQL para setup inicial do banco de dados.

---

## ⚠️ IMPORTANTE

Este projeto usa **Database First**. As tabelas foram criadas manualmente no SQL Server.

Os scripts neste diretório são apenas para:
- Inserção de dados iniciais
- Criação de stored procedures
- Setup do banco de logs

**NUNCA execute scripts de criação de tabelas** - elas já existem no banco.

---

## 📜 Scripts Disponíveis

### `cleanup_failed_insert.sql`

**Propósito:** Limpar dados incompletos de tentativas anteriores que falharam

**Quando usar:** Se o `insert_admin_user.sql` falhou no meio e deixou dados incompletos

**Como executar:**

```sql
-- Execute ANTES de tentar novamente o insert_admin_user.sql
USE pro_team_care;

-- Execute o script
-- (Abra cleanup_failed_insert.sql e execute com F5)
```

---

### `insert_admin_user.sql`

**Propósito:** Criar Super Admin do sistema (acesso global)

**Execução:** Execute apenas **uma vez** após criar as tabelas

**O que faz:**
1. Cria o usuário Super Admin:
   - **Email:** `admin@proteamcare.com.br`
   - **Senha:** `admin123`
   - **company_id:** NULL (acesso a TODAS as companies)
   - **is_system_admin:** TRUE
2. Cria a role `super_admin` com `context_type = 'system'`
3. Atribui a role ao usuário com `context_id = 0`

**⚠️ Importante:**
- Super Admin NÃO está vinculado a nenhuma company específica
- Ele tem acesso a TODAS as companies do sistema
- Use APENAS para administração do sistema
- Crie usuários específicos para cada company

**Como executar:**

```sql
-- No SQL Server Management Studio (SSMS):

-- 1. Conecte-se ao servidor SQL Server
-- 2. Selecione o banco pro_team_care
USE pro_team_care;

-- 3. Abra o arquivo insert_admin_user.sql
-- 4. Execute (F5)
```

**Resultado esperado:**

```
Usuário Super Admin criado com ID: 1
IMPORTANTE: Super Admin tem acesso a TODAS as companies do sistema.
Role super_admin criada com ID: 1
Role atribuída ao usuário com sucesso!

================================================================
SUPER ADMIN CRIADO COM SUCESSO!
================================================================

CREDENCIAIS DE ACESSO:
  Email:         admin@proteamcare.com.br
  Senha:         admin123
  User ID:       1
  Role:          super_admin (ID: 1)

PERMISSÕES:
  - Acesso em nível de SISTEMA (context_type = system)
  - Acesso a TODAS as companies do sistema
  - Sem vinculo a company específica (company_id = NULL)

⚠️  IMPORTANTE:
  - Altere a senha após o primeiro login!
  - Use este usuário APENAS para administração do sistema
  - Crie usuários específicos para cada company
================================================================
```

---

## 🔐 Segurança

### Hash de Senha

O script usa o hash **bcrypt** da senha `admin123`:

```
$2b$12$s.0a0SfkOP61AI.mYS4kMOgGm4V8/aF9eCAhwDfTjx6dn0fzvcrZ.
```

**Como gerar novo hash:**

```bash
cd ~/Projetos/meu_projeto/backend
source venv/bin/activate
python generate_password_hash.py
```

### Alterar Senha Padrão

**SEMPRE** altere a senha padrão após o primeiro login:

```sql
-- Atualizar senha do admin (substitua NEW_HASH pelo hash gerado)
UPDATE [core].[users]
SET password = 'NEW_HASH',
    updated_at = GETDATE()
WHERE email_address = 'admin@proteamcare.com.br';
```

---

## 🧪 Testar Login

### Via curl

```bash
curl -X POST http://192.168.11.83:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "admin@proteamcare.com.br",
    "password": "admin123"
  }'
```

### Via Swagger UI

1. Acesse: http://192.168.11.83:8000/docs
2. Expanda `POST /api/v1/auth/login`
3. Click em "Try it out"
4. Insira as credenciais:
   ```json
   {
     "email_address": "admin@proteamcare.com.br",
     "password": "admin123"
   }
   ```
5. Click em "Execute"

**Resposta esperada:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## ❌ Troubleshooting

### Erro: "String or binary data would be truncated in table 'core.people', column 'tax_id'"

**Causa:** CNPJ com pontuação ultrapassa o tamanho do campo

**Solução:** O script foi corrigido para usar CNPJ sem pontuação (apenas 14 dígitos)

**Se o erro persistir:**
1. Execute `cleanup_failed_insert.sql` para limpar dados incompletos
2. Execute novamente `insert_admin_user.sql`

---

### Erro: "Violation of UNIQUE KEY constraint"

**Causa:** Usuário já existe

**Solução:** O script é idempotente. Se o usuário já existe, ele será ignorado.

---

### Erro: "Cannot insert the value NULL into column 'created_at'"

**Causa:** Tabela não tem valores padrão configurados

**Solução:** Verifique se as tabelas foram criadas com os scripts corretos

---

### Erro: "Invalid object name 'core.users'"

**Causa:** Schema `[core]` não existe ou você está no banco errado

**Solução:**
```sql
-- Verificar banco atual
SELECT DB_NAME();

-- Mudar para o banco correto
USE pro_team_care;
```

---

### Script falhou no meio - Como limpar?

**Solução:**

```sql
-- 1. Execute o script de limpeza
USE pro_team_care;
-- Abra e execute: cleanup_failed_insert.sql

-- 2. Tente novamente
-- Abra e execute: insert_admin_user.sql
```

---

## 📚 Referências

- [DATABASE_STRUCTURE.md](../docs/DATABASE_STRUCTURE.md) - Estrutura completa do banco
- [SECURITY_ARCHITECTURE.md](../docs/SECURITY_ARCHITECTURE.md) - Arquitetura de segurança
