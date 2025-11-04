# 🤖 OpenCode.ai Setup Guide

Guia para configurar o OpenCode.ai como dev full-stack do Pro Team Care.

---

## 📋 O que é OpenCode.ai?

OpenCode.ai é um **agente de IA para terminal** que atua como desenvolvedor full-stack.

**Diferença de outros:**
- Windsurf/Cursor → IDE com IA integrada
- OpenCode → CLI/Terminal com IA autônoma
- Claude Code → CLI da Anthropic

---

## 🚀 Instalação (se ainda não instalou)

```bash
# Via npm
npm install -g @opencode-ai/cli

# Ou via brew (macOS/Linux)
brew install opencode-ai/tap/opencode
```

**Verificar instalação:**
```bash
opencode --version
```

---

## ⚙️ Configuração do Projeto

### 1. **AGENTS.md já está pronto!**

O arquivo `/home/juliano/Projetos/meu_projeto/AGENTS.md` contém:

✅ Regras do projeto (Database First, Multi-tenant, etc)
✅ Padrões de código (Backend Python + Frontend React)
✅ Padrões visuais (Tailwind CSS design system)
✅ Nomenclatura e estrutura de arquivos
✅ Workflows para tarefas comuns
✅ O que NUNCA fazer

**OpenCode lerá este arquivo automaticamente quando rodar no projeto!**

---

### 2. **Rodar OpenCode Server (Recomendado)**

O projeto já tem scripts prontos para iniciar OpenCode em modo servidor:

```bash
# Navegar para o projeto
cd /home/juliano/Projetos/meu_projeto

# Iniciar servidor OpenCode.ai (carrega AGENTS.md automaticamente)
./start_opencode.sh

# Em outro terminal, conectar cliente
opencode

# Ou usar comando direto
opencode "criar endpoint GET /api/v1/products"

# Parar servidor quando terminar
./stop_opencode.sh

# Monitorar logs
tail -f logs/opencode.log
```

**Vantagens do modo servidor:**
- ✅ Carrega `AGENTS.md` automaticamente
- ✅ Múltiplos clientes podem se conectar
- ✅ Roda em background
- ✅ Logs separados em `logs/opencode.log`
- ✅ Controle via scripts (start/stop)

---

### 3. **Rodar OpenCode Direto (Alternativa)**

Se preferir não usar modo servidor:

```bash
# Navegar para o projeto
cd /home/juliano/Projetos/meu_projeto

# Iniciar OpenCode (lê AGENTS.md automaticamente)
opencode

# Ou usar comando direto
opencode "criar endpoint GET /api/v1/products"
```

---

### 4. **Comandos Úteis do OpenCode**

```bash
# Inicializar projeto (gera AGENTS.md se não existir)
opencode /init

# Modo chat interativo
opencode

# Executar tarefa direta
opencode "adicionar validação de CPF no UserSchema"

# Com arquivo específico
opencode "refatorar UserService.py"

# Modo review (não escreve código, apenas analisa)
opencode --mode review "analisar segurança do endpoint /auth/login"
```

---

## 🎯 Como Usar Efetivamente

### ✅ **Boas Práticas:**

#### 1. **Seja Específico e Direto**
```bash
# ❌ Vago
opencode "melhorar o código"

# ✅ Específico
opencode "criar endpoint GET /api/v1/users com paginação usando BaseRepository"
```

#### 2. **Peça Planos Antes de Executar**
```bash
opencode "planejar implementação de sistema de notificações push"
# Ele vai mostrar plano → você aprova → ele executa
```

#### 3. **Use para Tarefas Repetitivas**
```bash
opencode "criar CRUD completo para entidade Product (model, schema, endpoint, testes)"
```

#### 4. **Refatoração em Lote**
```bash
opencode "refatorar todos endpoints em api/v1/ para usar BaseRepository"
```

#### 5. **Análise de Código**
```bash
opencode --mode review "verificar se todos endpoints têm autenticação"
opencode --mode review "encontrar código duplicado no frontend"
```

---

## 📐 Padrões que OpenCode Seguirá

### Backend (Python/FastAPI)

**Ao criar endpoint:**
1. ✅ Usa BaseRepository para CRUD
2. ✅ Adiciona autenticação (get_current_active_user)
3. ✅ Paginação com skip/limit
4. ✅ Schemas Pydantic (Create, Update, Response)
5. ✅ Testes com pytest
6. ✅ Docstrings em inglês
7. ✅ Type hints obrigatórios

