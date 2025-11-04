# 📊 Comparação: Web Scraping vs API DataJud

## 🎯 Qual Método Usar?

Baseado no seu projeto atual e nas suas necessidades, aqui está uma análise completa.

---

## 📋 Tabela Comparativa Detalhada

| Aspecto | Web Scraping (Atual) | API DataJud (CNJ) |
|---------|---------------------|-------------------|
| **Legalidade** | ✅ Legal (dados públicos) | ✅ 100% Legal (API oficial) |
| **Custo** | Gratuito | Gratuito |
| **Cadastro** | Não requer | Não requer |
| **Chave de Acesso** | Não precisa | Pública (já disponível) |
| **Complexidade** | Média-Alta | Baixa |
| **Manutenção** | Alta (site muda) | Baixa (API estável) |
| **Velocidade** | Lenta (10-15s/processo) | Rápida (1-2s/processo) |
| **CAPTCHA** | ⚠️ Pode bloquear | ✅ Sem CAPTCHA |
| **Rate Limiting** | Sim (6 req/min) | Não documentado |
| **Atualização** | Tempo real | Delay de horas/dias |
| **Cobertura** | Apenas TJSP | Todos os tribunais |
| **Dados Disponíveis** | Completos | Metadados |
| **Documentos (PDFs)** | ✅ Possível | ❌ Não disponível |
| **Confiabilidade** | 70-80% | 95-99% |

---

## 🔍 Análise Detalhada

### 1. **Dados Disponíveis**

#### Web Scraping (TJSP)
```
✅ Metadados do processo
✅ Partes e advogados
✅ Movimentações completas
✅ Decisões e despachos
✅ Valores atualizados
✅ Links para documentos
✅ Informações específicas do TJSP
```

#### API DataJud
```
✅ Metadados do processo
✅ Partes e advogados
✅ Movimentações (resumidas)
✅ Classe e assunto
✅ Órgão julgador
❌ Documentos (PDFs)
❌ Detalhes específicos do tribunal
```

### 2. **Performance**

#### Web Scraping
- **Tempo por processo:** 10-15 segundos
- **Processos/hora:** ~200-300
- **Gargalo:** Navegação do browser, CAPTCHA
- **Consumo de recursos:** Alto (browser completo)

#### API DataJud
- **Tempo por processo:** 1-2 segundos
- **Processos/hora:** ~1.800-3.600
- **Gargalo:** Rate limiting (se houver)
- **Consumo de recursos:** Baixo (apenas HTTP)

### 3. **Confiabilidade**

#### Web Scraping
- ⚠️ Sensível a mudanças no site
- ⚠️ CAPTCHA pode bloquear
- ⚠️ Requer manutenção constante
- ✅ Dados sempre atualizados

#### API DataJud
- ✅ API estável e documentada
- ✅ Sem risco de bloqueio
- ✅ Sem manutenção de seletores
- ⚠️ Dados podem ter delay

---

## 🎯 Recomendações por Caso de Uso

### Caso 1: Monitoramento de Processos Específicos
**Recomendação:** Web Scraping (Atual)

**Motivo:**
- Precisa de dados em tempo real
- Número limitado de processos
- Necessita de detalhes completos

**Exemplo:**
```python
# Monitorar 50 processos específicos do condomínio
python run.py --input processos_condominio.csv --output output/
```

---

### Caso 2: Pesquisa e Análise em Massa
**Recomendação:** API DataJud

**Motivo:**
- Precisa consultar centenas/milhares de processos
- Análise estatística
- Não precisa de documentos

**Exemplo:**
```python
# Buscar todos os processos de um advogado
api = DataJudAPI('tjsp')
processos = api.consultar_por_parte('Adilson Lopes Teixeira', max_resultados=1000)
```

---

### Caso 3: Dashboard e Relatórios
**Recomendação:** Híbrida

**Motivo:**
- Use DataJud para listar processos
- Use Web Scraping para detalhes específicos
- Melhor custo-benefício

**Exemplo:**
```python
# 1. Buscar processos na API DataJud (rápido)
processos = api.consultar_por_parte('Rio Nieva')

# 2. Para cada processo, buscar detalhes via scraping (quando necessário)
for proc in processos_prioritarios:
    detalhes = scraper.search_by_process_number(proc['numero'])
```

---

### Caso 4: Análise Multi-Tribunal
**Recomendação:** API DataJud

**Motivo:**
- Acesso centralizado a todos os tribunais
- Dados padronizados
- Impossível via web scraping (cada tribunal é diferente)

**Exemplo:**
```python
# Buscar processos em múltiplos tribunais
tribunais = ['tjsp', 'tjrj', 'tjmg', 'trf3']
for tribunal in tribunais:
    api = DataJudAPI(tribunal)
    processos = api.consultar_por_parte('Empresa XYZ')
```

---

## 💡 Estratégia Híbrida (Recomendada)

### Arquitetura Proposta

