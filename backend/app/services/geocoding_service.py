"""
Serviço de geocodificação
Integra com Nominatim (OpenStreetMap) para converter endereços em coordenadas
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


class GeocodingService:
    """Serviço para geocodificação de endereços via Nominatim"""

    def __init__(self):
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.timeout = httpx.Timeout(10.0)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 1000

        # Rate limiting: 1 request per second (Nominatim limit)
        self.rate_limiter = asyncio.Semaphore(1)
        self.last_request_time = 0
        self.min_interval = 1.0  # 1 segundo entre requests

        # User-Agent obrigatório pelo Nominatim
        self.headers = {
            "User-Agent": "ProTeamCare/1.0 (contato@proteamcare.com)"
        }

    async def geocode_address(self, address: str, city: str = "", state: str = "") -> Optional[Dict[str, Any]]:
        """
        Geocodifica um endereço para coordenadas lat/lng

        Args:
            address: Endereço completo
            city: Cidade (opcional, para melhorar precisão)
            state: Estado (opcional, para melhorar precisão)

        Returns:
            Dict com lat, lng e dados adicionais ou None se não encontrado
        """
        if not address:
            logger.warning("Endereço vazio fornecido")
            return None

        # Construir query otimizada
        query_parts = [address]
        if city:
            query_parts.append(city)
        if state:
            query_parts.append(state)

        query = ", ".join(query_parts)
        cache_key = f"geocode_{query.lower().replace(' ', '_')}"

        # Verificar cache
        if cache_key in self.cache:
            logger.info(f"Usando cache geocoding para: {query}")
            return self.cache[cache_key]

        # Rate limiting
        await self._rate_limit()

        try:
            logger.info(f"Geocodificando endereço: {query}")

            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                params = {
                    "q": query,
                    "format": "json",
                    "limit": 1,  # Apenas o melhor resultado
                    "countrycodes": "br",  # Limitar ao Brasil
                    "addressdetails": 1,
                    "extratags": 1
                }

                url = f"{self.nominatim_base_url}/search"
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data:
                    logger.warning(f"Nenhum resultado de geocoding para: {query}")
                    return None

                # Pegar primeiro resultado
                result = data[0]

                # Validar que tem coordenadas
                if not result.get("lat") or not result.get("lon"):
                    logger.warning(f"Resultado geocoding sem coordenadas para: {query}")
                    return None

                # Enriquecer dados
                enriched_data = self._enrich_geocoding_data(result, query)

                # Cachear resultado
                self._cache_result(cache_key, enriched_data)

                logger.info(f"Geocoding bem-sucedido para '{query}': {result.get('lat')}, {result.get('lon')}")
                return enriched_data

        except httpx.TimeoutException:
            logger.error(f"Timeout no geocoding para: {query}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP no geocoding para {query}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no geocoding para {query}: {str(e)}")
            return None

    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocoding: coordenadas para endereço

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Dict com dados do endereço ou None
        """
        cache_key = f"reverse_{lat:.6f}_{lng:.6f}"

        # Verificar cache
        if cache_key in self.cache:
            logger.info(f"Usando cache reverse geocoding para: {lat}, {lng}")
            return self.cache[cache_key]

        # Rate limiting
        await self._rate_limit()

        try:
            logger.info(f"Reverse geocoding para: {lat}, {lng}")

            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                params = {
                    "lat": lat,
                    "lon": lng,
                    "format": "json",
                    "addressdetails": 1,
                    "extratags": 1
                }

                url = f"{self.nominatim_base_url}/reverse"
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data or data.get("error"):
                    logger.warning(f"Nenhum resultado reverse geocoding para: {lat}, {lng}")
                    return None

                # Enriquecer dados
                enriched_data = self._enrich_reverse_geocoding_data(data)

                # Cachear resultado
                self._cache_result(cache_key, enriched_data)

                logger.info(f"Reverse geocoding bem-sucedido: {data.get('display_name')}")
                return enriched_data

        except httpx.TimeoutException:
            logger.error(f"Timeout no reverse geocoding para: {lat}, {lng}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP no reverse geocoding para {lat}, {lng}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no reverse geocoding para {lat}, {lng}: {str(e)}")
            return None

    async def _rate_limit(self) -> None:
        """Implementa rate limiting para respeitar limites do Nominatim"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: aguardando {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()

    def _enrich_geocoding_data(self, data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """
        Enriquece dados de geocoding

        Args:
            data: Dados brutos do Nominatim
            original_query: Query original

        Returns:
            Dados enriquecidos
        """
        enriched = {
            "latitude": float(data["lat"]),
            "longitude": float(data["lon"]),
            "display_name": data.get("display_name", ""),
            "type": data.get("type", ""),
            "importance": data.get("importance", 0),
            "address": data.get("address", {}),
            "boundingbox": data.get("boundingbox", []),
            "original_query": original_query
        }

        # Adicionar metadados
        enriched["_metadata"] = {
            "source": "nominatim",
            "enriched_at": "2025-10-28T11:30:00Z",
            "version": "1.0"
        }

        return enriched

    def _enrich_reverse_geocoding_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece dados de reverse geocoding

        Args:
            data: Dados brutos do Nominatim

        Returns:
            Dados enriquecidos
        """
        enriched = {
            "latitude": float(data["lat"]),
            "longitude": float(data["lon"]),
            "display_name": data.get("display_name", ""),
            "type": data.get("type", ""),
            "importance": data.get("importance", 0),
            "address": data.get("address", {}),
            "boundingbox": data.get("boundingbox", []),
        }

        # Adicionar metadados
        enriched["_metadata"] = {
            "source": "nominatim_reverse",
            "enriched_at": "2025-10-28T11:30:00Z",
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
            logger.info(f"Cache geocoding rotacionado, removida chave: {oldest_key}")

        self.cache[key] = data
        logger.debug(f"Resultado geocoding cacheado: {key}")

    def clear_cache(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        logger.info("Cache geocoding limpo")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "total_entries": len(self.cache),
            "max_size": self.max_cache_size,
            "usage_percent": (len(self.cache) / self.max_cache_size) * 100
        }


# Instância global do serviço
geocoding_service = GeocodingService()