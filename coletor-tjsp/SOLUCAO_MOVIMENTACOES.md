# ✅ SOLUÇÃO: Extração de TODAS as Movimentações

## 🎯 Problema Resolvido

### Antes:
```json
{
  "total_movimentacoes": 45,
  "movimentacoes": [ ... apenas 5 extraídas ... ]
}
```

### Depois (Esperado):
```json
{
  "total_movimentacoes": 45,
  "movimentacoes": [ ... 45 extraídas ... ]
}
```

---

## 🔧 Correção Implementada

### 1. **Novo Método: `_expandir_todas_movimentacoes()`**

**Localização:** `src/scraper.py` (linha ~550)

**Função:** Detecta e clica no botão "Ver todas as movimentações"

**Seletores testados:**
- `a:has-text("Ver todas")`
- `a:has-text("Exibir todas")`
- `a[onclick*="exibirTodasMovimentacoes"]`
- `#linkTodasMovimentacoes`
- E mais 10+ variações

### 2. **Método Modificado: `extract_movements()`**

**Mudanças:**
1. **Passo 1:** Tenta expandir todas as movimentações
2. **Passo 2:** Re-captura HTML após expansão
3. **Passo 3:** Prioriza tabela `tabelaTodasMovimentacoes` (completa)
4. **Passo 4:** Fallback para `tabelaUltimasMovimentacoes` (parcial)

---

## 🧪 Como Testar

### Teste Rápido:
```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp
source venv/bin/activate
python testar_movimentacoes_completas.py
```

### Teste com Processo Real:
```bash
# Criar CSV com processo que tem muitas movimentações
echo "processo_numero,etiqueta_opcional" > input/teste_completo.csv
echo "1024444-30.2025.8.26.0576,Teste Movimentações" >> input/teste_completo.csv

# Executar coleta
python run.py --input input/teste_completo.csv --output output/teste_completo --debug

# Verificar resultado
cat output/teste_completo/todas_movimentacoes_*.json | grep -A 2 "total_movimentacoes"
```

---

## 📊 Validação

### ✅ **Sucesso:**
```
✅ Tabela de movimentações encontrada: tbody {'id': 'tabelaTodasMovimentacoes'}
📋 Encontradas 45 linhas na tabela de movimentações
✅ Extraídas 45 movimentações
```

### ⚠️ **Parcial (Botão não encontrado):**
```
⚠️ Botão 'Ver todas' não encontrado - usando movimentações visíveis
✅ Tabela de movimentações encontrada: tbody {'id': 'tabelaUltimasMovimentacoes'}
📋 Encontradas 5 linhas na tabela de movimentações
```

### ❌ **Falha:**
```
❌ Nenhuma tabela de movimentações encontrada
```

---

## 🔍 Troubleshooting

### Problema: Ainda extrai apenas 5 movimentações

**Causa:** Botão "Ver todas" não está sendo encontrado

**Solução:**

1. **Executar em modo debug:**
```bash
python run.py --input input/teste.csv --output output/ --debug
```

2. **Verificar HTML salvo:**
```bash
# HTML é salvo em cache/ quando DEBUG_MODE=true
firefox cache/1024444-30.2025.8.26.0576.html
```

3. **Procurar botão manualmente:**
   - Abra o HTML no navegador
   - Inspecione elemento do botão "Ver todas"
   - Copie o seletor CSS correto
   - Adicione ao array `selectors` em `_expandir_todas_movimentacoes()`

### Problema: Erro ao clicar no botão

**Causa:** Botão está oculto ou desabilitado

**Solução:**

Adicione verificação de visibilidade:
```python
if element and await element.is_visible():
    await element.click()
```

### Problema: Tabela não carrega após clicar

**Causa:** JavaScript do site não executou

**Solução:**

Aumente timeout:
```python
await self.page.wait_for_selector(
    'tbody#tabelaTodasMovimentacoes',
    state='visible',
    timeout=15000  # Aumentar de 10s para 15s
)
```

---

## 📝 Checklist de Validação

Execute este checklist após a correção:

- [ ] Código modificado em `src/scraper.py`
- [ ] Método `_expandir_todas_movimentacoes()` adicionado
- [ ] Método `extract_movements()` modificado
- [ ] Teste `testar_movimentacoes_completas.py` criado
- [ ] Teste executado com sucesso
- [ ] JSON gerado tem `total_movimentacoes` == `len(movimentacoes)`
- [ ] Logs mostram "Tabela completa de movimentações carregada"

---

## 🎯 Resultado Esperado

### Logs de Sucesso:
```
Tentando expandir todas as movimentações...
✅ Botão 'Ver todas' encontrado: a:has-text("Ver todas")
✅ Tabela completa de movimentações carregada
✅ Todas as movimentações expandidas com sucesso
Re-capturando HTML após expansão...
✅ Tabela de movimentações encontrada: tbody {'id': 'tabelaTodasMovimentacoes'}
📋 Encontradas 45 linhas na tabela de movimentações
✅ Extraídas 45 movimentações
```

### JSON Gerado:
```json
{
  "processo": "1024444-30.2025.8.26.0576",
  "total_movimentacoes": 45,
  "movimentacoes": [
    {
      "mov_ordem": 1,
      "mov_data": "15/10/2025",
      "mov_descricao": "Distribuição - Processo distribuído por sorteio",
      ...
    },
    ...
    {
      "mov_ordem": 45,
      "mov_data": "30/10/2025",
      "mov_descricao": "Última movimentação",
      ...
    }
  ]
}
```

---

## 💡 Próximos Passos

1. **Executar teste:**
   ```bash
   python testar_movimentacoes_completas.py
   ```

2. **Se passar:** Sistema está funcionando!

3. **Se falhar:** 
   - Verificar logs de debug
   - Inspecionar HTML salvo
   - Ajustar seletores se necessário

---

## 📚 Arquivos Relacionados

- **Código:** `src/scraper.py` (linhas 550-630, 642-687)
- **Teste:** `testar_movimentacoes_completas.py`
- **Documentação:** `CORRECAO_MOVIMENTACOES_COMPLETAS.md`

---

**Status:** ✅ Correção implementada  
**Próximo passo:** Executar `python testar_movimentacoes_completas.py`  
**Data:** 30/10/2025