**Exemplo de prompt:**
```bash
opencode "criar endpoint POST /api/v1/companies para criar empresa"

# Ele vai:
# 1. Verificar se já existe similar
# 2. Criar CompanyCreate, CompanyUpdate, CompanyResponse schemas
# 3. Criar endpoint com BaseRepository
# 4. Adicionar auth + paginação
# 5. Criar testes
# 6. Registrar rota
```

---

### Frontend (React/TypeScript)

**Ao criar componente:**
1. ✅ Verifica se já existe similar (components/shared/)
2. ✅ TypeScript com interfaces (NUNCA any)
3. ✅ Tailwind CSS (NUNCA inline styles)
4. ✅ Componente < 200 linhas
5. ✅ Props className para customização
6. ✅ JSDoc com exemplo de uso

**Exemplo de prompt:**
```bash
opencode "criar componente ProductCard que mostra nome, preço e imagem"

# Ele vai:
# 1. Verificar se existe CardBase ou similar
# 2. Criar interface ProductCardProps
# 3. Usar Tailwind (bg-white shadow-md rounded-lg p-6)
# 4. Adicionar prop className
# 5. Criar exemplo de uso
```

---

## 🎨 Design System (Frontend)

**OpenCode seguirá automaticamente:**

```typescript
// Cores
Primary: blue-600, blue-700
Success: green-600
Error: red-600
Warning: yellow-600

// Botões
Primary: "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
Secondary: "bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg"

// Cards
Card: "bg-white shadow-md rounded-lg p-6"

// Forms
Input: "border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500"
```

**Exemplo:**
```bash
opencode "criar formulário de login com email e password"

# Resultado esperado:
# - Inputs com classes Tailwind corretas
# - Botão primary azul
# - Card branco com shadow
# - Validação com react-hook-form + zod
```

---

## 🔄 Workflows Automáticos

OpenCode está configurado para seguir workflows específicos:

### 1. **Criar Endpoint Completo**
```bash
opencode "criar CRUD completo para Products"
```
**Resultado:**
- ✅ Model mapeando tabela existente
- ✅ Schemas Pydantic (Create, Update, Response)
- ✅ 5 endpoints (GET list, GET id, POST, PUT, DELETE)
- ✅ BaseRepository usado
- ✅ Testes unitários
- ✅ Rota registrada

---

### 2. **Criar Página React Completa**
```bash
opencode "criar página de listagem de produtos com tabela e filtros"
```
**Resultado:**
- ✅ ProductsPage.tsx
- ✅ useProducts hook customizado
- ✅ productService com API calls
- ✅ Componentes reutilizáveis (DataTable)
- ✅ Tailwind CSS
- ✅ TypeScript tipado

---

### 3. **Refatorar Código Duplicado**
```bash
opencode "encontrar e refatorar código duplicado de formulário de endereço"
```
**Resultado:**
- ✅ Identifica 3 ocorrências
- ✅ Cria AddressForm.tsx reutilizável
- ✅ Substitui em todos lugares
- ✅ Remove código antigo
- ✅ Limpa imports não usados

---

### 4. **Corrigir Bugs**
```bash
opencode "corrigir erro 500 no endpoint /api/v1/users quando user_id não existe"
```
**Resultado:**
- ✅ Analisa código
- ✅ Identifica falta de validação
- ✅ Adiciona HTTPException 404
- ✅ Cria teste para caso de erro
- ✅ Valida que todos testes passam

---

## 🚨 Avisos Importantes

### ❌ **OpenCode NÃO pode:**
- Criar/alterar tabelas no SQL Server (Database First!)
- Fazer hard delete (sempre soft delete)
- Reiniciar servidor (hot reload está ativo!)
- Ignorar regras do AGENTS.md

### ✅ **OpenCode pode:**
- Criar/modificar código Python/TypeScript
- Criar/modificar testes
- Refatorar código existente
- Analisar segurança/performance
- Gerar documentação

---

## 🎓 Exemplos de Tarefas Comuns

### Backend

```bash
# Criar endpoint
opencode "criar endpoint GET /api/v1/establishments com filtro por company_id"

# Adicionar validação
opencode "adicionar validação de CPF no PfProfileCreate schema"

# Corrigir endpoint
opencode "corrigir endpoint POST /api/v1/users para validar email único"

# Criar testes
opencode "criar testes para todos endpoints de /api/v1/companies"

# Refatorar
opencode "refatorar UserService para usar BaseService"
```

