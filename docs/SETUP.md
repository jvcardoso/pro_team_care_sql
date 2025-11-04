# Guia de Setup Completo

Instruções detalhadas para configuração do projeto em ambiente Windows.

---

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação do Ambiente](#instalação-do-ambiente)
3. [Configuração do SQL Server](#configuração-do-sql-server)
4. [Setup do Backend](#setup-do-backend)
5. [Setup do Frontend](#setup-do-frontend)
6. [Testes](#testes)
7. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### Software Necessário

| Software | Versão Mínima | Download |
|----------|---------------|----------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| SQL Server | 2019+ | Microsoft SQL Server |
| Git | 2.x | https://git-scm.com/ |
| VS Code | Latest | https://code.visualstudio.com/ |

### Verificar Instalações

```cmd
python --version
node --version
npm --version
git --version
```

---

## Instalação do Ambiente

### 1. Clonar Repositório

```cmd
git clone <url-do-repo>
cd meu_projeto
```

### 2. Executar Setup Automático

```cmd
scripts\setup_env.bat
```

Ou siga os passos manuais abaixo.

---

## Configuração do SQL Server

### 1. Criar Banco de Dados

Abra o SQL Server Management Studio (SSMS) e execute:

```sql
CREATE DATABASE meubanco;
GO
```

### 2. Criar Usuário (opcional)

```sql
USE meubanco;
GO

CREATE LOGIN app_user WITH PASSWORD = 'SenhaForte@123';
GO

CREATE USER app_user FOR LOGIN app_user;
GO

ALTER ROLE db_owner ADD MEMBER app_user;
GO
```

### 3. Habilitar TCP/IP

1. Abra **SQL Server Configuration Manager**
2. Vá em **SQL Server Network Configuration > Protocols**
3. Habilite **TCP/IP**
4. Reinicie o serviço SQL Server

### 4. Configurar Firewall

```cmd
netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433
```

### 5. Testar Conexão

```powershell
Test-NetConnection -ComputerName 192.168.11.84 -Port 1433
```

### 6. Executar Scripts SQL

No SSMS, execute em ordem:

1. `backend/sql_scripts/001_create_users.sql`
2. `backend/sql_scripts/002_create_companies.sql`
3. `backend/sql_scripts/003_create_initial_data.sql`

---

## Setup do Backend

### 1. Navegar para pasta

```cmd
cd backend
```

### 2. Criar Ambiente Virtual

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Atualizar pip

```cmd
python -m pip install --upgrade pip
```

### 4. Instalar Dependências

```cmd
pip install -r requirements.txt
```

### 5. Configurar .env

```cmd
copy .env.example .env
```

Edite `backend/.env`:

```env
APP_NAME=Meu Projeto
DEBUG=True
ENVIRONMENT=development

DB_SERVER=192.168.11.84
DB_PORT=1433
DB_NAME=meubanco
DB_USER=sa
DB_PASSWORD=SuaSenha

SECRET_KEY=gerar-chave-segura-aqui
```

**Gerar SECRET_KEY:**

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Testar Backend

```cmd
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

---

## Setup do Frontend

### 1. Navegar para pasta

```cmd
cd frontend
```

### 2. Instalar Dependências

```cmd
npm install
```

### 3. Configurar .env

```cmd
copy .env.example .env
```

Edite `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

### 4. Testar Frontend

```cmd
npm run dev
```

Acesse: http://localhost:3000

---

## Testes

### Backend

```cmd
cd backend
venv\Scripts\activate
pytest
```

### Frontend

```cmd
cd frontend
npm run lint
```

---

## Troubleshooting

### Erro: "pip não é reconhecido"

```cmd
python -m pip install --upgrade pip
```

### Erro: "uvicorn não encontrado"

```cmd
pip install uvicorn[standard]
```

### Erro: "Não foi possível conectar ao SQL Server"

1. Verifique se o serviço está rodando
2. Teste porta: `telnet 192.168.11.84 1433`
3. Verifique firewall
4. Confirme usuário/senha

### Erro: "ODBC Driver não encontrado"

Instale: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Frontend não conecta ao Backend

1. Verifique se backend está rodando em http://localhost:8000
2. Confirme `VITE_API_URL` no `.env` do frontend
3. Verifique CORS em `backend/app/core/config.py`

### Erro: "Tabela não existe"

Execute os scripts SQL em `backend/sql_scripts/` no SSMS.

---

## Próximos Passos

1. ✅ Criar tabelas no SQL Server
2. ✅ Configurar arquivos .env
3. ✅ Iniciar backend e frontend
4. ✅ Fazer login com credenciais padrão
5. 🔒 **IMPORTANTE:** Trocar senha do admin

---

## Comandos Rápidos

### Iniciar Tudo

```cmd
scripts\start_all.bat
```

### Apenas Backend

```cmd
scripts\start_backend.bat
```

### Apenas Frontend

```cmd
scripts\start_frontend.bat
```

---

## Suporte

Se precisar de ajuda, verifique:

1. Logs do backend no terminal
2. Console do navegador (F12)
3. Documentação da API: http://localhost:8000/docs
