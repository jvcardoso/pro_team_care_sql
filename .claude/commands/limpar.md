---
description: Limpar código removendo imports não usados, código comentado e aplicando formatação
---

# Limpar Código

Limpar código removendo imports não usados, código comentado e aplicando formatação.

## Comandos Disponíveis
**Uso:** `/limpar [arquivo|diretório]`
**Exemplo:** `/limpar backend/app/api/`

## Workflow

### 1. Análise do Código
Verificar:
- [ ] Imports não utilizados
- [ ] Variáveis não usadas
- [ ] Funções não usadas
- [ ] Código comentado
- [ ] TODOs sem contexto
- [ ] Formatação inconsistente

### 2. Apresentar Diagnóstico
```
🧹 Análise de Limpeza:

Encontrado em [arquivo]:
- Imports não usados: [N]
- Variáveis não usadas: [N]
- Código comentado: [X] linhas
- TODOs: [N]
- Formatação: [issues]

Posso limpar?
```

Aguardar confirmação.

### 3. Remover Imports Não Usados

#### Backend (Python):
```bash
cd backend
autoflake --remove-all-unused-imports --in-place app/**/*.py
```

#### Frontend (TypeScript):
```bash
cd frontend
# Remover manualmente ou usar ESLint fix
npm run lint -- --fix
```

### 4. Remover Código Comentado
REGRA: **Código comentado deve ser removido**
- Use git history, não comentários
- Único motivo para manter: documentar decisão técnica importante

Exemplo VÁLIDO de comentário:
```python
# PERFORMANCE: Stored procedure 10x mais rápido que ORM aqui
result = await db.execute(text("EXEC sp_authenticate_user"))
```

### 5. Limpar TODOs
- Remover TODOs sem contexto ou datados
- Converter TODOs relevantes em issues
- Manter apenas TODOs com deadline ou responsável

### 6. Aplicar Formatação

#### Backend (Python):
```bash
cd backend
black .
flake8 .
```

#### Frontend (TypeScript):
```bash
cd frontend
npm run format
npm run lint -- --fix
```

### 7. Validar que Nada Quebrou

#### Backend:
```bash
cd backend
pytest
```

#### Frontend:
```bash
cd frontend
npm test
npm run build
```

### 8. Apresentar Resumo
```
✅ Limpeza concluída!

📊 Removido:
- Imports não usados: [N]
- Variáveis não usadas: [N]
- Código comentado: [X] linhas
- TODOs obsoletos: [N]

🎨 Formatação:
- Arquivos formatados: [N]
- Linter: ✅ Sem warnings

✅ Validação:
- Testes: ✅ Todos passaram
- Build: ✅ Sucesso
- Código funciona: ✅
```

## Checklist
- [ ] Imports não usados removidos
- [ ] Variáveis não usadas removidas
- [ ] Código comentado removido (exceto docs importantes)
- [ ] TODOs limpos ou convertidos em issues
- [ ] Formatação aplicada (Black/Prettier)
- [ ] Linter passou sem warnings
- [ ] Testes continuam passando
- [ ] Build funciona

## Padrões Obrigatórios
- ✅ Remover código comentado (usar git)
- ✅ Limpar imports automaticamente
- ✅ Aplicar formatação (Black/Prettier)
- ✅ Validar com testes
- ❌ NUNCA deletar código em uso
- ❌ NUNCA ignorar warnings do linter

## Único Motivo para Manter Comentário
- ✅ Documenta decisão técnica importante
- ✅ Explica lógica não óbvia ou complexa
- ✅ Aviso sobre comportamento crítico/performance