```
┌─────────────────────────────────────────────────┐
│           1. Busca Inicial (DataJud)            │
│  - Listar todos os processos                    │
│  - Filtrar por critérios                        │
│  - Identificar processos de interesse           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      2. Cache e Verificação de Novidades        │
│  - Comparar com processos já coletados          │
│  - Identificar novos processos                  │
│  - Identificar processos atualizados            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│    3. Coleta Detalhada (Web Scraping TJSP)      │
│  - Apenas para processos novos/atualizados      │
│  - Coletar movimentações completas              │
│  - Extrair documentos e anexos                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         4. Armazenamento e Análise              │
│  - Consolidar dados de ambas as fontes          │
│  - Gerar dashboard                              │
│  - Criar relatórios                             │
└─────────────────────────────────────────────────┘
```

### Implementação

```python
class ColetorHibrido:
    """Combina API DataJud com Web Scraping TJSP"""
    
    def __init__(self):
        self.api = DataJudAPI('tjsp')
        self.scraper = TJSPScraper()
        self.cache = ProcessoCache()
    
    async def coletar_processos(self, nome_parte: str):
        """Coleta híbrida: API + Scraping"""
        
        # 1. Buscar lista na API (rápido)
        print("1. Buscando processos na API DataJud...")
        processos_api = self.api.consultar_por_parte(nome_parte, max_resultados=100)
        print(f"   ✅ {len(processos_api)} processos encontrados")
        
        # 2. Filtrar processos que precisam de atualização
        print("\n2. Verificando cache...")
        processos_atualizar = []
        
        for proc in processos_api:
            if self.cache.precisa_atualizar(proc['numero']):
                processos_atualizar.append(proc['numero'])
        
        print(f"   ✅ {len(processos_atualizar)} processos precisam de atualização")
        
        # 3. Coletar detalhes via scraping (apenas necessários)
        print("\n3. Coletando detalhes via web scraping...")
        
        async with self.scraper:
            for i, numero in enumerate(processos_atualizar, 1):
                print(f"   [{i}/{len(processos_atualizar)}] {numero}")
                
                detalhes = await self.scraper.search_by_process_number(numero)
                
                if detalhes:
                    # Mesclar dados da API com dados do scraping
                    processo_completo = self._mesclar_dados(
                        next(p for p in processos_api if p['numero'] == numero),
                        detalhes
                    )
                    
                    self.cache.salvar(processo_completo)
                
                await self.scraper.random_delay()
        
        print("\n✅ Coleta híbrida concluída!")
        return self.cache.listar_todos()
    
    def _mesclar_dados(self, dados_api: dict, dados_scraping: dict) -> dict:
        """Combina dados de ambas as fontes"""
        return {
            **dados_api,  # Dados da API
            'movimentacoes_completas': dados_scraping.get('movimentacoes', []),
            'documentos': dados_scraping.get('documentos', []),
            'detalhes_tjsp': dados_scraping
        }
```

---

## 📈 Análise de Custos

### Cenário: 1.000 Processos

#### Apenas Web Scraping
- **Tempo:** ~4-5 horas
- **Risco de bloqueio:** Alto
- **Manutenção:** Alta
- **Custo computacional:** Alto

#### Apenas API DataJud
- **Tempo:** ~30 minutos
- **Risco de bloqueio:** Zero
- **Manutenção:** Baixa
- **Limitação:** Dados incompletos

#### Híbrido (Recomendado)
- **Tempo:** ~2 horas
- **Risco de bloqueio:** Baixo
- **Manutenção:** Média
- **Resultado:** Dados completos

---

## ✅ Decisão Final

### Para Seu Projeto Específico

Baseado no seu código atual (`coletor-tjsp`) e nos dashboards gerados, recomendo:

#### **Fase 1: Manter Web Scraping (Curto Prazo)**
- ✅ Seu código já funciona
- ✅ Gera dashboards completos
- ✅ Dados específicos do TJSP

**Melhorias:**
1. Implementar cache robusto
2. Melhorar detecção de CAPTCHA
3. Adicionar retry automático

#### **Fase 2: Adicionar API DataJud (Médio Prazo)**
- ✅ Usar para busca inicial de processos
- ✅ Reduzir carga no site TJSP
- ✅ Aumentar velocidade de coleta

**Implementação:**
1. Criar módulo `src/datajud_client.py`
2. Integrar com código existente
3. Usar cache para evitar duplicação

#### **Fase 3: Abordagem Híbrida (Longo Prazo)**
- ✅ Melhor dos dois mundos
- ✅ Máxima eficiência
- ✅ Dados completos

---

## 🚀 Próximos Passos

### 1. Testar API DataJud
```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp
python exemplo_datajud.py
```

### 2. Comparar Resultados
- Execute coleta via web scraping
- Execute coleta via API DataJud
- Compare qualidade dos dados

### 3. Decidir Estratégia
- Se API atende: Migre gradualmente
- Se precisa de mais: Implemente híbrido
- Se específico TJSP: Otimize scraping atual

---

## 📚 Recursos

### Documentação
- **API DataJud:** https://datajud-wiki.cnj.jus.br/api-publica/
- **Seu Projeto:** `ANALISE_VIABILIDADE_LEGAL.md`
- **Exemplo Prático:** `exemplo_datajud.py`

### Suporte
- **Issues GitHub:** Procure "datajud python"
- **Comunidade:** Stack Overflow tag `datajud`

---

**Conclusão:** A melhor estratégia é **híbrida**, usando API DataJud para busca inicial e Web Scraping para detalhes específicos. Isso maximiza velocidade, confiabilidade e completude dos dados.

**Última atualização:** 30/10/2025
