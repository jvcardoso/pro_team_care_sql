# 🐛 Guia de Debug - Coletor TJSP

## Problema Identificado: Timeout ao Coletar Processos

### 🔍 Diagnóstico Passo a Passo

## 1️⃣ Teste de Conexão Básica (EXECUTAR PRIMEIRO)

```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp

# Ativar ambiente virtual
source venv/bin/activate

# Executar teste diagnóstico (abre browser visível)
python test_connection.py
```

### O que este teste faz:
- ✅ Abre browser em modo visual (você vê o que acontece)
- ✅ Acessa página de consulta do TJSP
- ✅ Verifica se há CAPTCHA
- ✅ Testa busca por "Rio Nieva"
- ✅ Salva HTML em `debug_resultado.html`
- ✅ Mostra processos encontrados

### Resultados Esperados:

#### ✅ **Sucesso**
```
✓ Página carregada com sucesso
✓ Sem CAPTCHA detectado
✓ Select de pesquisa encontrado
✓ Campo de consulta encontrado
✓ Botão de consultar encontrado
✓ 15 processos encontrados
```

#### ⚠️ **CAPTCHA Detectado**
```
⚠️ CAPTCHA DETECTADO - Site está protegido
→ Solução: Executar em horários de baixo tráfego (22h-6h)
```

#### ❌ **Elementos Não Encontrados**
```
✗ Select de pesquisa NÃO encontrado
→ Site mudou layout - precisa atualizar seletores
```

---

## 2️⃣ Se Teste de Conexão Funcionou

### Teste com 1 Processo Real

```bash
# Usar processo público real (substitua pelo número correto)
echo "processo_numero,etiqueta_opcional" > input/teste_real.csv
echo "1000032-02.2024.8.26.0100,Teste" >> input/teste_real.csv

# Executar coleta em modo debug
python run.py --input input/teste_real.csv --output output/debug --debug
```

---

## 3️⃣ Problemas Comuns e Soluções

### ❌ Problema: "Timeout após 60 segundos"

**Causas Possíveis:**
1. **CAPTCHA**: Site detectou automação
2. **Seletores errados**: Site mudou layout
3. **Processo inexistente**: Número inválido
4. **Rate limiting**: Muitas requisições

**Soluções:**

#### A) CAPTCHA Detectado
```bash
# Editar .env e aumentar delays
MIN_DELAY=10
MAX_DELAY=20

# Executar em horário de baixo tráfego
# Melhor horário: 22h-6h
```

#### B) Seletores Desatualizados
```bash
# 1. Executar teste de conexão
python test_connection.py

# 2. Abrir HTML salvo
firefox debug_resultado.html

# 3. Verificar estrutura da página
# Se elementos mudaram, precisa atualizar src/scraper.py
```

#### C) Processo Inexistente
```bash
# Usar processo que você SABE que existe
# Consulte manualmente no site primeiro:
# https://esaj.tjsp.jus.br/cpopg/open.do
```

---

## 4️⃣ Teste Alternativo: Busca Direta

Se coleta por número falhar, teste busca por nome:

```bash
# Busca por condomínio (mais confiável)
python run.py --search-party "Rio Nieva" --output output/busca_condominio --debug

# Busca por advogado
python run.py --search-lawyer "Adilson Lopes Teixeira" --output output/busca_advogado --debug
```

---

## 5️⃣ Análise de Logs

### Verificar logs detalhados:

```bash
# Ver último log
tail -f logs/coletor_*.log

# Buscar erros específicos
grep "ERROR" logs/coletor_*.log
grep "Timeout" logs/coletor_*.log
```

### Verificar HTML salvo (se DEBUG_MODE=true):

```bash
# Listar HTMLs salvos
ls -lh cache/*.html

# Abrir no navegador para análise
firefox cache/1000032-02.2024.8.26.0100.html
```

---

## 6️⃣ Correções Rápidas

### Se site mudou seletores CSS:

Edite `src/scraper.py` e atualize os seletores:

```python
# ANTES (linha ~150)
await page.select_option('select[name="cbPesquisa"]', 'NUMPROC')

# DEPOIS (se mudou)
await page.select_option('#cbPesquisa', 'NUMPROC')
# ou
await page.select_option('select.form-control[name="cbPesquisa"]', 'NUMPROC')
```

### Como descobrir seletores corretos:

1. Abra `debug_resultado.html` no navegador
2. Clique com botão direito no elemento → Inspecionar
3. Copie o seletor CSS correto
4. Atualize em `src/scraper.py`

---

## 7️⃣ Modo Seguro (Sem Risco de Ban)

```bash
# Configurar delays maiores no .env
MIN_DELAY=15
MAX_DELAY=30
MAX_REQUESTS_PER_MINUTE=3

# Executar em lotes pequenos
python run.py --input input/lote_5_processos.csv --output output/
```

---

## 8️⃣ Checklist de Troubleshooting

- [ ] Executei `test_connection.py` e vi o browser abrir?
- [ ] CAPTCHA apareceu na tela?
- [ ] Elementos foram encontrados no teste?
- [ ] HTML foi salvo em `debug_resultado.html`?
- [ ] Verifiquei se processo existe manualmente no site?
- [ ] Tentei em horário de baixo tráfego (22h-6h)?
- [ ] Aumentei delays no `.env`?
- [ ] Logs mostram erro específico?

---

## 9️⃣ Quando Pedir Ajuda

Se após todos os testes ainda não funcionar, envie:

1. **Saída do teste de conexão**:
   ```bash
   python test_connection.py > teste_saida.txt 2>&1
   ```

2. **HTML salvo**: `debug_resultado.html`

3. **Logs de erro**:
   ```bash
   tail -100 logs/coletor_*.log > logs_erro.txt
   ```

4. **Screenshot do erro** (se browser abrir)

---

## 🎯 Próximo Passo Recomendado

**EXECUTE AGORA:**

```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp
source venv/bin/activate
python test_connection.py
```

Isso vai mostrar exatamente onde está o problema! 🔍
