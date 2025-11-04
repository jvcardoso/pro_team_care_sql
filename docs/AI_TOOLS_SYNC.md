# Guia de Sincronização: Ferramentas de IA

Este documento explica como todas as ferramentas de IA do projeto estão sincronizadas e como utilizá-las de forma consistente.

## 🎯 Objetivo

Manter **Windsurf IDE**, **OpenCode.ai** e **Claude Code** com o mesmo contexto, regras e workflows para garantir consistência no desenvolvimento.

---

## 📁 Estrutura de Configuração

### Visão Geral

```
meu_projeto/
├── CLAUDE.md                        # Contexto principal (todas ferramentas)
├── AGENTS.md                        # Rules específicas OpenCode
├── GEMINI.md                        # Configuração para Gemini
├── .claude/                         # Claude Code específico
│   ├── settings.json               # Permissões e ambiente
│   └── commands/                   # Slash commands customizados
│       ├── endpoint.md             # /endpoint - Criar API endpoint
│       ├── bug-fix.md              # /bug-fix - Corrigir bugs
│       ├── teste.md                # /teste - Criar testes
│       ├── componente.md           # /componente - Criar componente React
│       ├── refatorar.md            # /refatorar - Refatorar código
│       └── limpar.md               # /limpar - Limpar código
└── ~/.codeium/windsurf/            # Windsurf IDE configuração
    ├── memories/
    │   └── global_rules.md         # Regras globais Windsurf
    └── global_workflows/           # Workflows Windsurf
        ├── endpoint.md
        ├── bug-fix.md
        ├── teste.md
        ├── componente.md
        ├── refatorar.md
        └── limpar.md
```

---

## 🛠️ Ferramentas e Seus Arquivos

### 1. **Windsurf IDE** (IDE Principal)

**Arquivos:**
- `~/.codeium/windsurf/memories/global_rules.md` - Regras globais
- `~/.codeium/windsurf/global_workflows/*.md` - Workflows reutilizáveis
- `CLAUDE.md` - Contexto do projeto (lê automaticamente)

**Como usar:**
- IDE já carrega regras automaticamente
- Use Cascade (Ctrl+L) para invocar IA
- Workflows disponíveis no menu de contexto

**Características:**
- ✅ Hot reload automático
- ✅ Memória persistente entre sessões
- ✅ Contexto do projeto sempre ativo

---

### 2. **OpenCode.ai** (Terminal Agent)

**Arquivos:**
- `AGENTS.md` - Rules principais (carregado automaticamente)
- `CLAUDE.md` - Contexto de fallback

**Como usar:**
```bash
# Iniciar servidor (recomendado)
./start_opencode.sh
opencode

# Ou direto
opencode "criar endpoint para users"

# Review mode (não escreve código)
opencode --mode review "analisar segurança do /auth/login"

# Parar servidor
./stop_opencode.sh
```

**Características:**
- ✅ Executa comandos bash automaticamente
- ✅ Pode modificar múltiplos arquivos
- ✅ Ideal para tarefas complexas multi-arquivo

---

### 3. **Claude Code** (CLI oficial Anthropic)

**Arquivos:**
- `CLAUDE.md` - Contexto principal (lê automaticamente)
- `.claude/settings.json` - Permissões e configurações
- `.claude/commands/*.md` - Slash commands customizados

**Como usar:**
```bash
# Iniciar sessão interativa
claude

# Usar slash commands
/endpoint companies GET,POST,PUT
/bug-fix Erro ao salvar endereço
/teste endpoint backend/app/api/v1/companies.py
/componente DataTable common
/refatorar src/components/forms/
/limpar backend/app/api/

# Limpar contexto
/clear

# Configurar
/config
```

**Características:**
- ✅ Slash commands customizados
- ✅ Permissões granulares (allow/deny/ask)
- ✅ Integração oficial Anthropic

---

### 4. **Gemini Code Assist** (VS Code Extension)

**Arquivos:**
- `GEMINI.md` - Configuração específica
- `CLAUDE.md` - Contexto de fallback

**Como usar:**
- Instalar extensão no VS Code
- Configurar `GEMINI.md` no workspace
- Usar atalhos da extensão

**Características:**
- ✅ Integração VS Code nativa
- ✅ Suporte a GEMINI.md files
- ✅ Context window grande (1M tokens)

---

## 🔄 Sincronização entre Ferramentas

### Arquivos Compartilhados

| Arquivo | Windsurf | OpenCode | Claude Code | Gemini |
|---------|----------|----------|-------------|--------|
| `CLAUDE.md` | ✅ | ✅ | ✅ | ✅ |
| `AGENTS.md` | ✅ | ✅ | ⚠️ | ⚠️ |
| `GEMINI.md` | ⚠️ | ⚠️ | ⚠️ | ✅ |
| `.claude/*` | ❌ | ❌ | ✅ | ❌ |

✅ Lê automaticamente
⚠️ Pode ler se especificado
❌ Não usa

### Hierarquia de Configuração

1. **Global** (mais geral)
   - `~/.codeium/windsurf/memories/global_rules.md`
   - `~/.claude/CLAUDE.md` (user-level)

2. **Project** (específico do projeto)
   - `CLAUDE.md` (todas ferramentas)
   - `AGENTS.md` (OpenCode)
   - `GEMINI.md` (Gemini)

