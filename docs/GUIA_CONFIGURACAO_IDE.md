# 🚀 GUIA DE CONFIGURAÇÃO DA IDE

Guia prático para configurar sua IDE (Windsurf, Cursor, ou similar) com os arquivos de contexto do projeto.

---

## 📋 **O QUE VOCÊ TEM**

Seu projeto agora possui **4 arquivos de configuração**:

1. **CLAUDE.md** - Documentação principal para Claude Code
2. **IDE_RULES.md** - Regras de desenvolvimento e padrões
3. **IDE_WORKFLOWS.md** - Fluxos de trabalho automatizados
4. **IDE_MEMORIES.md** - Base de conhecimento do projeto

---

## 🎯 **COMO CONFIGURAR**

### Opção 1: Windsurf IDE (Cascade AI)

#### Passo 1: Abrir Configurações
1. Abra o Windsurf
2. Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)
3. Digite: "Cascade: Configure Rules"

#### Passo 2: Configurar Rules
1. Cole o conteúdo de `IDE_RULES.md`
2. Ou referencie o arquivo: `@IDE_RULES.md`

#### Passo 3: Configurar Workflows
1. Pressione `Ctrl+Shift+P`
2. Digite: "Cascade: Configure Workflows"
3. Cole o conteúdo de `IDE_WORKFLOWS.md`

#### Passo 4: Configurar Memories
1. Pressione `Ctrl+Shift+P`
2. Digite: "Cascade: Configure Memories"
3. Cole o conteúdo de `IDE_MEMORIES.md`

---

### Opção 2: Cursor IDE

#### Passo 1: Criar arquivo .cursorrules
```bash
# Na raiz do projeto
cp IDE_RULES.md .cursorrules
```

#### Passo 2: Configurar Composer
1. Abra o Cursor
2. Pressione `Ctrl+K` para abrir o Composer
3. Clique em "Settings" (⚙️)
4. Em "Context Files", adicione:
   - `IDE_WORKFLOWS.md`
   - `IDE_MEMORIES.md`
   - `CLAUDE.md`

---

### Opção 3: VS Code com Copilot

#### Criar arquivo de instruções
```bash
# Na raiz do projeto
mkdir -p .github
cat IDE_RULES.md IDE_WORKFLOWS.md IDE_MEMORIES.md > .github/copilot-instructions.md
```

Agora o GitHub Copilot lerá automaticamente essas instruções.

---

## ✅ **TESTAR SE FUNCIONOU**

### Teste 1: Criar Endpoint
Digite no chat da IA:
```
Criar endpoint GET /api/v1/products
```

**Resultado esperado:** A IA deve seguir o Workflow 1:
1. Criar schema em `backend/app/schemas/products.py`
2. Criar endpoint em `backend/app/api/v1/products.py`
3. Registrar rota
4. Criar testes
5. Executar testes

---

### Teste 2: Criar Componente React
Digite no chat da IA:
```
Criar componente ProductCard
```

**Resultado esperado:** A IA deve seguir o Workflow 2:
1. Criar types
2. Criar service
3. Criar hook
4. Criar componente
5. Criar página
6. Registrar rota

---

### Teste 3: Verificar Regras
Digite no chat da IA:
```
Devo usar migrations no backend?
```

**Resultado esperado:** A IA deve responder:
```
❌ NÃO! Este projeto usa Database First.
Tabelas devem ser criadas MANUALMENTE no SQL Server.
NUNCA use Alembic ou migrations.
```

---

## 🎨 **PERSONALIZAR AINDA MAIS**

### Adicionar suas próprias regras

Edite `IDE_RULES.md` e adicione:
```markdown
## Minhas Regras Customizadas

- Sempre usar logger ao invés de print()
- Commits em português
- Branches no formato: feature/[nome]
```

### Adicionar workflows específicos

Edite `IDE_WORKFLOWS.md` e adicione:
```markdown
## Workflow 6: Deploy em Produção

1. Rodar todos os testes
2. Build do frontend
3. Commitar mudanças
4. Push para main
5. Deploy via CI/CD
```

### Adicionar preferências pessoais

Edite `IDE_MEMORIES.md` e adicione:
```markdown
## Minhas Preferências

- Sempre usar aspas simples no Python
- Preferir list comprehension ao invés de loops
- Comentários em português
```

---

## 🔧 **COMANDOS ÚTEIS PARA A IA**

