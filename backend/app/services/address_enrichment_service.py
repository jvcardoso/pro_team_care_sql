"""
Serviço de enriquecimento de endereços
Integra com ViaCEP para enriquecer endereços automaticamente
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class AddressEnrichmentService:
    """Serviço para enriquecimento automático de endereços via ViaCEP"""

    def __init__(self):
        self.viacep_base_url = "https://viacep.com.br/ws"
        self.timeout = httpx.Timeout(10.0)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 1000  # Limitar tamanho do cache

        # Mapeamento UF para código IBGE do estado
        self.ibge_state_codes = {
            "AC": 12, "AL": 27, "AP": 16, "AM": 13, "BA": 29,
            "CE": 23, "DF": 53, "ES": 32, "GO": 52, "MA": 21,
            "MT": 51, "MS": 50, "MG": 31, "PA": 15, "PB": 25,
            "PR": 41, "PE": 26, "PI": 22, "RJ": 33, "RN": 24,
            "RS": 43, "RO": 11, "RR": 14, "SC": 42, "SP": 35,
            "SE": 28, "TO": 17,
        }

    async def consult_viacep(self, cep: str) -> Optional[Dict[str, Any]]:
        """
        Consulta ViaCEP para obter dados do CEP

        Args:
            cep: CEP com ou sem formatação (8 dígitos)

        Returns:
            Dict com dados do endereço ou None se não encontrado/inválido
        """
        if not cep:
            logger.warning("CEP vazio fornecido")
            return None

        # Limpar formatação
        clean_cep = ''.join(filter(str.isdigit, cep))

        # Validar formato
        if len(clean_cep) != 8:
            logger.warning(f"CEP com formato inválido: {cep} -> {clean_cep}")
            return None

        cache_key = f"viacep_{clean_cep}"

        # Verificar cache
        if cache_key in self.cache:
            logger.info(f"Usando cache ViaCEP para CEP: {clean_cep}")
            return self.cache[cache_key]

        try:
            logger.info(f"Consultando ViaCEP para CEP: {clean_cep}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.viacep_base_url}/{clean_cep}/json/"
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()

                # Verificar se CEP foi encontrado
                if data.get("erro"):
                    logger.warning(f"CEP não encontrado no ViaCEP: {clean_cep}")
                    return None

                # Validar resposta básica
                if not data.get("cep"):
                    logger.warning(f"Resposta ViaCEP inválida para CEP {clean_cep}: {data}")
                    return None

                # Enriquecer dados com informações adicionais
                enriched_data = self._enrich_viacep_data(data)

                # Cachear resultado
                self._cache_result(cache_key, enriched_data)

                logger.info(f"ViaCEP consulta bem-sucedida para CEP {clean_cep}: {data.get('logradouro')}")
                return enriched_data

        except httpx.TimeoutException:
            logger.error(f"Timeout na consulta ViaCEP para CEP: {clean_cep}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP na consulta ViaCEP para CEP {clean_cep}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na consulta ViaCEP para CEP {clean_cep}: {str(e)}")
            return None

    def _enrich_viacep_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece dados do ViaCEP com informações adicionais

        Args:
            data: Dados brutos do ViaCEP

        Returns:
            Dados enriquecidos
        """
        enriched = data.copy()

        # Adicionar código IBGE do estado
        uf = data.get("uf")
        if uf and uf in self.ibge_state_codes:
            enriched["ibge_state_code"] = self.ibge_state_codes[uf]

        # Adicionar metadados
        enriched["_metadata"] = {
            "source": "viacep",
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
            logger.info(f"Cache ViaCEP rotacionado, removida chave: {oldest_key}")

        self.cache[key] = data
        logger.debug(f"Resultado cacheado: {key}")

    def clear_cache(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        logger.info("Cache ViaCEP limpo")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "total_entries": len(self.cache),
            "max_size": self.max_cache_size,
            "usage_percent": (len(self.cache) / self.max_cache_size) * 100
        }


# Instância global do serviço
address_enrichment_service = AddressEnrichmentService()