# Coletor de Processos TJSP - 1º Grau

## 📋 Descrição
Sistema automatizado para coleta de dados públicos de processos judiciais do TJSP (1º Grau), focado em análise estratégica de processos condominiais.

## 🎯 Objetivos
- Extrair metadados e movimentações de processos públicos
- Classificar automaticamente decisões e medidas constritivas
- Identificar padrões de cobrança (SISBAJUD → RENAJUD → INFOJUD)
- Analisar atuação de advogados e resultados obtidos

## ⚡ Início Rápido

### Setup Automático (Recomendado)
```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp
./setup.sh
```

Este comando faz tudo automaticamente:
- ✅ Cria ambiente virtual
- ✅ Instala dependências
- ✅ Instala browser Chromium
- ✅ Configura .env
- ✅ Cria diretórios

### Validação
```bash
source venv/bin/activate
python test_basico.py
```

**Leia:** `EXECUTAR_AGORA.md` para guia passo a passo completo.

## ⚙️ Instalação Manual

### Pré-requisitos
- Python 3.11+
- Chrome/Chromium instalado

### Setup Manual
```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar browser
playwright install chromium

# 4. Configurar
cp .env.example .env
```

## 🚀 Uso

### Coleta por Lista de Processos
```bash
# Coleta única
python src/main.py --input input/processos.csv --output output/

# Com limite de movimentações
python src/main.py --input input/processos.csv --output output/ --max-mov 50

# Modo debug (salva HTML bruto)
python src/main.py --input input/processos.csv --output output/ --debug
```

### Busca por Advogado
```bash
python src/main.py --search-lawyer "Adilson Lopes Teixeira" --output output/
```

### Busca por Parte (Condomínio)
```bash
python src/main.py --search-party "Rio Nieva" --output output/
```

### Workflow Completo Rio Nieva
```bash
# Buscar TODOS os processos de "Rio Nieva" e extrair dados completos
python workflow_rio_nieva.py

# Processar em lotes para controle de tempo
python workflow_rio_nieva.py --start 1 --end 10    # Processos 1-10
python workflow_rio_nieva.py --start 11 --end 20   # Processos 11-20
python workflow_rio_nieva.py --start 21 --end 29   # Processos 21-29

# Resultados salvos em: output/rio_nieva_completo/
# - processos_encontrados.json: Lista de processos encontrados
# - processo_completo_*.json: Dados completos de cada processo
# - relatorio_workflow.json: Relatório final
```

### Monitoramento Periódico
```bash
# Verificar novos andamentos a cada 6 horas
python src/main.py --input input/processos.csv --monitor --interval 6h
```

## 📁 Estrutura de Arquivos

### Entrada (`input/processos.csv`)
```csv
processo_numero,etiqueta_opcional
1234567-89.2024.8.26.0100,Condomínio Rio Nieva - Cobrança
9876543-21.2024.8.26.0100,Condomínio Rio Nieva - Execução
```

### Saídas

#### Workflow Rio Nieva (`output/rio_nieva_completo/`)
- `processos_encontrados.json`: Lista completa de processos encontrados
- `processo_completo_*.json`: Dados completos individuais de cada processo
- `relatorio_workflow.json`: Estatísticas e resumo da coleta

#### Formato Individual de Processo
```json
{
  "processo_numero": "1024444-30.2025.8.26.0576",
  "coleta_timestamp": "2025-10-30T19:09:32.533554",
  "vara": "7ª Vara Cível",
  "classe_assunto": "Execução de Título Extrajudicial - Despesas Condominiais",
  "situacao": "Juiz: Ana Maria Chalub De Aquino",
  "movimentacoes": [
    {
      "mov_ordem": 1,
      "mov_data": "14/10/2025",
      "mov_descricao": "Certidão de Publicação Expedida...",
      "mov_texto_completo": "Texto completo da movimentação",
      "palavras_chave_detectadas": ["ACORDO"],
      "decisao_resultado": "NAO_IDENTIFICADO"
    }
  ]
}
```

#### Formato CSV (modo legado)
#### `output/processos.csv`
- Metadados dos processos (vara, classe, valor da causa)
- Partes (exequente, executado)
- Advogados (nome e OAB)

#### `output/movimentacoes.csv`
- Todas as movimentações com data e texto completo
- Classificação automática (palavras-chave detectadas)
- Resultado da decisão (DEFERIDO/INDEFERIDO/PARCIAL)
- Valores bloqueados extraídos

#### `output/analise_estrategica.json`
- Estatísticas consolidadas
- Taxa de sucesso por tipo de medida
- Tempo médio entre fases processuais
- Padrões identificados

## 🔍 Palavras-chave Detectadas

- **Medidas Constritivas**: SISBAJUD, RENAJUD, INFOJUD, SERASAJUD
- **Constrições**: PENHORA, ARRESTO, BLOQUEIO, DESBLOQUEIO
- **Defesas**: EMBARGOS, EXCEÇÃO DE PRÉ-EXECUTIVIDADE
- **Procedimentos**: CITAÇÃO, INTIMAÇÃO, PROTESTO
- **Resolução**: ACORDO, PARCELAMENTO

## ⚠️ Limitações

- Apenas dados públicos (sem login)
- Processos em segredo de justiça não são acessíveis
- PDFs de peças processuais não são baixados
- Sujeito a mudanças no layout do site TJSP

## 📊 Relatórios Gerados

### Dashboard HTML
Após coleta, abra `output/dashboard.html` para visualizar:
- Resumo estatístico dos processos
- Timeline de decisões
- Taxa de sucesso por tipo de medida
- Comparativo entre advogados

## 🔧 Configuração Avançada

### Arquivo `.env`
```env
# Delays entre requisições (segundos)
MIN_DELAY=5
MAX_DELAY=15

# Timeout para carregamento de página (segundos)
PAGE_TIMEOUT=30

# Número de tentativas em caso de erro
MAX_RETRIES=3

# User-agent para requisições
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Horário de execução preferencial (menor tráfego)
PREFERRED_HOURS=22-06

# Modo debug (salva HTML bruto)
DEBUG_MODE=false
```

## 🐛 Troubleshooting

### Erro: "Captcha detectado"
- Aumentar delays no `.env`
- Executar em horários de menor tráfego (22h-6h)
- Reduzir número de processos por lote

### Erro: "Timeout ao carregar página"
- Aumentar `PAGE_TIMEOUT` no `.env`
- Verificar conexão com internet
- Tentar novamente em outro horário

### Erro: "Seletor não encontrado"
- Site TJSP pode ter mudado layout
- Executar com `--debug` para salvar HTML
- Reportar issue com HTML anexado

## 📈 Métricas de Performance

- Tempo médio por processo: 10-15 segundos
- Taxa de sucesso: >95% (exceto manutenções)
- Consumo de memória: ~200MB
- Consumo de banda: ~500KB por processo

## 🔒 Conformidade Legal

- ✅ Respeita robots.txt do TJSP
- ✅ Usa apenas dados públicos
- ✅ Implementa rate limiting
- ✅ Não armazena dados sensíveis desnecessários
- ✅ Conformidade com LGPD

## 📝 Licença

Uso interno - Não distribuir

## 👥 Suporte

Para dúvidas ou problemas, criar issue neste repositório.
