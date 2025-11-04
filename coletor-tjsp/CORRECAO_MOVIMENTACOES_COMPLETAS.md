# 🔧 Correção: Extração de TODAS as Movimentações

## 🎯 Problema Identificado

### Situação Atual:
```json
{
  "total_movimentacoes": 45,
  "movimentacoes": [ ... apenas 5 extraídas ... ]
}
```

**Sistema extrai apenas as últimas 5-10 movimentações, mas o processo tem 45!**

---

## 🔍 Causa Raiz

No site do TJSP, as movimentações funcionam assim:

### 1. **Visualização Inicial**
- Mostra apenas últimas 5-10 movimentações
- Tabela: `tabelaUltimasMovimentacoes`

### 2. **Para Ver Todas**
- Precisa clicar em botão "Ver todas as movimentações"
- Ou link "Exibir todas"
- Carrega tabela completa: `tabelaTodasMovimentacoes`

### 3. **Estrutura HTML**

```html
<!-- Inicialmente visível -->
<table id="tabelaUltimasMovimentacoes">
  <tr><!-- Últimas 5-10 movimentações --></tr>
</table>

<!-- Botão para expandir -->
<a href="#" onclick="exibirTodasMovimentacoes()">
  Ver todas as movimentações (45)
</a>

<!-- Tabela completa (oculta inicialmente) -->
<table id="tabelaTodasMovimentacoes" style="display:none">
  <tr><!-- Todas as 45 movimentações --></tr>
</table>
```

---

## ✅ Solução Implementada

### Passo 1: Detectar Botão "Ver Todas"

```python
async def _expandir_todas_movimentacoes(self):
    """
    Clica no botão 'Ver todas as movimentações' se existir
    
    Returns:
        True se expandiu, False se não havia botão
    """
    try:
        # Seletores possíveis para o botão
        selectors = [
            'a:has-text("Ver todas")',
            'a:has-text("ver todas")',
            'a:has-text("Exibir todas")',
            'a:has-text("exibir todas")',
            'a:has-text("Mostrar todas")',
            'a[onclick*="exibirTodasMovimentacoes"]',
            'a[onclick*="mostrarTodasMovimentacoes"]',
            'button:has-text("Ver todas")',
            '#linkTodasMovimentacoes',
            '.link-todas-movimentacoes'
        ]
        
        for selector in selectors:
            try:
                # Verificar se elemento existe
                element = await self.page.query_selector(selector)
                
                if element:
                    logger.info(f"Botão 'Ver todas' encontrado: {selector}")
                    
                    # Clicar no botão
                    await self.page.click(selector)
                    
                    # Aguardar carregamento
                    await asyncio.sleep(2)
                    await self.page.wait_for_load_state('networkidle')
                    
                    logger.info("✅ Todas as movimentações expandidas")
                    return True
                    
            except Exception as e:
                logger.debug(f"Seletor {selector} não funcionou: {e}")
                continue
        
        logger.debug("Botão 'Ver todas' não encontrado - usando movimentações visíveis")
        return False
        
    except Exception as e:
        logger.error(f"Erro ao expandir movimentações: {e}")
        return False
```

### Passo 2: Usar Tabela Correta

```python
async def extract_movements(self, soup: BeautifulSoup) -> List[Dict]:
    """Extrai movimentações do processo"""
    movimentacoes = []
    
    try:
        # PRIMEIRO: Tentar expandir todas as movimentações
        if self.page:
            await self._expandir_todas_movimentacoes()
            
            # Re-capturar HTML após expansão
            content = await self.page.content()
            soup = BeautifulSoup(content, 'lxml')
        
        # SEGUNDO: Buscar tabela COMPLETA primeiro
        mov_table = None
        
        # Priorizar tabela completa
        selectors = [
            ('tbody', {'id': 'tabelaTodasMovimentacoes'}),  # TODAS (prioritário)
            ('table', {'id': 'tabelaTodasMovimentacoes'}),
            ('tbody', {'id': 'tabelaUltimasMovimentacoes'}),  # Últimas (fallback)
            ('table', {'id': 'tabelaUltimasMovimentacoes'}),
        ]
        
        for tag, attrs in selectors:
            mov_table = soup.find(tag, attrs)
            if mov_table:
                logger.info(f"✅ Tabela encontrada: {tag} {attrs}")
                break
        
        if mov_table:
            rows = mov_table.find_all('tr')
            logger.info(f"📋 Extraindo {len(rows)} movimentações...")
            
            # ... resto do código de extração ...
```

---

## 🚀 Implementação Completa

Vou adicionar a correção ao código:

### Arquivo: `src/scraper.py`

**Localização:** Antes do método `extract_movements` (linha ~545)

**Adicionar:**