3. **Local** (mais específico, não versionado)
   - `.claude/settings.local.json`
   - Subdiretórios com `CLAUDE.md` próprio

**Regra:** Mais específico sobrescreve mais geral

---

## 📋 Workflows Padronizados

Todos os workflows abaixo estão sincronizados entre as ferramentas:

### 1. **Criar Endpoint API**

**Windsurf:** Menu contexto → "Workflow: Criar Endpoint"
**OpenCode:** `opencode "criar endpoint companies com CRUD completo"`
**Claude Code:** `/endpoint companies GET,POST,PUT,DELETE`

**Passos:**
1. Verificar se endpoint similar existe
2. Criar schemas Pydantic
3. Criar endpoint com BaseRepository
4. Registrar rota
5. Criar testes
6. Validar

---

### 2. **Corrigir Bug**

**Windsurf:** Menu contexto → "Workflow: Corrigir Bug"
**OpenCode:** `opencode "corrigir bug ao salvar endereço vazio"`
**Claude Code:** `/bug-fix Erro ao salvar endereço com CEP vazio`

**Passos:**
1. Reproduzir bug
2. Localizar código
3. Identificar causa raiz
4. Criar teste que falha (TDD)
5. Implementar correção
6. Validar testes

---

### 3. **Criar Testes**

**Windsurf:** Menu contexto → "Workflow: Criar Testes"
**OpenCode:** `opencode "criar testes para endpoint companies"`
**Claude Code:** `/teste endpoint backend/app/api/v1/companies.py`

**Passos:**
1. Identificar o que testar
2. Criar casos de sucesso
3. Criar casos de erro
4. Criar edge cases
5. Validar cobertura (>80%)

---

### 4. **Criar Componente React**

**Windsurf:** Menu contexto → "Workflow: Criar Componente"
**OpenCode:** `opencode "criar componente DataTable reutilizável"`
**Claude Code:** `/componente DataTable common`

**Passos:**
1. Verificar se similar existe
2. Planejar estrutura
3. Criar componente TypeScript
4. Criar types se necessário
5. Oferecer criar testes

---

### 5. **Refatorar Código**

**Windsurf:** Menu contexto → "Workflow: Refatorar"
**OpenCode:** `opencode "refatorar src/components/forms/"`
**Claude Code:** `/refatorar src/components/forms/`

**Passos:**
1. Identificar duplicação
2. Criar componente/função reutilizável
3. Substituir ocorrências
4. Limpar código
5. Rodar testes

---

### 6. **Limpar Código**

**Windsurf:** Menu contexto → "Workflow: Limpar"
**OpenCode:** `opencode "limpar backend/app/api/"`
**Claude Code:** `/limpar backend/app/api/`

**Passos:**
1. Remover imports não usados
2. Remover código comentado
3. Aplicar formatação (Black/Prettier)
4. Validar testes

---

## 🎯 Quando Usar Cada Ferramenta

### Use **Windsurf IDE** para:
- ✅ Desenvolvimento diário
- ✅ Edições rápidas e pequenas
- ✅ Navegação e exploração de código
- ✅ Debugging visual
- ✅ Git operations com UI

### Use **OpenCode.ai** para:
- ✅ Tarefas complexas multi-arquivo
- ✅ Refatorações grandes
- ✅ Geração de código em lote
- ✅ Análise profunda de codebase
- ✅ Automações bash

### Use **Claude Code** para:
- ✅ Workflows estruturados (slash commands)
- ✅ Revisão de código
- ✅ Análise de segurança
- ✅ Documentação
- ✅ Quando precisa de controle granular

### Use **Gemini** para:
- ✅ Context windows muito grandes
- ✅ Integração VS Code nativa
- ✅ Quando Windsurf não disponível
- ✅ Features específicas do Gemini

---

## 🔧 Manutenção

### Atualizar Regras

Quando atualizar regras, sincronize nos arquivos:

1. **Regras Globais:**
   - `CLAUDE.md` (principal)
   - `AGENTS.md` (OpenCode)
   - `GEMINI.md` (Gemini)
   - `~/.codeium/windsurf/memories/global_rules.md`

2. **Workflows:**
   - `.claude/commands/*.md`
   - `~/.codeium/windsurf/global_workflows/*.md`

### Testar Sincronização

```bash
# Testar OpenCode
opencode "criar endpoint test com GET"

# Testar Claude Code
claude
/endpoint test GET

# Verificar se ambos seguem mesmos padrões
```

---

## 📚 Referências

- **CLAUDE.md** - Documentação principal do projeto
- **AGENTS.md** - Rules específicas do OpenCode
- **GEMINI.md** - Configuração do Gemini
- **docs/OPENCODE_SETUP.md** - Setup detalhado do OpenCode

---

## ✅ Checklist de Sincronização

- [ ] `CLAUDE.md` atualizado
- [ ] `AGENTS.md` sincronizado com CLAUDE.md
- [ ] `GEMINI.md` sincronizado
- [ ] `.claude/commands/` criados
- [ ] Windsurf workflows atualizados
- [ ] Testado em pelo menos 2 ferramentas
- [ ] Documentação atualizada

---

**Última atualização:** Janeiro 2025
**Versão:** 1.0
**Mantido por:** Juliano
