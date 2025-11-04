"""
Serviço de consulta CNPJ
Integra com ReceitaWS para obter dados de empresas
"""

import asyncio
import logging
import re
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class CNPJService:
    """Serviço para consulta de dados via ReceitaWS"""

    def __init__(self):
        self.receitaws_base_url = "https://www.receitaws.com.br/v1/cnpj"
        self.timeout = httpx.Timeout(15.0)  # ReceitaWS pode ser mais lento
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 500  # Menor cache pois dados são maiores

        # Mapeamento de códigos de atividade econômica
        self.activity_codes = {
            "01": "Agricultura, pecuária, produção florestal, pesca e aquicultura",
            "02": "Indústrias extrativas",
            "03": "Indústrias de transformação",
            "05": "Eletricidade e gás",
            "06": "Água, esgoto, atividades de gestão de resíduos e descontaminação",
            "07": "Construção",
            "08": "Comércio; reparação de veículos automotores e motocicletas",
            "09": "Transporte, armazenagem e correio",
            "10": "Alojamento e alimentação",
            "11": "Informação e comunicação",
            "12": "Atividades financeiras, de seguros e serviços relacionados",
            "13": "Atividades imobiliárias",
            "14": "Atividades profissionais, científicas e técnicas",
            "15": "Atividades administrativas e serviços complementares",
            "16": "Administração pública, defesa e seguridade social",
            "17": "Educação",
            "18": "Saúde humana e serviços sociais",
            "19": "Artes, cultura, esporte e recreação",
            "20": "Outras atividades de serviços",
            "21": "Serviços domésticos",
            "22": "Organismos internacionais e outras instituições extraterritoriais",
        }

    async def consult_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Consulta ReceitaWS para obter dados da empresa

        Args:
            cnpj: CNPJ com ou sem formatação (14 dígitos)

        Returns:
            Dict com dados da empresa ou None se não encontrado/inválido
        """
        if not cnpj:
            logger.warning("CNPJ vazio fornecido")
            return None

        # Limpar formatação
        clean_cnpj = re.sub(r'\D', '', cnpj)

        # Validar formato
        if len(clean_cnpj) != 14:
            logger.warning(f"CNPJ com formato inválido: {cnpj} -> {clean_cnpj}")
            return None

        # Validar dígitos verificadores
        if not self._validate_cnpj_digits(clean_cnpj):
            logger.warning(f"CNPJ com dígitos inválidos: {clean_cnpj}")
            return None

        cache_key = f"cnpj_{clean_cnpj}"

        # Verificar cache
        if cache_key in self.cache:
            logger.info(f"Usando cache ReceitaWS para CNPJ: {clean_cnpj}")
            return self.cache[cache_key]

        try:
            logger.info(f"Consultando ReceitaWS para CNPJ: {clean_cnpj}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.receitaws_base_url}/{clean_cnpj}"
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()

                # Verificar se CNPJ foi encontrado
                if data.get("status") == "ERROR":
                    logger.warning(f"CNPJ não encontrado no ReceitaWS: {clean_cnpj} - {data.get('message')}")
                    return None

                # Validar resposta básica
                if not data.get("cnpj"):
                    logger.warning(f"Resposta ReceitaWS inválida para CNPJ {clean_cnpj}: {data}")
                    return None

                # Enriquecer dados com informações adicionais
                enriched_data = self._enrich_cnpj_data(data)

                # Cachear resultado
                self._cache_result(cache_key, enriched_data)

                logger.info(f"ReceitaWS consulta bem-sucedida para CNPJ {clean_cnpj}: {data.get('nome')}")
                return enriched_data

        except httpx.TimeoutException:
            logger.error(f"Timeout na consulta ReceitaWS para CNPJ: {clean_cnpj}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP na consulta ReceitaWS para CNPJ {clean_cnpj}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na consulta ReceitaWS para CNPJ {clean_cnpj}: {str(e)}")
            return None

    def _validate_cnpj_digits(self, cnpj: str) -> bool:
        """
        Valida os dígitos verificadores do CNPJ

        Args:
            cnpj: CNPJ limpo (14 dígitos)

        Returns:
            True se válido
        """
        # Implementação do algoritmo de validação CNPJ
        # Primeiro dígito verificador
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum1 = sum(int(cnpj[i]) * weights1[i] for i in range(12))
        digit1 = 11 - (sum1 % 11)
        digit1 = 0 if digit1 > 9 else digit1

        if int(cnpj[12]) != digit1:
            return False

        # Segundo dígito verificador
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum2 = sum(int(cnpj[i]) * weights2[i] for i in range(13))
        digit2 = 11 - (sum2 % 11)
        digit2 = 0 if digit2 > 9 else digit2

        return int(cnpj[13]) == digit2

    def _enrich_cnpj_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece dados do ReceitaWS com informações adicionais

        Args:
            data: Dados brutos do ReceitaWS

        Returns:
            Dados enriquecidos
        """
        enriched = data.copy()

        # Adicionar descrição da atividade principal
        if data.get("atividade_principal"):
            main_activity = data["atividade_principal"][0] if data["atividade_principal"] else {}
            code = main_activity.get("code", "")[:2]
            if code in self.activity_codes:
                enriched["atividade_principal_descricao"] = self.activity_codes[code]

        # Normalizar campos de endereço
        if data.get("logradouro"):
            enriched["endereco_completo"] = f"{data.get('logradouro', '')}, {data.get('numero', '')} - {data.get('bairro', '')}, {data.get('municipio', '')} - {data.get('uf', '')}, CEP: {data.get('cep', '')}"

        # Adicionar metadados
        enriched["_metadata"] = {
            "source": "receitaws",
            "enriched_at": "2025-10-28T11:30:00Z",  # Timestamp atual
            "version": "1.0"
        }

        return enriched

    def _cache_result(self, key: str, data: Dict[str, Any]) -> None:
        """
        Cacheia resultado da consulta

        Args:
            key: Chave do cache
            data: Dados a cachear
        """
        # Verificar limite do cache
        if len(self.cache) >= self.max_cache_size:
            # Remover entrada mais antiga (simples FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.info(f"Cache ReceitaWS rotacionado, removida chave: {oldest_key}")

        self.cache[key] = data
        logger.debug(f"Resultado cacheado: {key}")

    def clear_cache(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        logger.info("Cache ReceitaWS limpo")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "total_entries": len(self.cache),
            "max_size": self.max_cache_size,
            "usage_percent": (len(self.cache) / self.max_cache_size) * 100
        }


# Instância global do serviço
cnpj_service = CNPJService()