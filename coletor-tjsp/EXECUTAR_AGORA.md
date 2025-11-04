# 🚀 EXECUTAR AGORA - Guia Passo a Passo

## ⚠️ IMPORTANTE: Siga esta ordem exata!

---

## 📋 Passo 1: Setup Inicial (OBRIGATÓRIO)

```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp
./setup.sh
```

**O que este comando faz:**
- ✅ Cria ambiente virtual Python
- ✅ Instala todas as dependências
- ✅ Instala browser Chromium
- ✅ Cria arquivo .env
- ✅ Cria diretórios necessários

**Tempo estimado:** 2-3 minutos

**Resultado esperado:**
```
✅ SETUP CONCLUÍDO COM SUCESSO!
```

---

## 📋 Passo 2: Ativar Ambiente

```bash
source venv/bin/activate
```

**Você verá:** `(venv)` no início da linha do terminal

---

## 📋 Passo 3: Teste Básico (Validação)

```bash
python test_basico.py
```

**O que este teste faz:**
- ✅ Verifica conectividade com TJSP
- ✅ Valida seletores CSS
- ✅ Detecta CAPTCHA
- ✅ Salva HTML para análise

**Tempo estimado:** 10-20 segundos

### Resultados Possíveis:

#### ✅ **Sucesso Total**
```
✅ SUCESSO TOTAL!
   Todos os elementos encontrados
   Sistema pronto para uso
```
**→ Vá para o Passo 4**

#### ⚠️ **Sucesso Parcial**
```
⚠️ SUCESSO PARCIAL
   2/3 elementos encontrados
   Sistema pode funcionar com limitações
```
**→ Tente Passo 4, mas pode ter problemas**

#### ❌ **Falha**
```
❌ FALHA
   Poucos elementos encontrados
   Site pode ter mudado ou CAPTCHA está bloqueando
```
**→ Leia seção "Troubleshooting" abaixo**

---

## 📋 Passo 4: Teste com Dados Reais

### Opção A: Buscar por Condomínio

```bash
python run.py --search-party "Rio Nieva" --output output/teste_condominio --debug --max-mov 20
```

### Opção B: Buscar por Advogado

```bash
python run.py --search-lawyer "Adilson Lopes Teixeira" --output output/teste_advogado --debug --max-mov 20
```

### Opção C: Buscar por Número de Processo

```bash
# Primeiro, crie arquivo com processo real
echo "processo_numero,etiqueta_opcional" > input/teste_real.csv
echo "1000032-02.2024.8.26.0100,Teste" >> input/teste_real.csv

# Depois execute
python run.py --input input/teste_real.csv --output output/teste_numero --debug
```

**Tempo estimado:** 30-60 segundos por processo

### Resultados Esperados:

#### ✅ **Sucesso**
```
✓ 15 processos encontrados
✓ Processos exportados para: output/teste_condominio/processos_*.csv
✓ Dashboard HTML gerado: output/teste_condominio/dashboard_*.html
```

**Arquivos gerados:**
- `processos_[timestamp].csv` - Metadados
- `movimentacoes_[timestamp].csv` - Movimentações
- `dashboard_[timestamp].html` - Dashboard visual
- `analise_[timestamp].json` - Análise estratégica

#### ⚠️ **Nenhum Resultado**
```
⚠️ Nenhum processo encontrado
```
**Possíveis causas:**
- Nome não tem processos públicos
- Processos em segredo de justiça
- CAPTCHA bloqueou

#### ❌ **Timeout**
```
❌ Timeout ao buscar
```
**→ Veja seção "Troubleshooting" abaixo**

---

## 🐛 Troubleshooting

### Problema 1: "ModuleNotFoundError: No module named 'playwright'"

**Solução:**
```bash
./setup.sh
source venv/bin/activate
```

### Problema 2: "Timeout após 30 segundos"

**Causas:**
- CAPTCHA ativo
- Rate limiting
- Horário de pico

