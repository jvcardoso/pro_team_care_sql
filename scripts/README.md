# Scripts de Gerenciamento

Scripts para gerenciar o projeto no Linux/Mac.

---

## Scripts Disponíveis

### 🚀 `start.sh` - Iniciar Projeto

Inicia backend e frontend automaticamente.

**Uso:**
```bash
./start.sh                # Início normal (limpa cache)
./start.sh --skip-cache   # Início rápido (sem limpar cache)
./start.sh -s             # Atalho para --skip-cache
```

**O que faz:**
- ✅ Verifica sistema (Python, Node.js, portas)
- ✅ Limpa cache (Python e Node.js)
- ✅ Para processos existentes nas portas 8000 e 3000
- ✅ Verifica/cria arquivos .env
- ✅ Instala dependências se necessário
- ✅ Inicia backend (FastAPI)
- ✅ Inicia frontend (React + Vite)
- ✅ Testa conectividade
- ✅ Mantém processos rodando (Ctrl+C para parar)

---

### 🛑 `stop.sh` - Parar Projeto

Para todos os serviços rodando.

**Uso:**
```bash
./stop.sh
```

**O que faz:**
- 🔴 Para backend (porta 8000)
- 🔴 Para frontend (porta 3000)
- 🔴 Limpa processos nas portas
- 🔴 Remove arquivos PID

---

### 🧹 `clean_cache.sh` - Limpar Cache

Limpa todo o cache do projeto.

**Uso:**
```bash
./clean_cache.sh
```

**O que faz:**
- 🧹 Limpa cache Python (`__pycache__`, `.pyc`)
- 🧹 Limpa cache Node.js (`.vite`, `dist`, `node_modules/.cache`)
- 🧹 Limpa npm cache
- 🧹 Limpa logs antigos

---

## Scripts Windows (.bat)

Os scripts Windows estão em `scripts/`:

```cmd
scripts\setup_env.bat      # Setup inicial
scripts\start_backend.bat  # Apenas backend
scripts\start_frontend.bat # Apenas frontend
scripts\start_all.bat      # Backend + Frontend
```

---

## Primeira Vez

### Linux/Mac

1. **Setup inicial:**
   ```bash
   # Dar permissão de execução
   chmod +x start.sh stop.sh clean_cache.sh

   # Configurar backend
   cd backend
   cp .env.example .env
   # Editar .env com dados do SQL Server

   # Voltar para raiz
   cd ..
   ```

2. **Criar tabelas no SQL Server:**
   Execute os scripts em `backend/sql_scripts/` no SSMS:
   - 001_create_users.sql
   - 002_create_companies.sql
   - 003_create_initial_data.sql

3. **Iniciar projeto:**
   ```bash
   ./start.sh
   ```

### Windows

1. **Setup inicial:**
   ```cmd
   scripts\setup_env.bat
   ```

2. **Editar configuração:**
   - Edite `backend\.env` com dados do SQL Server

3. **Criar tabelas no SQL Server:**
   Execute os scripts em `backend\sql_scripts\` no SSMS

4. **Iniciar projeto:**
   ```cmd
   scripts\start_all.bat
   ```

---

## Troubleshooting

### Erro: "Porta já em uso"

```bash
# Parar tudo
./stop.sh

# Ou matar processos manualmente
lsof -ti :8000 | xargs kill -9
lsof -ti :3000 | xargs kill -9
```

### Erro: "Comando não encontrado"

```bash
# Linux/Ubuntu
sudo apt install python3 python3-venv nodejs npm net-tools

# Mac
brew install python node
```

### Erro: "Backend não inicia"

```bash
# Ver logs
tail -f logs/backend.log

# Verificar dependências
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Frontend não inicia"

```bash
# Ver logs
tail -f logs/frontend.log

# Reinstalar dependências
cd frontend
rm -rf node_modules
npm install
```

### Erro: "Não conecta ao banco"

1. Verifique `backend/.env`
2. Teste conexão:
   ```bash
   telnet SEU_IP 1433
   ```
3. Verifique firewall do SQL Server
4. Confirme que as tabelas foram criadas

---

## Logs

Os logs ficam em `logs/`:

```bash
# Ver logs em tempo real
tail -f logs/backend.log   # Backend
tail -f logs/frontend.log  # Frontend

# Ver logs completos
cat logs/backend.log
cat logs/frontend.log
```

---

## URLs de Acesso

Após iniciar:

- **Backend API:** http://localhost:8000
- **Documentação:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Frontend:** http://localhost:3000

**Credenciais padrão:**
- Email: `admin@example.com`
- Senha: `admin123`

---

## Comandos Úteis

```bash
# Verificar se está rodando
ps aux | grep uvicorn    # Backend
ps aux | grep vite       # Frontend

# Verificar portas
lsof -i :8000            # Backend
lsof -i :3000            # Frontend

# Limpar tudo e reiniciar
./stop.sh
./clean_cache.sh
./start.sh

# Início rápido (sem limpar cache)
./start.sh --skip-cache
```

---

## Automatizar Início

### Linux/Mac (systemd)

Crie um serviço systemd para iniciar automaticamente.

### PM2 (Recomendado)

```bash
# Instalar PM2
npm install -g pm2

# Iniciar com PM2
pm2 start start.sh --name meu-projeto

# Ver status
pm2 status

# Parar
pm2 stop meu-projeto

# Logs
pm2 logs meu-projeto
```

---

## Desenvolvimento

### Backend

```bash
cd backend
source venv/bin/activate

# Rodar manualmente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testes
pytest

# Formatar código
black .
```

### Frontend

```bash
cd frontend

# Rodar manualmente
npm run dev

# Build
npm run build

# Preview build
npm run preview
```
