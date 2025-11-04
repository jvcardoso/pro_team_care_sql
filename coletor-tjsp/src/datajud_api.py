"""
Módulo de integração com API DataJud (CNJ)
Abordagem oficial e legal para consulta de processos jurídicos
"""
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Config


class DataJudAPI:
    """
    Cliente para API Pública do DataJud (CNJ)

    Esta é a abordagem RECOMENDADA para consulta de processos jurídicos:
    - 100% legal e oficial
    - Não requer ser advogado
    - Acesso gratuito e público
    - Sem CAPTCHA ou bloqueios
    """

    # Chave pública oficial do CNJ
    API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
    BASE_URL = "https://api-publica.datajud.cnj.jus.br"

    def __init__(self, tribunal: str = 'tjsp'):
        """
        Inicializa cliente da API

        Args:
            tribunal: Sigla do tribunal (tjsp, tjrj, trf3, etc.)
        """
        self.tribunal = tribunal
        self.endpoint = f"{self.BASE_URL}/api_publica_{tribunal}/_search"
        self.headers = {
            'Authorization': f'APIKey {self.API_KEY}',
            'Content-Type': 'application/json'
        }
        self.config = Config()

    def _limpar_numero_processo(self, numero: str) -> str:
        """Remove formatação do número do processo para busca"""
        return numero.replace('-', '').replace('.', '').replace(' ', '')

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def consultar_por_numero(self, numero_processo: str) -> Optional[Dict[str, Any]]:
        """
        Consulta processo por número CNJ

        Args:
            numero_processo: Número do processo (ex: '1000032-02.2024.8.26.0100')

        Returns:
            Dados do processo ou None se não encontrado
        """
        numero_limpo = self._limpar_numero_processo(numero_processo)

        query = {
            "query": {
                "match": {
                    "numeroProcesso": numero_limpo
                }
            },
            "size": 1  # Apenas o primeiro resultado
        }

        try:
            logger.info(f"Consultando processo {numero_processo} via API DataJud")

            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=query,
                timeout=30
            )

            if response.status_code == 200:
                dados = response.json()
                hits = dados.get('hits', {}).get('hits', [])

                if hits:
                    processo = self._processar_resultado(hits[0]['_source'])
                    logger.success(f"Processo {numero_processo} encontrado via API")
                    return processo
                else:
                    logger.warning(f"Processo {numero_processo} não encontrado na API DataJud")
                    return None
            else:
                logger.error(f"Erro HTTP {response.status_code} na API DataJud: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição API DataJud: {e}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def consultar_por_parte(self, nome_parte: str, max_resultados: int = 50) -> List[Dict[str, Any]]:
        """
        Busca processos por nome da parte

        Args:
            nome_parte: Nome da parte (pessoa física ou jurídica)
            max_resultados: Número máximo de resultados (padrão: 50)

        Returns:
            Lista de processos encontrados
        """
        # Limitar max_resultados ao limite da API
        max_resultados = min(max_resultados, 1000)

        query = {
            "query": {
                "match": {
                    "nome": nome_parte
                }
            },
            "size": max_resultados,
            "sort": [
                {"dataAjuizamento": {"order": "desc"}}  # Mais recentes primeiro
            ]
        }

        try:
            logger.info(f"Buscando processos de '{nome_parte}' via API DataJud")

            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=query,
                timeout=30
            )

            if response.status_code == 200:
                dados = response.json()
                hits = dados.get('hits', {}).get('hits', [])

                if hits:
                    processos = [self._processar_resultado(hit['_source']) for hit in hits]
                    logger.success(f"Encontrados {len(processos)} processos para '{nome_parte}'")
                    return processos
                else:
                    logger.info(f"Nenhum processo encontrado para '{nome_parte}'")
                    return []
            else:
                logger.error(f"Erro HTTP {response.status_code} na busca por parte")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição de busca por parte: {e}")
            return []

    def _processar_resultado(self, processo: Dict[str, Any]) -> Dict[str, Any]:
        """Processa e estrutura dados do processo da API"""
        # Extrair assuntos
        assuntos = []
        if processo.get('assunto'):
            assuntos = [assunto.get('nome', '') for assunto in processo['assunto'] if assunto.get('nome')]

        # Extrair movimentações básicas (resumo)
        movimentacoes = []
        if processo.get('movimentos'):
            for mov in processo['movimentos'][:10]:  # Limitar às 10 mais recentes
                movimentacao = {
                    'data': mov.get('dataHora'),
                    'tipo': mov.get('tipo', {}).get('nome', ''),
                    'complemento': mov.get('complemento')
                }
                movimentacoes.append(movimentacao)

        return {
            'numero': processo.get('numeroProcesso'),
            'numero_formatado': self._formatar_numero_processo(processo.get('numeroProcesso', '')),
            'classe': processo.get('classe', {}).get('nome'),
            'assuntos': assuntos,
            'assunto_principal': assuntos[0] if assuntos else None,
            'orgao_julgador': processo.get('orgaoJulgador', {}).get('nome'),
            'comarca': processo.get('comarca', {}).get('nome'),
            'data_ajuizamento': processo.get('dataAjuizamento'),
            'data_ultima_atualizacao': processo.get('dataHoraUltimaAtualizacao'),
            'sistema': processo.get('sistema', {}).get('nome'),
            'grau': processo.get('grau'),
            'tribunal': processo.get('siglaTribunal'),
            'status': processo.get('status'),
            'valor_causa': processo.get('valorCausa'),
            'quantidade_movimentacoes': len(processo.get('movimentos', [])),
            'movimentacoes_recentes': movimentacoes,
            'fonte': 'API DataJud (CNJ)',
            'data_consulta': datetime.now().isoformat(),
            'dados_completos': processo
        }

    def _formatar_numero_processo(self, numero: str) -> str:
        """Formata número do processo no padrão CNJ"""
        if not numero or len(numero) < 20:
            return numero

        # Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
        try:
            return f"{numero[:7]}-{numero[7:9]}.{numero[9:13]}.{numero[13:14]}.{numero[14:16]}.{numero[16:20]}"
        except:
            return numero

    def salvar_resultados(self, processos: List[Dict], nome_base: Optional[str] = None) -> str:
        """
        Salva resultados em arquivo JSON

        Args:
            processos: Lista de processos
            nome_base: Nome base para o arquivo

        Returns:
            Caminho do arquivo salvo
        """
        if not nome_base:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_base = f'datajud_{self.tribunal}_{timestamp}'

        # Salvar dados estruturados
        dados_estruturados = {
            'metadata': {
                'fonte': 'API DataJud (CNJ)',
                'tribunal': self.tribunal,
                'data_consulta': datetime.now().isoformat(),
                'total_processos': len(processos)
            },
            'processos': processos
        }

        caminho_arquivo = self.config.get_output_path(f'{nome_base}.json')

        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_estruturados, f, indent=2, ensure_ascii=False)

        logger.info(f"Resultados salvos em: {caminho_arquivo}")
        return str(caminho_arquivo)

    def obter_estatisticas_tribunal(self) -> Dict[str, Any]:
        """
        Obtém estatísticas básicas do tribunal

        Returns:
            Estatísticas do tribunal
        """
        query = {
            "query": {"match_all": {}},
            "size": 0,  # Não retorna documentos, apenas contagem
            "aggs": {
                "por_classe": {
                    "terms": {"field": "classe.nome.keyword", "size": 20}
                },
                "por_ano": {
                    "date_histogram": {
                        "field": "dataAjuizamento",
                        "calendar_interval": "year"
                    }
                }
            }
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=query,
                timeout=30
            )

            if response.status_code == 200:
                dados = response.json()
                total = dados.get('hits', {}).get('total', {}).get('value', 0)

                return {
                    'tribunal': self.tribunal,
                    'total_processos': total,
                    'data_consulta': datetime.now().isoformat(),
                    'status': 'ativo'
                }
            else:
                return {
                    'tribunal': self.tribunal,
                    'status': 'erro',
                    'erro': f'HTTP {response.status_code}'
                }

        except Exception as e:
            return {
                'tribunal': self.tribunal,
                'status': 'erro',
                'erro': str(e)
            }