**Soluções:**

#### A) Aumentar Delays
Edite `.env`:
```bash
MIN_DELAY=15
MAX_DELAY=30
```

#### B) Executar em Horário Noturno
- Melhor horário: **22h - 6h**
- Menor tráfego = menos CAPTCHA

#### C) Testar Manualmente
1. Abra: https://esaj.tjsp.jus.br/cpopg/open.do
2. Tente buscar "Rio Nieva"
3. Se aparecer CAPTCHA → Site está protegido no momento

### Problema 3: "Elementos não encontrados"

**Solução:**
```bash
# Executar teste de seletores
python test_selectors.py

# Abrir HTML salvo para análise
firefox debug_teste_basico.html
```

### Problema 4: "Browser não abre"

**Solução:**
```bash
# Reinstalar browser
playwright install chromium

# Ou usar modo headless
# Edite .env:
HEADLESS=true
```

---

## 📊 Verificar Resultados

### Ver Dashboard HTML
```bash
# Abrir no navegador
firefox output/teste_condominio/dashboard_*.html

# Ou
xdg-open output/teste_condominio/dashboard_*.html
```

### Ver CSVs
```bash
# Listar arquivos gerados
ls -lh output/teste_condominio/

# Ver primeiras linhas
head output/teste_condominio/processos_*.csv
head output/teste_condominio/movimentacoes_*.csv
```

### Ver Logs
```bash
# Logs em tempo real
tail -f logs/coletor_*.log

# Buscar erros
grep "ERROR" logs/coletor_*.log
```

---

## 🎯 Coleta em Produção

Após validação bem-sucedida:

### 1. Coletar Todos os Processos do Condomínio
```bash
python run.py --search-party "Rio Nieva" --output output/condominio_completo
```

### 2. Coletar Todos os Processos do Advogado
```bash
python run.py --search-lawyer "Adilson Lopes Teixeira" --output output/advogado_completo
```

### 3. Coletar Lista Específica
```bash
# Criar CSV com processos desejados
nano input/meus_processos.csv

# Executar coleta
python run.py --input input/meus_processos.csv --output output/meus_processos
```

---

## ⚙️ Configurações Recomendadas

### Para Evitar Bloqueios

Edite `.env`:
```bash
# Delays maiores
MIN_DELAY=10
MAX_DELAY=20

# Timeout maior
PAGE_TIMEOUT=60

# Modo headless (mais discreto)
HEADLESS=true

# Limite de movimentações
MAX_MOVIMENTACOES=50
```

### Para Debug

Edite `.env`:
```bash
# Salvar HTML bruto
DEBUG_MODE=true

# Salvar screenshots
SAVE_SCREENSHOTS=true

# Logs detalhados
LOG_LEVEL=DEBUG
```

---

## 📞 Quando Pedir Ajuda

Se após todos os passos ainda não funcionar, envie:

1. **Saída do teste básico:**
   ```bash
   python test_basico.py > teste_saida.txt 2>&1
   ```

2. **HTML salvo:**
   - `debug_teste_basico.html`

3. **Logs de erro:**
   ```bash
   tail -100 logs/coletor_*.log > logs_erro.txt
   ```

4. **Informações do sistema:**
   ```bash
   python --version
   pip list | grep playwright
   ```

---

## ✅ Checklist Completo

- [ ] Executei `./setup.sh` com sucesso
- [ ] Ativei ambiente: `source venv/bin/activate`
- [ ] Teste básico passou: `python test_basico.py`
- [ ] Teste com dados reais funcionou
- [ ] Dashboard HTML foi gerado
- [ ] CSVs contêm dados válidos
- [ ] Sistema validado e pronto para produção

---

## 🎉 Próximo Passo

**EXECUTE AGORA:**

```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp
./setup.sh
```

Depois de concluído:

```bash
source venv/bin/activate
python test_basico.py
```

**Boa sorte! 🚀**
