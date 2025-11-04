"""
Coletor Híbrido: API DataJud + Web Scraping
Abordagem recomendada para máxima eficiência e confiabilidade
"""
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

from .datajud_api import DataJudAPI
from .scraper import TJSPScraper
from .cache_manager import CacheManager
from .config import Config


class HybridCollector:
    """
    Coletor híbrido que combina API DataJud com web scraping

    Estratégia:
    1. Usa API DataJud para busca rápida e metadados
    2. Usa web scraping para detalhes específicos do TJSP
    3. Combina dados para resultado completo
    """

    def __init__(self):
        self.api = DataJudAPI('tjsp')
        self.scraper = None  # Inicializado sob demanda
        self.config = Config()
        self.cache = CacheManager(self.config)  # Sistema de cache inteligente

    async def _get_scraper(self):
        """Obtém instância do scraper (lazy loading)"""
        if self.scraper is None:
            self.scraper = TJSPScraper()
            await self.scraper.__aenter__()
        return self.scraper

    def _mesclar_dados_api_scraping(self, dados_api: Dict[str, Any], dados_scraping: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mescla dados da API DataJud com dados de web scraping

        Args:
            dados_api: Dados da API DataJud
            dados_scraping: Dados do web scraping

        Returns:
            Dados mesclados com prioridade para API, complementados com scraping
        """
        # Começar com dados da API (mais confiáveis)
        dados_mesclados = dados_api.copy()

        # Adicionar fonte composta
        dados_mesclados['fonte'] = 'API DataJud + Web Scraping (TJSP)'

        # Adicionar dados complementares do scraping
        dados_mesclados['dados_complementares'] = {
            'vara_detalhada': dados_scraping.get('vara', ''),
            'situacao': dados_scraping.get('situacao', ''),
            'valor_causa_formatado': dados_scraping.get('valor_causa', ''),
        }

        # Adicionar partes do processo (informação exclusiva do scraping)
        partes = {}
        if dados_scraping.get('exequente'):
            partes['exequente'] = dados_scraping['exequente']
        if dados_scraping.get('executado'):
            partes['executado'] = dados_scraping['executado']

        # Adicionar advogados se disponíveis
        advogados = {}
        if dados_scraping.get('advogado_autor_nome'):
            advogados['autor'] = {
                'nome': dados_scraping.get('advogado_autor_nome', ''),
                'oab': dados_scraping.get('advogado_autor_oab', '')
            }
        if dados_scraping.get('advogado_reu_nome'):
            advogados['reu'] = {
                'nome': dados_scraping.get('advogado_reu_nome', ''),
                'oab': dados_scraping.get('advogado_reu_oab', '')
            }

        if partes:
            dados_mesclados['partes'] = partes
        if advogados:
            dados_mesclados['advogados'] = advogados

        # Adicionar movimentações detalhadas se disponíveis
        if dados_scraping.get('movimentacoes'):
            # Filtrar apenas movimentações que contenham decisões judiciais
            decisoes_judiciais = [
                mov for mov in dados_scraping['movimentacoes']
                if mov.get('contem_decisao_judicial', False)
            ]

            if decisoes_judiciais:
                dados_mesclados['decisoes_judiciais'] = decisoes_judiciais
                logger.debug(f"Adicionadas {len(decisoes_judiciais)} decisões judiciais")

        # Adicionar timestamp de enriquecimento
        dados_mesclados['data_enriquecimento'] = datetime.now().isoformat()

        return dados_mesclados

    async def coletar_por_numeros(self, numeros_processos: List[str]) -> List[Dict[str, Any]]:
        """
        Coleta dados de múltiplos processos por número

        Estratégia híbrida:
        1. Primeiro tenta API DataJud (rápido, confiável)
        2. Se não encontrar, tenta web scraping (mais detalhes)
        3. Combina resultados

        Args:
            numeros_processos: Lista de números de processos

        Returns:
            Lista com dados dos processos encontrados
        """
        logger.info(f"Iniciando coleta híbrida de {len(numeros_processos)} processos")

        resultados = []

        for numero in numeros_processos:
            logger.info(f"Processando: {numero}")

            # 1. Verificar cache primeiro
            cached_result = self.cache.get('numero_processo', {'numero': numero})
            if cached_result:
                logger.success(f"Processo {numero} encontrado no cache")
                resultados.append(cached_result)
                continue

            # 2. Tentar API DataJud primeiro (mais rápido e confiável)
            processo_api = self.api.consultar_por_numero(numero)

            if processo_api:
                logger.success(f"Processo {numero} encontrado via API DataJud")

                # Tentar enriquecer com dados de scraping (partes do processo)
                try:
                    logger.debug(f"Tentando enriquecer dados da API com scraping para {numero}")
                    scraper = await self._get_scraper()
                    dados_scraping = await scraper.search_by_process_number(numero)

                    if dados_scraping:
                        # Mesclar dados da API com dados de scraping
                        processo_completo = self._mesclar_dados_api_scraping(processo_api, dados_scraping)
                        logger.success(f"Dados enriquecidos com partes do processo para {numero}")
                        # Salvar no cache
                        self.cache.set('numero_processo', {'numero': numero}, processo_completo, 'api_datajud')
                        resultados.append(processo_completo)
                        continue
                except Exception as e:
                    logger.debug(f"Não foi possível enriquecer dados para {numero}: {e}")

                # Se não conseguiu enriquecer, usar apenas dados da API
                self.cache.set('numero_processo', {'numero': numero}, processo_api, 'api_datajud')
                resultados.append(processo_api)
                continue

            # 3. Se não encontrou na API, tentar web scraping
            logger.info(f"Tentando web scraping para {numero}")
            try:
                scraper = await self._get_scraper()
                processo_scraped = await scraper.search_by_process_number(numero)

                if processo_scraped:
                    logger.success(f"Processo {numero} encontrado via web scraping")
                    # Marcar fonte dos dados
                    processo_scraped['fonte'] = 'Web Scraping (TJSP)'
                    # Salvar no cache
                    self.cache.set('numero_processo', {'numero': numero}, processo_scraped, 'web_scraping')
                    resultados.append(processo_scraped)
                else:
                    logger.warning(f"Processo {numero} não encontrado em nenhuma fonte")
                    resultado_nao_encontrado = {
                        'numero': numero,
                        'status': 'não_encontrado',
                        'fonte': 'nenhuma',
                        'data_consulta': datetime.now().isoformat()
                    }
                    # Cache mesmo resultados não encontrados (por menos tempo)
                    self.cache.set('numero_processo', {'numero': numero}, resultado_nao_encontrado, 'api_datajud', ttl_seconds=1800)  # 30 min
                    resultados.append(resultado_nao_encontrado)

            except Exception as e:
                logger.error(f"Erro no web scraping para {numero}: {e}")
                resultado_erro = {
                    'numero': numero,
                    'status': 'erro',
                    'erro': str(e),
                    'fonte': 'erro_web_scraping',
                    'data_consulta': datetime.now().isoformat()
                }
                # Cache erros por pouco tempo
                self.cache.set('numero_processo', {'numero': numero}, resultado_erro, 'web_scraping', ttl_seconds=300)  # 5 min
                resultados.append(resultado_erro)

        logger.info(f"Coleta concluída: {len(resultados)} processos processados")
        return resultados

    async def coletar_por_parte(self, nome_parte: str, max_resultados: int = 100) -> List[Dict[str, Any]]:
        """
        Coleta processos por nome da parte

        Estratégia:
        1. Usa API DataJud para encontrar processos rapidamente
        2. Opcionalmente, complementa com web scraping para mais detalhes

        Args:
            nome_parte: Nome da parte
            max_resultados: Máximo de resultados

        Returns:
            Lista de processos encontrados
        """
        logger.info(f"Buscando processos de '{nome_parte}' via abordagem híbrida")

        # 1. Verificar cache primeiro
        cached_results = self.cache.get('nome_parte', {'nome_parte': nome_parte, 'max_resultados': max_resultados})
        if cached_results:
            logger.success(f"Resultados para '{nome_parte}' encontrados no cache ({len(cached_results)} processos)")
            return cached_results

        # 2. Buscar via API DataJud (mais eficiente para descoberta)
        processos_api = self.api.consultar_por_parte(nome_parte, max_resultados)

        if not processos_api:
            logger.info(f"Nenhum processo encontrado para '{nome_parte}'")
            # Cache mesmo resultados vazios (por menos tempo)
            self.cache.set('nome_parte', {'nome_parte': nome_parte, 'max_resultados': max_resultados}, [], 'api_datajud', ttl_seconds=1800)  # 30 min
            return []

        logger.success(f"Encontrados {len(processos_api)} processos via API DataJud")

        # Salvar no cache
        self.cache.set('nome_parte', {'nome_parte': nome_parte, 'max_resultados': max_resultados}, processos_api, 'api_datajud')

        # 2. Opcional: Para os primeiros processos, tentar obter mais detalhes via scraping
        # (desabilitado por padrão para não sobrecarregar)
        if self.config.DEBUG_MODE and len(processos_api) <= 5:
            logger.info("Modo debug: tentando enriquecer dados com web scraping")
            for processo in processos_api[:3]:  # Apenas os primeiros 3
                try:
                    numero = processo.get('numero')
                    if numero:
                        scraper = await self._get_scraper()
                        detalhes_scraped = await scraper.search_by_process_number(str(numero))

                        if detalhes_scraped:
                            # Mesclar dados da API com dados do scraping
                            processo['dados_scraping'] = detalhes_scraped
                            logger.debug(f"Detalhes adicionais obtidos para {numero}")

                except Exception as e:
                    logger.debug(f"Não foi possível obter detalhes extras para {numero}: {e}")

        return processos_api

    async def gerar_relatorio_comparativo(self, nome_parte: str = "João Silva") -> Dict[str, Any]:
        """
        Gera relatório comparativo entre API e web scraping

        Args:
            nome_parte: Nome para teste de busca

        Returns:
            Relatório comparativo
        """
        logger.info("Gerando relatório comparativo entre métodos")

        # Verificar cache primeiro
        cached_report = self.cache.get('relatorio', {'tipo': 'comparativo', 'nome_parte': nome_parte})
        if cached_report:
            logger.success("Relatório comparativo encontrado no cache")
            return cached_report

        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'teste_nome_parte': nome_parte,
            'comparacao': {}
        }

        # Teste 1: Busca por parte
        logger.info("Testando busca por parte...")

        # Via API
        inicio_api = datetime.now()
        resultados_api = self.api.consultar_por_parte(nome_parte, 10)
        tempo_api = (datetime.now() - inicio_api).total_seconds()

        # Via web scraping
        try:
            inicio_scraping = datetime.now()
            scraper = await self._get_scraper()
            resultados_scraping = await scraper.search_by_party(nome_parte, 1)  # Apenas 1 página
            tempo_scraping = (datetime.now() - inicio_scraping).total_seconds()
        except Exception as e:
            resultados_scraping = []
            tempo_scraping = -1
            logger.error(f"Erro no web scraping: {e}")

        relatorio['comparacao'] = {
            'api_datajud': {
                'resultados': len(resultados_api),
                'tempo_segundos': round(tempo_api, 2),
                'status': 'sucesso' if resultados_api else 'sem_resultados'
            },
            'web_scraping': {
                'resultados': len(resultados_scraping),
                'tempo_segundos': round(tempo_scraping, 2) if tempo_scraping > 0 else None,
                'status': 'sucesso' if resultados_scraping else 'erro'
            }
        }

        # Estatísticas dos tribunais
        logger.info("Obtendo estatísticas dos tribunais...")
        tribunais = ['tjsp', 'tjrj', 'trf3']
        relatorio['estatisticas_tribunais'] = {}

        for tribunal in tribunais:
            api_temp = DataJudAPI(tribunal)
            stats = api_temp.obter_estatisticas_tribunal()
            relatorio['estatisticas_tribunais'][tribunal] = stats

        # Salvar relatório no cache
        self.cache.set('relatorio', {'tipo': 'comparativo', 'nome_parte': nome_parte}, relatorio, 'api_datajud')

        return relatorio

    async def salvar_resultados(self, resultados: List[Dict], nome_arquivo: Optional[str] = None) -> str:
        """
        Salva resultados da coleta híbrida

        Args:
            resultados: Resultados a salvar
            nome_arquivo: Nome do arquivo (opcional)

        Returns:
            Caminho do arquivo salvo
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f'coleta_hibrida_{timestamp}'

        # Estrutura de dados para exportação
        dados_exportacao = {
            'metadata': {
                'tipo_coleta': 'hibrida',
                'fonte_api': 'DataJud (CNJ)',
                'fonte_scraping': 'TJSP Web',
                'data_coleta': datetime.now().isoformat(),
                'total_processos': len(resultados)
            },
            'resultados': resultados
        }

        # Usar método da API DataJud para salvar
        caminho_json = self.api.salvar_resultados(resultados, nome_arquivo)
        return caminho_json

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.scraper:
            await self.scraper.__aexit__(exc_type, exc_val, exc_tb)