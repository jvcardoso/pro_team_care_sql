"""
Scraper principal para coleta de dados do TJSP
"""
import asyncio
import random
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, TimeoutError
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Config
from .keywords import Keywords


class TJSPScraper:
    """Scraper para coleta de processos do TJSP"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.config = Config()
        self.lock = asyncio.Lock()
        
    async def __aenter__(self):
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def setup(self):
        """Inicializa o browser e configurações"""
        logger.info("Inicializando browser...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.config.HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        context = await self.browser.new_context(
            viewport={'width': self.config.BROWSER_WIDTH, 'height': self.config.BROWSER_HEIGHT},
            user_agent=self.config.USER_AGENT,
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )
        
        self.page = await context.new_page()
        
        # Configurar timeouts
        self.page.set_default_timeout(self.config.PAGE_TIMEOUT)
        
        logger.info("Browser inicializado com sucesso")
    
    async def cleanup(self):
        """Fecha o browser e limpa recursos"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser fechado")
    
    async def random_delay(self):
        """Aplica delay aleatório entre requisições"""
        delay = random.uniform(self.config.MIN_DELAY, self.config.MAX_DELAY)
        logger.debug(f"Aguardando {delay:.1f} segundos...")
        await asyncio.sleep(delay)
    
    async def save_screenshot(self, name: str):
        """Salva screenshot para debug"""
        if self.config.SAVE_SCREENSHOTS and self.page:
            path = self.config.get_cache_path(f"{name}_{datetime.now():%Y%m%d_%H%M%S}.png")
            await self.page.screenshot(path=path)
            logger.debug(f"Screenshot salvo: {path}")
    
    async def save_html(self, processo_numero: str, content: str):
        """Salva HTML bruto para debug"""
        if self.config.DEBUG_MODE:
            path = self.config.get_cache_path(f"{processo_numero}.html")
            path.write_text(content, encoding='utf-8')
            logger.debug(f"HTML salvo: {path}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def search_by_process_number(self, processo_numero: str) -> Optional[Dict]:
        """
        Busca processo por número

        Args:
            processo_numero: Número do processo no formato CNJ

        Returns:
            Dados do processo ou None se não encontrado
        """
        logger.info(f"Buscando processo: {processo_numero}")

        try:
                # Método 1: Tentar busca direta via URL
            try:
                # Construir URL de busca direta
                search_params = {
                    'cbPesquisa': 'NUMPROC',
                    'numeroDigitoAnoUnificado': processo_numero[:15],  # primeiros 15 dígitos (até o ano)
                    'foroNumeroUnificado': processo_numero[-4:],  # últimos 4 dígitos
                    'dadosConsulta.valorConsultaNuUnificado': processo_numero,
                    'dadosConsulta.tipoNuProcesso': 'UNIFICADO'
                }

                query_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
                search_url = f"{self.config.TJSP_SEARCH_URL}?{query_string}"

                logger.debug(f"Tentando busca direta: {search_url}")
                await self.page.goto(search_url)
                await self.page.wait_for_load_state('networkidle')
                await self.random_delay()

                content = await self.page.content()

                # Verificar se é página de detalhes
                soup = BeautifulSoup(content, 'lxml')
                if soup.find('div', {'id': 'dadosDoProcesso'}) or "Movimentações" in content:
                    logger.info(f"Busca direta bem-sucedida para {processo_numero}")
                    await self.save_html(processo_numero, content)
                    return await self.extract_process_data(content, processo_numero)

                # Verificar se encontrou resultados
                if "tipo de pesquisa informado é inválido" in content:
                    logger.error(f"Tipo de pesquisa inválido para processo {processo_numero}")
                    return None

                if "Não existem informações" not in content and "segredo de justiça" not in content:
                    # Procurar links de processo
                    links = soup.find_all('a', {'class': 'linkMovVincProc'})
                    if links:
                        logger.info(f"Encontrados {len(links)} links de processo")
                        # Usar o primeiro link
                        href = links[0].get('href')
                        if href.startswith('/'):
                            href = f"{self.config.TJSP_BASE_URL}{href}"

                        await self.page.goto(href)
                        await self.page.wait_for_load_state('networkidle')
                        await self.random_delay()

                        detail_content = await self.page.content()
                        await self.save_html(processo_numero, detail_content)
                        return await self.extract_process_data(detail_content, processo_numero)

            except Exception as e:
                logger.debug(f"Busca direta falhou: {e}")

            # Método 2: Busca via formulário (fallback)
            logger.debug("Tentando busca via formulário")
            await self.page.goto(self.config.TJSP_SEARCH_URL)
            await self.random_delay()

            # Aguardar carregamento completo
            await self.page.wait_for_load_state('networkidle')
            await self.random_delay()

            # Selecionar tipo de busca por número
            await self.page.select_option('#cbPesquisa', 'NUMPROC')
            await self.random_delay()

            # Aguardar campos serem habilitados
            await self.page.wait_for_selector('#numeroDigitoAnoUnificado:not([disabled])', timeout=5000)

            # Preencher campos
            await self.page.fill('#numeroDigitoAnoUnificado', processo_numero[:15])
            await self.page.fill('#foroNumeroUnificado', processo_numero[-4:])

            # Submeter busca
            await self.page.click('#botaoConsultarProcessos')
            await self.page.wait_for_load_state('networkidle')
            await self.random_delay()

            # Verificar resultado
            content = await self.page.content()

            if "tipo de pesquisa informado é inválido" in content:
                logger.error(f"Tipo de pesquisa inválido para processo {processo_numero}")
                return None

            if "Não existem informações" in content or "segredo de justiça" in content:
                logger.warning(f"Processo {processo_numero} não encontrado ou em segredo")
                return None

            # Verificar se é página de detalhes
            soup = BeautifulSoup(content, 'lxml')
            if soup.find('div', {'id': 'dadosDoProcesso'}) or "Movimentações" in content:
                logger.info(f"Página de detalhes carregada via formulário para {processo_numero}")
                await self.save_html(processo_numero, content)
                return await self.extract_process_data(content, processo_numero)

            # Procurar links
            links = soup.find_all('a', {'class': 'linkMovVincProc'})
            if links:
                logger.info(f"Encontrados {len(links)} links via formulário")
                # Usar primeiro link
                href = links[0].get('href')
                if href.startswith('/'):
                    href = f"{self.config.TJSP_BASE_URL}{href}"

                await self.page.goto(href)
                await self.page.wait_for_load_state('networkidle')
                await self.random_delay()

                detail_content = await self.page.content()
                await self.save_html(processo_numero, detail_content)
                return await self.extract_process_data(detail_content, processo_numero)

            # Método 3: Tentar acesso direto via URL do processo
            try:
                logger.debug(f"Tentando acesso direto ao processo: {processo_numero}")
                direct_url = f"{self.config.TJSP_OPEN_URL}?processo.numero={processo_numero}"

                await self.page.goto(direct_url)
                await self.page.wait_for_load_state('networkidle')
                await self.random_delay()

                direct_content = await self.page.content()
                soup_direct = BeautifulSoup(direct_content, 'lxml')

                # Verificar se carregou página de processo
                if soup_direct.find('div', {'id': 'dadosDoProcesso'}) or "Movimentações" in direct_content:
                    logger.info(f"Acesso direto bem-sucedido para {processo_numero}")
                    await self.save_html(processo_numero, direct_content)
                    return await self.extract_process_data(direct_content, processo_numero)

                # Verificar se é página de erro ou não encontrado
                if "Não existem informações" in direct_content or "segredo de justiça" in direct_content:
                    logger.warning(f"Processo {processo_numero} não encontrado ou em segredo")
                    return None

                logger.debug(f"Acesso direto não resultou em página de processo válida")

            except Exception as e:
                logger.debug(f"Acesso direto falhou: {e}")

            logger.warning(f"Nenhum resultado encontrado para {processo_numero}")
            return None

        except TimeoutError:
            logger.error(f"Timeout ao buscar processo {processo_numero}")
            await self.save_screenshot(f"timeout_{processo_numero}")
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar processo {processo_numero}: {e}")
            await self.save_screenshot(f"error_{processo_numero}")
            raise
    
    async def search_by_lawyer(self, lawyer_name: str, max_pages: int = 10) -> List[str]:
        """
        Busca processos por nome do advogado
        
        Args:
            lawyer_name: Nome do advogado
            max_pages: Máximo de páginas para buscar
            
        Returns:
            Lista de números de processos
        """
        logger.info(f"Buscando processos do advogado: {lawyer_name}")
        processos = []
        
        try:
            # Navegar para página de busca
            await self.page.goto(self.config.TJSP_SEARCH_URL)
            await self.random_delay()
            
            # Selecionar tipo de busca por advogado
            await self.page.select_option('#cbPesquisa', 'NMADVOGADO')
            await self.random_delay()

            # Aguardar campo específico ser habilitado
            await self.page.wait_for_selector('#campo_NMADVOGADO:not([disabled])', timeout=10000)
            await self.page.fill('#campo_NMADVOGADO', lawyer_name)

            # Submeter busca
            await self.page.click('#botaoConsultarProcessos')
            await self.page.wait_for_load_state('networkidle')
            await self.random_delay()
            
            # Coletar processos de todas as páginas
            for page_num in range(1, max_pages + 1):
                logger.info(f"Coletando página {page_num}")
                
                content = await self.page.content()
                page_processos = self.extract_process_numbers_from_list(content)
                processos.extend(page_processos)
                
                # Verificar se há próxima página
                if not await self.has_next_page():
                    break
                
                # Navegar para próxima página
                await self.goto_next_page()
                await self.random_delay()
            
            logger.info(f"Total de processos encontrados: {len(processos)}")
            return processos
            
        except Exception as e:
            logger.error(f"Erro ao buscar por advogado {lawyer_name}: {e}")
            return processos
    
    async def search_by_party(self, party_name: str, max_pages: int = 10) -> List[str]:
        """
        Busca processos por nome da parte
        
        Args:
            party_name: Nome da parte
            max_pages: Máximo de páginas para buscar
            
        Returns:
            Lista de números de processos
        """
        logger.info(f"Buscando processos da parte: {party_name}")
        processos = []
        
        try:
            # Navegar para página de busca
            await self.page.goto(self.config.TJSP_SEARCH_URL)
            await self.random_delay()
            
            # Selecionar tipo de busca por parte
            await self.page.select_option('#cbPesquisa', 'NMPARTE')
            await self.random_delay()

            # Aguardar campo específico ser habilitado
            await self.page.wait_for_selector('#campo_NMPARTE:not([disabled])', timeout=10000)
            await self.page.fill('#campo_NMPARTE', party_name)

            # Submeter busca
            await self.page.click('#botaoConsultarProcessos')
            await self.page.wait_for_load_state('networkidle')
            await self.random_delay()

            # Obter total de processos na primeira página para calcular páginas necessárias
            content = await self.page.content()
            total_processos = self.extract_total_process_count(content)
            processos_por_pagina = 25  # TJSP mostra 25 processos por página

            if total_processos > 0:
                paginas_necessarias = (total_processos + processos_por_pagina - 1) // processos_por_pagina
                paginas_a_percorrer = min(paginas_necessarias, max_pages)
                logger.info(f"Total de processos: {total_processos}, Páginas necessárias: {paginas_necessarias}, Páginas a percorrer: {paginas_a_percorrer}")
            else:
                paginas_a_percorrer = max_pages

            # Coletar processos de todas as páginas necessárias
            for page_num in range(1, paginas_a_percorrer + 1):
                logger.info(f"Coletando página {page_num}")

                if page_num > 1:
                    content = await self.page.content()

                page_processos = self.extract_process_numbers_from_list(content)
                processos.extend(page_processos)

                # Verificar se há próxima página e se ainda precisamos continuar
                if page_num >= paginas_a_percorrer or not await self.has_next_page():
                    break

                # Navegar para próxima página
                await self.goto_next_page()
                await self.random_delay()

            logger.info(f"Total de processos encontrados: {len(processos)}")
            return processos
            
        except Exception as e:
            logger.error(f"Erro ao buscar por parte {party_name}: {e}")
            return processos
    
    async def extract_process_data(self, html: str, processo_numero: str) -> Dict:
        """
        Extrai dados do processo do HTML
        
        Args:
            html: HTML da página do processo
            processo_numero: Número do processo
            
        Returns:
            Dicionário com dados do processo
        """
        soup = BeautifulSoup(html, 'lxml')
        
        data = {
            'processo_numero': processo_numero,
            'coleta_timestamp': datetime.now().isoformat(),
            'vara': '',
            'classe_assunto': '',
            'valor_causa': '',
            'exequente': '',
            'executado': '',
            'advogado_autor_nome': '',
            'advogado_autor_oab': '',
            'advogado_reu_nome': '',
            'advogado_reu_oab': '',
            'situacao': '',
            'movimentacoes': []
        }
        
        try:
            # Extrair dados básicos - tentar múltiplas estruturas HTML
            
            # Método 1: Estrutura atual com IDs específicos (mais confiável)
            classe_elem = soup.find('span', {'id': 'classeProcesso'})
            if classe_elem:
                data['classe_assunto'] = classe_elem.get_text(strip=True)
                logger.debug(f"Classe extraída por ID: {data['classe_assunto']}")
            
            vara_elem = soup.find('span', {'id': 'varaProcesso'})
            if vara_elem:
                data['vara'] = vara_elem.get_text(strip=True)
                logger.debug(f"Vara extraída por ID: {data['vara']}")
            
            juiz_elem = soup.find('span', {'id': 'juizProcesso'})
            if juiz_elem:
                data['situacao'] = f"Juiz: {juiz_elem.get_text(strip=True)}"
                logger.debug(f"Juiz extraído por ID: {juiz_elem.get_text(strip=True)}")
            
            assunto_elem = soup.find('span', {'id': 'assuntoProcesso'})
            if assunto_elem:
                assunto = assunto_elem.get_text(strip=True)
                if data['classe_assunto']:
                    data['classe_assunto'] += f" - {assunto}"
                else:
                    data['classe_assunto'] = assunto
                logger.debug(f"Assunto extraído por ID: {assunto}")
            
            # Método 2: Estrutura antiga com dadosDoProcesso (fallback)
            if not data['vara']:
                dados_processo = soup.find('div', {'id': 'dadosDoProcesso'})
                if dados_processo:
                    # Vara
                    vara_elem = dados_processo.find('span', text=re.compile('Vara'))
                    if vara_elem:
                        data['vara'] = vara_elem.get_text(strip=True)

                    # Classe e assunto
                    classe_elem = dados_processo.find('span', text=re.compile('Classe'))
                    if classe_elem:
                        data['classe_assunto'] = classe_elem.find_next_sibling().get_text(strip=True)

                    # Valor da causa
                    valor_elem = dados_processo.find('span', text=re.compile('Valor'))
                    if valor_elem:
                        data['valor_causa'] = valor_elem.find_next_sibling().get_text(strip=True)

            # Método 3: Extrair de texto direto (último recurso)
            if not data['vara']:
                # Procurar seções por texto
                text_content = soup.get_text()
                logger.debug(f"Extraindo dados de texto. Tamanho do texto: {len(text_content)}")

                # Extrair dados básicos - procurar por labels seguidas de valores
                lines = text_content.split('\n')
                current_label = None

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Verificar se é um label
                    if line in ['Classe', 'Assunto', 'Foro', 'Vara', 'Juiz', 'Valor da causa']:
                        current_label = line
                    elif current_label:
                        # Esta linha deve ser o valor do label anterior
                        if current_label == 'Classe':
                            data['classe_assunto'] = line
                            logger.debug(f"Classe encontrada: {line}")
                        elif current_label == 'Assunto':
                            if data['classe_assunto']:
                                data['classe_assunto'] += f" - {line}"
                            else:
                                data['classe_assunto'] = line
                            logger.debug(f"Assunto encontrado: {line}")
                        elif current_label == 'Vara':
                            data['vara'] = line
                            logger.debug(f"Vara encontrada: {line}")
                        elif current_label == 'Juiz':
                            data['situacao'] = f"Juiz: {line}"
                            logger.debug(f"Juiz encontrado: {line}")
                        elif current_label == 'Valor da causa':
                            data['valor_causa'] = line

                    current_label = None  # Reset para próximo label

            # Extrair partes - tentar múltiplas estruturas
            # Método 1: Tabela estruturada (estrutura atual do TJSP)
            partes_table = soup.find('table', {'id': 'tablePartesPrincipais'})
            
            if partes_table:
                logger.debug("✅ Encontrada tabela tablePartesPrincipais")
                for row in partes_table.find_all('tr'):
                    # Buscar célula com tipo de participação
                    tipo_cell = row.find('td', {'class': 'label'})
                    nome_cell = row.find('td', {'class': 'nomeParteEAdvogado'})
                    
                    if tipo_cell and nome_cell:
                        tipo_text = tipo_cell.get_text(strip=True)
                        logger.debug(f"Tipo encontrado: '{tipo_text}'")
                        
                        # Extrair nome da parte (primeira linha do texto)
                        nome_completo = nome_cell.get_text(separator='\n', strip=True)
                        linhas_nome = [l.strip() for l in nome_completo.split('\n') if l.strip()]
                        
                        if linhas_nome:
                            nome_parte = linhas_nome[0]
                            logger.debug(f"Nome extraído: '{nome_parte}'")
                            
                            # Identificar tipo de parte
                            if 'exeq' in tipo_text.lower():
                                data['exequente'] = nome_parte
                                logger.info(f"✅ Exequente: {nome_parte}")
                                
                                # Buscar advogado do exequente - Método 1: Por texto
                                for linha in linhas_nome[1:]:
                                    if 'advogado' in linha.lower():
                                        # Extrair nome e OAB
                                        adv_match = re.search(r'([^(]+)\s*\(OAB\s*(\d+/\w+)\)', linha)
                                        if adv_match:
                                            data['advogado_autor_nome'] = adv_match.group(1).strip()
                                            data['advogado_autor_oab'] = adv_match.group(2).strip()
                                            logger.info(f"✅ Advogado autor: {data['advogado_autor_nome']} - OAB {data['advogado_autor_oab']}")
                                
                                # Buscar advogado do exequente - Método 2: Por span
                                if not data['advogado_autor_nome']:
                                    adv_span = nome_cell.find('span', text=re.compile('Advogado'))
                                    if adv_span:
                                        # Pegar próximo texto após o span
                                        adv_text = adv_span.find_next(string=True)
                                        if adv_text:
                                            adv_nome = adv_text.strip()
                                            if adv_nome:
                                                data['advogado_autor_nome'] = adv_nome
                                                logger.info(f"✅ Advogado autor (span): {adv_nome}")
                            
                            elif 'exec' in tipo_text.lower() or 'réu' in tipo_text.lower():
                                data['executado'] = nome_parte
                                logger.info(f"✅ Executado: {nome_parte}")
                                
                                # Buscar advogado do executado
                                for linha in linhas_nome[1:]:
                                    if 'advogado' in linha.lower():
                                        # Extrair nome e OAB
                                        adv_match = re.search(r'([^(]+)\s*\(OAB\s*(\d+/\w+)\)', linha)
                                        if adv_match:
                                            data['advogado_reu_nome'] = adv_match.group(1).strip()
                                            data['advogado_reu_oab'] = adv_match.group(2).strip()
                                            logger.info(f"✅ Advogado réu: {data['advogado_reu_nome']} - OAB {data['advogado_reu_oab']}")
            else:
                logger.debug("⚠️ Tabela tablePartesPrincipais não encontrada")
            
            logger.debug(f"Dados extraídos - Vara: '{data['vara']}', Classe: '{data['classe_assunto']}', Exeq: '{data['exequente']}', Exec: '{data['executado']}'")
            
            # Extrair movimentações
            movimentacoes = await self.extract_movements(soup)
            data['movimentacoes'] = movimentacoes
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do processo: {e}")
        
        return data

    async def _extrair_texto_completo_movimentacao(self, desc_elem: BeautifulSoup, idx: int) -> str:
        """
        Extrai o texto completo de uma movimentação, incluindo decisões judiciais detalhadas

        Args:
            desc_elem: Elemento BeautifulSoup da descrição da movimentação
            idx: Índice da movimentação

        Returns:
            Texto completo da movimentação ou string vazia se não conseguir extrair
        """
        try:
            # Primeiro tentar encontrar texto já expandido na página
            texto_completo = desc_elem.get_text(separator='\n', strip=True)

            # Verificar se há link "Mais" ou "Ver mais" para expandir
            mais_link = desc_elem.find('a', text=re.compile(r'Mais|mais|Ver mais|ver mais', re.IGNORECASE))
            if mais_link and self.page:
                try:
                    logger.debug(f"Tentando expandir movimentação {idx}...")

                    # Tentar diferentes seletores para o link
                    link_selectors = [
                        f'td.descricaoMovimentacao a:has-text("Mais")',
                        f'td.descricaoMovimentacao a:has-text("mais")',
                        f'a[href*="expandir"]',
                        f'a[onclick*="expandir"]'
                    ]

                    for selector in link_selectors:
                        try:
                            await self.page.click(selector)
                            await asyncio.sleep(1)
                            break
                        except:
                            continue

                    # Aguardar carregamento
                    await self.page.wait_for_load_state('networkidle')
                    await asyncio.sleep(0.5)

                    # Re-capturar conteúdo da página
                    new_content = await self.page.content()
                    new_soup = BeautifulSoup(new_content, 'lxml')

                    # Re-encontrar a movimentação específica
                    new_mov_table = new_soup.find('tbody', {'id': 'tabelaTodasMovimentacoes'}) or \
                                   new_soup.find('table', {'id': 'tabelaUltimasMovimentacoes'})

                    if new_mov_table:
                        new_rows = new_mov_table.find_all('tr')
                        if idx <= len(new_rows):
                            new_row = new_rows[idx-1]
                            new_tds = new_row.find_all('td')
                            if len(new_tds) >= 2:
                                new_desc_elem = new_tds[1]
                                texto_expandido = new_desc_elem.get_text(separator='\n', strip=True)

                                # Verificar se o texto foi realmente expandido
                                if len(texto_expandido) > len(texto_completo):
                                    texto_completo = texto_expandido
                                    logger.debug(f"Movimentação {idx} expandida com sucesso")

                except Exception as e:
                    logger.debug(f"Não foi possível expandir movimentação {idx}: {e}")

            # Limpar e formatar o texto
            if texto_completo:
                # Remover espaços extras e quebras de linha desnecessárias
                texto_completo = re.sub(r'\n+', '\n', texto_completo)
                texto_completo = re.sub(r' +', ' ', texto_completo)
                texto_completo = texto_completo.strip()

            return texto_completo

        except Exception as e:
            logger.debug(f"Erro ao extrair texto completo da movimentação {idx}: {e}")
            return ""

    def _contem_decisao_judicial(self, texto: str) -> bool:
        """
        Verifica se o texto contém uma decisão judicial detalhada

        Args:
            texto: Texto da movimentação

        Returns:
            True se contém decisão judicial, False caso contrário
        """
        indicadores_decisao = [
            'visto', 'vistos', 'decido', 'decidiu', 'determino', 'ordeno',
            'defiro', 'indefiro', 'julgo', 'condeno', 'absolvo',
            'art.', 'artigo', 'lei nº', 'cpc', 'cpp',
            'sisbajud', 'renajud', 'infojud', 'cnib',
            'bloqueio', 'penhora', 'arresto', 'sequestro',
            'intime-se', 'intimem-se', 'citem-se',
            'provimento', 'recurso', 'agravo', 'apelação'
        ]

        texto_lower = texto.lower()
        return any(indicador in texto_lower for indicador in indicadores_decisao)
    
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
                # Texto em português - "Mais" é o botão real observado
                'a:has-text("Mais")',
                'a:has-text("mais")',
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
                'a[onclick*="mais"]',
                'a[onclick*="expandir"]',

                # Por ID ou classe
                '#linkTodasMovimentacoes',
                '#verTodasMovimentacoes',
                '.link-todas-movimentacoes',
                '.ver-todas-movimentacoes',
                '#linkMaisMovimentacoes',
                '.mais-movimentacoes',

                # Botões
                'button:has-text("Mais")',
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

            # Tentar diferentes seletores (COMPLETA primeiro, depois PARCIAL)
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
                ('div', {'id': 'divMovimentacoes'}),
            ]

            for tag, attrs in selectors:
                mov_table = soup.find(tag, attrs)
                if mov_table:
                    logger.info(f"✅ Tabela de movimentações encontrada: {tag} {attrs}")
                    break
            
            if not mov_table:
                logger.warning("⚠️ Nenhuma tabela de movimentações encontrada")
                return movimentacoes

            if mov_table:
                rows = mov_table.find_all('tr')
                logger.info(f"📋 Encontradas {len(rows)} linhas na tabela de movimentações")

                for idx, row in enumerate(rows, 1):
                    # Pular cabeçalhos
                    if row.find('th'):
                        continue

                    mov = {
                        'mov_ordem': idx,
                        'mov_data': '',
                        'mov_descricao': '',
                        'mov_texto_completo': '',
                        'mov_tipo': '',
                        'mov_detalhes': '',
                        'palavras_chave_detectadas': [],
                        'decisao_resultado': 'NAO_IDENTIFICADO',
                        'valor_bloqueado': '',
                        'contem_decisao_judicial': False,
                        'coleta_timestamp': datetime.now().isoformat()
                    }

                    tds = row.find_all('td')
                    if len(tds) >= 3:
                        # Data (primeira coluna)
                        mov['mov_data'] = tds[0].get_text(strip=True)

                        # Texto da movimentação (terceira coluna, pulando célula vazia)
                        desc_elem = tds[2]

                        # Extrair descrição básica
                        mov['mov_descricao'] = ' '.join(desc_elem.stripped_strings)

                        # Tentar extrair texto completo da decisão judicial
                        texto_completo = await self._extrair_texto_completo_movimentacao(desc_elem, idx)
                        mov['mov_texto_completo'] = texto_completo

                        # Usar texto completo se disponível, senão descrição básica
                        mov['mov_texto'] = texto_completo if texto_completo else mov['mov_descricao']

                        # Verificar se contém decisão judicial
                        mov['contem_decisao_judicial'] = self._contem_decisao_judicial(mov['mov_texto'])

                    # Classificar movimentação
                    if mov['mov_texto']:
                        mov['palavras_chave_detectadas'] = Keywords.detect_keywords(mov['mov_texto'])
                        mov['decisao_resultado'] = Keywords.classify_decision(mov['mov_texto'])

                        # Extrair valores
                        valores = Keywords.extract_values(mov['mov_texto'])
                        if valores:
                            mov['valor_bloqueado'] = valores[0]  # Pegar primeiro valor encontrado

                    movimentacoes.append(mov)

                    # Limitar número de movimentações
                    if self.config.MAX_MOVIMENTACOES > 0 and len(movimentacoes) >= self.config.MAX_MOVIMENTACOES:
                        break

            else:
                logger.warning("Tabela de movimentações não encontrada na página")

        except Exception as e:
            logger.error(f"Erro ao extrair movimentações: {e}")
            import traceback
            traceback.print_exc()

        logger.info(f"Extraídas {len(movimentacoes)} movimentações")
        return movimentacoes
    
    def extract_total_process_count(self, html: str) -> int:
        """
        Extrai o total de processos da página de resultados

        Args:
            html: HTML da página de resultados

        Returns:
            Total de processos encontrados ou 0 se não conseguir extrair
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            # Procurar por texto indicando total de processos
            # Padrões comuns: "Exibindo X a Y de Z processos", "Total: Z processos", etc.
            patterns = [
                r'exibindo.*?de\s+(\d+)\s+processos?',
                r'total.*?:\s*(\d+)',
                r'(\d+)\s+processos?\s+encontrados?',
                r'de\s+(\d+)\s+resultados?',
                r'(\d+)\s+registros?'
            ]

            text_content = soup.get_text().lower()

            for pattern in patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    total = int(match.group(1))
                    logger.debug(f"Total de processos extraído: {total}")
                    return total

            # Tentar encontrar em elementos específicos
            result_info = soup.find('div', {'class': 'result-info'}) or \
                         soup.find('span', {'class': 'total-results'}) or \
                         soup.find('p', text=re.compile(r'processos?|resultados?', re.IGNORECASE))

            if result_info:
                text = result_info.get_text()
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        total = int(match.group(1))
                        logger.debug(f"Total de processos extraído de elemento específico: {total}")
                        return total

            logger.debug("Não foi possível extrair total de processos da página")
            return 0

        except Exception as e:
            logger.error(f"Erro ao extrair total de processos: {e}")
            return 0

    def extract_process_numbers_from_list(self, html: str) -> List[str]:
        """
        Extrai números de processos de uma página de lista

        Args:
            html: HTML da página de lista

        Returns:
            Lista de números de processos
        """
        processos = []
        soup = BeautifulSoup(html, 'lxml')

        # Buscar links de processos
        links = soup.find_all('a', {'class': 'linkProcesso'})
        for link in links:
            # Extrair número do processo do texto ou href
            texto = link.get_text(strip=True)
            # Padrão CNJ: XXXXXXX-XX.XXXX.X.XX.XXXX
            import re
            match = re.search(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', texto)
            if match:
                processos.append(match.group())

        return processos

    def extract_total_process_count(self, html: str) -> int:
        """
        Extrai o total de processos da página de resultados

        Args:
            html: HTML da página de resultados

        Returns:
            Total de processos encontrados ou 0 se não conseguir extrair
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            # Procurar por texto indicando total de processos
            # Padrões comuns: "Exibindo X a Y de Z processos", "Total: Z processos", etc.
            patterns = [
                r'exibindo.*?de\s+(\d+)\s+processos?',
                r'total.*?:\s*(\d+)',
                r'(\d+)\s+processos?\s+encontrados?',
                r'de\s+(\d+)\s+resultados?',
                r'(\d+)\s+registros?'
            ]

            text_content = soup.get_text().lower()

            for pattern in patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    total = int(match.group(1))
                    logger.debug(f"Total de processos extraído: {total}")
                    return total

            # Tentar encontrar em elementos específicos
            result_info = soup.find('div', {'class': 'result-info'}) or \
                         soup.find('span', {'class': 'total-results'}) or \
                         soup.find('p', text=re.compile(r'processos?|resultados?', re.IGNORECASE))

            if result_info:
                text = result_info.get_text()
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        total = int(match.group(1))
                        logger.debug(f"Total de processos extraído de elemento específico: {total}")
                        return total

            logger.debug("Não foi possível extrair total de processos da página")
            return 0

        except Exception as e:
            logger.error(f"Erro ao extrair total de processos: {e}")
            return 0

    async def has_next_page(self) -> bool:
        """Verifica se há próxima página"""
        try:
            # Buscar link de próxima página (pela classe CSS)
            next_button = await self.page.query_selector('a.unj-pagination__next')
            return next_button is not None
        except:
            return False

    async def goto_next_page(self):
        """Navega para próxima página"""
        try:
            await self.page.click('a.unj-pagination__next')
            await self.page.wait_for_load_state('networkidle')
            await self.random_delay()
        except Exception as e:
            logger.error(f"Erro ao navegar para próxima página: {e}")