### Consultar Contexto
```
"Qual é a arquitetura do backend?"
"Como funciona o sistema multi-tenant?"
"Onde estão os modelos SQLAlchemy?"
```

### Criar Código
```
"Criar endpoint POST /api/v1/users"
"Criar componente UserCard"
"Adicionar validação de CPF no schema"
```

### Refatorar
```
"Refatorar UserService para usar BaseService"
"Melhorar performance do endpoint /users"
"Adicionar tratamento de erro em ProductCard"
```

### Depurar
```
"Por que o backend não está iniciando?"
"Erro CORS no frontend, como resolver?"
"Testes falhando, o que fazer?"
```

---

## 📊 **COMPARAÇÃO DE IDEs**

| Recurso | Windsurf (Cascade) | Cursor | VS Code + Copilot |
|---------|-------------------|--------|-------------------|
| **Rules** | ✅ Nativo | ✅ .cursorrules | ✅ copilot-instructions.md |
| **Workflows** | ✅ Nativo | ⚠️ Via Context | ⚠️ Via Context |
| **Memories** | ✅ Nativo | ⚠️ Via Context | ⚠️ Via Context |
| **Chat** | ✅ Cascade AI | ✅ Composer | ✅ Copilot Chat |
| **Edição** | ✅ Multi-arquivo | ✅ Multi-arquivo | ⚠️ Arquivo único |
| **Contexto** | ✅ Automático | ✅ Manual | ⚠️ Limitado |

**Recomendação:** Windsurf ou Cursor para melhor experiência.

---

## 💡 **DICAS PRO**

### 1. Sempre referencie os arquivos
```
"Seguindo IDE_WORKFLOWS.md, criar endpoint /products"
```

### 2. Use triggers dos workflows
```
"Adicionar tabela contracts"  ← Trigger do Workflow 4
```

### 3. Peça para IA explicar decisões
```
"Por que você usou BaseRepository aqui?"
```

### 4. Mantenha arquivos atualizados
Quando mudar algo importante no projeto:
```
"Atualizar IDE_MEMORIES.md com nova entidade Contract"
```

---

## 🚨 **PROBLEMAS COMUNS**

### IA não está seguindo as regras
**Solução:**
- Verifique se arquivos estão na raiz do projeto
- Reinicie a IDE
- Force o contexto: "Leia IDE_RULES.md e..."

### IA criou migrations (Database First)
**Solução:**
- Lembre a regra: "Este projeto é Database First!"
- Adicione em IDE_RULES.md em negrito

### IA não encontra arquivos de contexto
**Solução:**
- Use caminhos absolutos
- Adicione arquivos manualmente ao contexto
- Verifique permissões dos arquivos

---

## 📈 **MEDIR PRODUTIVIDADE**

### Antes da Configuração
- ⏱️ Criar endpoint: ~30 minutos
- ⏱️ Criar componente React: ~40 minutos
- ⏱️ Explicar arquitetura: ~20 minutos

### Depois da Configuração
- ⚡ Criar endpoint: ~5 minutos (6x mais rápido)
- ⚡ Criar componente React: ~7 minutos (5x mais rápido)
- ⚡ Explicar arquitetura: ~2 minutos (10x mais rápido)

---

## 🎓 **PRÓXIMOS PASSOS**

1. ✅ Configurar IDE com os 3 arquivos
2. ✅ Testar com criação de endpoint
3. ✅ Testar com criação de componente
4. ✅ Personalizar regras para seu estilo
5. ✅ Adicionar workflows específicos
6. ✅ Compartilhar com equipe

---

## 🤝 **COMPARTILHAR COM EQUIPE**

### Para novo desenvolvedor:
```bash
# 1. Clonar repositório
git clone [url]
cd meu_projeto

# 2. Ler documentação
cat CLAUDE.md

# 3. Configurar IDE
# Seguir este guia: GUIA_CONFIGURACAO_IDE.md

# 4. Testar
# Pedir IA para criar endpoint /test
```

---

## 📚 **RECURSOS ADICIONAIS**

- **CLAUDE.md** - Documentação completa do projeto
- **README.md** - Como rodar o projeto
- **docs/** - Documentação técnica detalhada

---

**✨ Configuração completa! Agora sua IDE entende 100% do projeto.**

**💬 Dúvidas? Pergunte à IA: "Como usar os arquivos de configuração da IDE?"**
