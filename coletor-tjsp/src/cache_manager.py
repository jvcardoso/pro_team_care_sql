"""
Sistema de Cache para otimizar performance das consultas
Implementa cache inteligente com TTL e invalidação automática
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import pickle
from loguru import logger

from .config import Config


@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    key: str
    data: Any
    timestamp: datetime
    ttl_seconds: int
    source: str  # 'api_datajud' ou 'web_scraping'
    query_type: str  # 'numero_processo', 'nome_parte', etc.
    query_params: Dict[str, Any]

    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (para JSON)"""
        return {
            'key': self.key,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'ttl_seconds': self.ttl_seconds,
            'source': self.source,
            'query_type': self.query_type,
            'query_params': self.query_params
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Cria instância a partir de dicionário"""
        return cls(
            key=data['key'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            ttl_seconds=data['ttl_seconds'],
            source=data['source'],
            query_type=data['query_type'],
            query_params=data['query_params']
        )


class CacheManager:
    """
    Gerenciador de cache inteligente para consultas de processos

    Recursos:
    - Cache em memória e disco
    - TTL configurável por tipo de consulta
    - Invalidação automática
    - Estatísticas de performance
    - Compressão de dados grandes
    """

    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = config.CACHE_DIR / 'queries'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache em memória para consultas frequentes
        self.memory_cache: Dict[str, CacheEntry] = {}

        # Estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'expired': 0,
            'saved': 0
        }

        # TTL padrão por tipo de consulta (em segundos)
        self.default_ttl = {
            'numero_processo': 3600 * 24 * 7,  # 7 dias
            'nome_parte': 3600 * 24 * 1,       # 1 dia
            'estatisticas': 3600 * 6,          # 6 horas
            'relatorio': 3600 * 24 * 30        # 30 dias
        }

        # Carregar cache do disco na inicialização
        self._load_cache_from_disk()

        logger.info(f"Cache inicializado: {len(self.memory_cache)} entradas carregadas")

    def _generate_key(self, query_type: str, params: Dict[str, Any]) -> str:
        """Gera chave única para a consulta"""
        # Ordena os parâmetros para consistência
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        content = f"{query_type}:{sorted_params}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cache_file(self, key: str) -> Path:
        """Retorna caminho do arquivo de cache"""
        return self.cache_dir / f"{key}.cache"

    def _save_to_disk(self, entry: CacheEntry):
        """Salva entrada no disco"""
        try:
            cache_file = self._get_cache_file(entry.key)
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            logger.warning(f"Erro ao salvar cache no disco: {e}")

    def _load_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Carrega entrada do disco"""
        try:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                    # Verifica se ainda é válido
                    if not entry.is_expired():
                        return entry
                    else:
                        # Remove arquivo expirado
                        cache_file.unlink()
        except Exception as e:
            logger.debug(f"Erro ao carregar cache do disco: {e}")
        return None

    def _load_cache_from_disk(self):
        """Carrega entradas recentes do disco para memória"""
        try:
            # Carrega apenas arquivos recentes (últimas 24h)
            cutoff_time = datetime.now() - timedelta(hours=24)

            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    # Verifica data de modificação do arquivo
                    if cache_file.stat().st_mtime > cutoff_time.timestamp():
                        with open(cache_file, 'rb') as f:
                            entry = pickle.load(f)
                            if not entry.is_expired():
                                self.memory_cache[entry.key] = entry
                except Exception as e:
                    logger.debug(f"Erro ao carregar {cache_file}: {e}")
                    # Remove arquivo corrompido
                    try:
                        cache_file.unlink()
                    except:
                        pass

        except Exception as e:
            logger.warning(f"Erro ao carregar cache do disco: {e}")

    def get(self, query_type: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Busca dados no cache

        Args:
            query_type: Tipo da consulta
            params: Parâmetros da consulta

        Returns:
            Dados cached ou None se não encontrado/expirado
        """
        key = self._generate_key(query_type, params)

        # Primeiro tenta cache em memória
        entry = self.memory_cache.get(key)
        if entry:
            if not entry.is_expired():
                self.stats['hits'] += 1
                logger.debug(f"Cache HIT (memória): {query_type}")
                return entry.data
            else:
                # Remove entrada expirada
                del self.memory_cache[key]
                self.stats['expired'] += 1

        # Tenta cache em disco
        entry = self._load_from_disk(key)
        if entry:
            # Coloca de volta na memória
            self.memory_cache[key] = entry
            self.stats['hits'] += 1
            logger.debug(f"Cache HIT (disco): {query_type}")
            return entry.data

        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {query_type}")
        return None

    def set(self, query_type: str, params: Dict[str, Any], data: Any,
            source: str, ttl_seconds: Optional[int] = None):
        """
        Armazena dados no cache

        Args:
            query_type: Tipo da consulta
            params: Parâmetros da consulta
            data: Dados a armazenar
            source: Fonte dos dados ('api_datajud' ou 'web_scraping')
            ttl_seconds: TTL em segundos (usa padrão se None)
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl.get(query_type, 3600)  # 1 hora padrão

        key = self._generate_key(query_type, params)

        entry = CacheEntry(
            key=key,
            data=data,
            timestamp=datetime.now(),
            ttl_seconds=ttl_seconds,
            source=source,
            query_type=query_type,
            query_params=params
        )

        # Salva em memória
        self.memory_cache[key] = entry

        # Salva em disco (apenas se não for muito grande)
        if len(pickle.dumps(data)) < 1024 * 1024:  # Menos de 1MB
            self._save_to_disk(entry)

        self.stats['saved'] += 1
        logger.debug(f"Cache SET: {query_type} ({source}) - TTL: {ttl_seconds}s")

    def invalidate(self, query_type: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        """
        Invalida entradas do cache

        Args:
            query_type: Tipo específico para invalidar (None = todos)
            params: Parâmetros específicos (None = todos do tipo)
        """
        if query_type and params:
            # Invalida entrada específica
            key = self._generate_key(query_type, params)
            if key in self.memory_cache:
                del self.memory_cache[key]
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
            logger.info(f"Cache invalidado: {query_type} com params {params}")
        elif query_type:
            # Invalida todas as entradas do tipo
            keys_to_remove = [k for k, v in self.memory_cache.items() if v.query_type == query_type]
            for key in keys_to_remove:
                del self.memory_cache[key]
            # Remove arquivos do disco
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, 'rb') as f:
                        entry = pickle.load(f)
                        if entry.query_type == query_type:
                            cache_file.unlink()
                except:
                    pass
            logger.info(f"Cache invalidado: todas as entradas do tipo {query_type}")
        else:
            # Invalida todo o cache
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info("Cache completamente invalidado")

    def cleanup_expired(self):
        """Remove entradas expiradas do cache"""
        expired_keys = []
        for key, entry in self.memory_cache.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            del self.memory_cache[key]

        # Remove arquivos expirados do disco
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                    if entry.is_expired():
                        cache_file.unlink()
            except:
                pass

        if expired_keys:
            logger.info(f"Cache cleanup: {len(expired_keys)} entradas expiradas removidas")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_entries = len(self.memory_cache)
        total_size = sum(len(pickle.dumps(entry.data)) for entry in self.memory_cache.values())

        return {
            'entries_in_memory': total_entries,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'expired': self.stats['expired'],
            'saved': self.stats['saved'],
            'hit_rate': round(self.stats['hits'] / max(self.stats['hits'] + self.stats['misses'], 1) * 100, 1),
            'cache_dir': str(self.cache_dir)
        }

    def export_stats(self) -> str:
        """Exporta estatísticas para arquivo JSON"""
        stats = self.get_stats()
        stats['timestamp'] = datetime.now().isoformat()

        stats_file = self.cache_dir.parent / 'cache_stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        logger.info(f"Estatísticas do cache exportadas: {stats_file}")
        return str(stats_file)