### Frontend

```bash
# Criar componente
opencode "criar componente UserCard que mostra avatar, nome e email"

# Criar página
opencode "criar página de dashboard com cards de estatísticas"

# Adicionar funcionalidade
opencode "adicionar filtro de data na página de usuários"

# Corrigir bug
opencode "corrigir erro de tipo em UserForm quando email está vazio"

# Melhorar UI
opencode "melhorar responsividade da página de empresas para mobile"
```

### Full-Stack

```bash
# Feature completa
opencode "implementar sistema de notificações: backend endpoint + frontend toast"

# CRUD completo
opencode "criar CRUD completo para Contracts: backend + frontend + testes"

# Migração
opencode "migrar endpoint /users de queries diretas para BaseRepository"
```

---

## 📊 Monitorar Mudanças

OpenCode mostra:

```bash
📝 Arquivos modificados:
  M backend/app/api/v1/users.py
  M backend/app/schemas/user.py
  A backend/tests/test_users.py

📊 Estatísticas:
  Linhas adicionadas: +125
  Linhas removidas: -15
  Arquivos modificados: 3
  Testes criados: 8
```

---

## 🔍 Verificar Qualidade

```bash
# Após OpenCode fazer mudanças, rodar:

# Backend
cd backend && pytest -v
cd backend && black . && flake8 .

# Frontend
cd frontend && npm run lint
cd frontend && npm run test

# Verificar hot reload funcionando
# (não precisa reiniciar servidor!)
```

---

## 💡 Dicas Avançadas

### 1. **Modo Review (sem escrever código)**
```bash
opencode --mode review "analisar performance dos endpoints"
opencode --mode review "verificar segurança LGPD"
opencode --mode review "encontrar código duplicado"
```

### 2. **Trabalhar em Branch**
```bash
git checkout -b feature/products-crud
opencode "criar CRUD completo para Products"
git add .
git commit -m "feat: adiciona CRUD de produtos"
```

### 3. **Iterações**
```bash
# Primeira iteração
opencode "criar componente UserCard básico"

# Segunda iteração (refinar)
opencode "adicionar avatar e badge de status no UserCard"

# Terceira iteração (polish)
opencode "melhorar responsividade e adicionar skeleton loading no UserCard"
```

### 4. **Combinar com Windsurf**
```bash
# OpenCode para tarefas grandes/repetitivas
opencode "criar CRUD completo para 5 entidades"

# Windsurf para ajustes finos e review
# (usar IDE para revisar código gerado)
```

---

## 🆘 Troubleshooting

### Problema: OpenCode não está seguindo AGENTS.md

**Solução:**
```bash
# Verificar se está na raiz do projeto
pwd  # Deve ser /home/juliano/Projetos/meu_projeto

# Verificar se arquivo existe
ls -la AGENTS.md

# Re-inicializar
opencode /init
```

### Problema: OpenCode criou código com padrão errado

**Solução:**
```bash
# Pedir para corrigir seguindo AGENTS.md
opencode "refatorar último código criado seguindo padrões do AGENTS.md"
```

### Problema: OpenCode quer criar migration

**Solução:**
```bash
# Lembrar que é Database First
opencode "este projeto é Database First. Não use migrations. Apenas mapeie a tabela existente com SQLAlchemy."
```

---

## 📚 Recursos

- **AGENTS.md** - Instruções completas para OpenCode
- **CLAUDE.md** - Documentação do projeto
- **IDE_MEMORIES.md** - Contexto adicional
- **docs/HOT_RELOAD.md** - Hot reload guide

---

## ✅ Checklist de Setup

- [ ] OpenCode instalado (`opencode --version`)
- [ ] AGENTS.md na raiz do projeto
- [ ] Rodou `opencode /init` (se necessário)
- [ ] Testou comando simples: `opencode "listar arquivos do projeto"`
- [ ] Verificou que segue padrões: `opencode "criar endpoint de teste"`
- [ ] Backend e Frontend rodando (para testar mudanças)

---

**🚀 OpenCode configurado! Agora você tem um dev full-stack trabalhando para você 24/7!**

**Próximo passo:** Teste com `opencode "criar endpoint GET /api/v1/health-check simples"`