```python
async def _expandir_todas_movimentacoes(self):
    """
    Clica no botão 'Ver todas as movimentações' para carregar movimentações completas
    
    Returns:
        True se conseguiu expandir, False caso contrário
    """
    try:
        logger.debug("Tentando expandir todas as movimentações...")
        
        # Lista de seletores possíveis para o botão/link
        selectors = [
            # Texto em português
            'a:has-text("Ver todas")',
            'a:has-text("ver todas")',
            'a:has-text("Exibir todas")',
            'a:has-text("exibir todas")',
            'a:has-text("Mostrar todas")',
            'a:has-text("mostrar todas")',
            'a:has-text("Ver todas as movimentações")',
            
            # Por atributos onclick
            'a[onclick*="exibirTodasMovimentacoes"]',
            'a[onclick*="mostrarTodasMovimentacoes"]',
            'a[onclick*="todasMovimentacoes"]',
            
            # Por ID ou classe
            '#linkTodasMovimentacoes',
            '#verTodasMovimentacoes',
            '.link-todas-movimentacoes',
            '.ver-todas-movimentacoes',
            
            # Botões
            'button:has-text("Ver todas")',
            'button:has-text("Exibir todas")',
        ]
        
        for selector in selectors:
            try:
                # Verificar se elemento existe e está visível
                element = await self.page.query_selector(selector)
                
                if element:
                    # Verificar se está visível
                    is_visible = await element.is_visible()
                    
                    if is_visible:
                        logger.info(f"✅ Botão 'Ver todas' encontrado: {selector}")
                        
                        # Clicar no elemento
                        await element.click()
                        
                        # Aguardar carregamento da tabela completa
                        await asyncio.sleep(2)
                        
                        # Aguardar até que a tabela completa esteja visível
                        try:
                            await self.page.wait_for_selector(
                                'tbody#tabelaTodasMovimentacoes, table#tabelaTodasMovimentacoes',
                                state='visible',
                                timeout=10000
                            )
                            logger.info("✅ Tabela completa de movimentações carregada")
                        except:
                            logger.debug("Tabela completa não apareceu, mas botão foi clicado")
                        
                        await self.page.wait_for_load_state('networkidle')
                        
                        logger.info("✅ Todas as movimentações expandidas com sucesso")
                        return True
                    
            except Exception as e:
                logger.debug(f"Seletor '{selector}' não funcionou: {e}")
                continue
        
        logger.debug("⚠️ Botão 'Ver todas' não encontrado - usando movimentações visíveis")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao tentar expandir movimentações: {e}")
        return False
```

**Modificar método `extract_movements`:**

```python
async def extract_movements(self, soup: BeautifulSoup) -> List[Dict]:
    """
    Extrai movimentações do processo
    
    Args:
        soup: BeautifulSoup object da página
        
    Returns:
        Lista de movimentações
    """
    movimentacoes = []
    
    try:
        # PASSO 1: Tentar expandir todas as movimentações
        if self.page:
            expandiu = await self._expandir_todas_movimentacoes()
            
            if expandiu:
                # Re-capturar HTML após expansão
                logger.debug("Re-capturando HTML após expansão...")
                content = await self.page.content()
                soup = BeautifulSoup(content, 'lxml')
        
        # PASSO 2: Buscar tabela de movimentações
        # Priorizar tabela COMPLETA
        mov_table = None
        
        selectors = [
            # Tabela COMPLETA (prioridade)
            ('tbody', {'id': 'tabelaTodasMovimentacoes'}),
            ('table', {'id': 'tabelaTodasMovimentacoes'}),
            
            # Tabela PARCIAL (fallback)
            ('tbody', {'id': 'tabelaUltimasMovimentacoes'}),
            ('table', {'id': 'tabelaUltimasMovimentacoes'}),
            
            # Outros seletores
            ('tbody', {'id': 'tabelaMovimentacoes'}),
            ('table', {'class': 'movimentacoes'}),
        ]
        
        for tag, attrs in selectors:
            mov_table = soup.find(tag, attrs)
            if mov_table:
                logger.info(f"✅ Tabela de movimentações encontrada: {tag} {attrs}")
                break
        
        if not mov_table:
            logger.warning("⚠️ Nenhuma tabela de movimentações encontrada")
            return movimentacoes
        
        # PASSO 3: Extrair movimentações
        rows = mov_table.find_all('tr')
        logger.info(f"📋 Encontradas {len(rows)} linhas na tabela")
        
        # ... resto do código de extração permanece igual ...
```

---

## 📊 Resultado Esperado

### Antes da Correção:
```json
{
  "total_movimentacoes": 45,
  "movimentacoes": [ ... 5 movimentações ... ]
}
```

### Depois da Correção:
```json
{
  "total_movimentacoes": 45,
  "movimentacoes": [ ... 45 movimentações ... ]
}
```

---

## 🧪 Como Testar

```bash
cd /home/juliano/Projetos/meu_projeto/coletor-tjsp

# Testar com processo específico
python run.py --input input/teste_processo.csv --output output/teste_completo --debug

# Verificar JSON gerado
cat output/teste_completo/todas_movimentacoes_*.json | grep -A 2 "total_movimentacoes"
```

**Verificação:**
- `total_movimentacoes` deve ser igual ao tamanho do array `movimentacoes`

---

## 📝 Checklist de Validação

- [ ] Botão "Ver todas" é detectado
- [ ] Botão é clicado com sucesso
- [ ] Tabela completa é carregada
- [ ] Todas as movimentações são extraídas
- [ ] `total_movimentacoes` == `len(movimentacoes)`

---

**Próximo passo:** Vou implementar essa correção no código agora!
