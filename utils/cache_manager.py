#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestion du cache pour SuperSmartMatch
"""

import json
import logging
import time
from typing import Any, Optional, Dict

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestionnaire de cache pour SuperSmartMatch
    Supporte Redis et un cache en mémoire de fallback
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.memory_cache = {}  # Cache de fallback en mémoire
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
        
        # Initialisation de Redis si disponible
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test de connexion
                self.redis_client.ping()
                logger.info("Cache Redis initialisé avec succès")
            except Exception as e:
                logger.warning(f"Impossible de se connecter à Redis: {e}. Utilisation du cache mémoire.")
                self.redis_client = None
        else:
            if not REDIS_AVAILABLE:
                logger.info("Redis non disponible. Utilisation du cache mémoire.")
            else:
                logger.info("Pas d'URL Redis fournie. Utilisation du cache mémoire.")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur mise en cache ou None si non trouvée
        """
        try:
            # Tentative avec Redis d'abord
            if self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    self.cache_stats['hits'] += 1
                    return json.loads(cached_data)
            
            # Fallback sur le cache mémoire
            if key in self.memory_cache:
                cache_entry = self.memory_cache[key]
                
                # Vérification de l'expiration
                if cache_entry['expires_at'] > time.time():
                    self.cache_stats['hits'] += 1
                    return cache_entry['data']
                else:
                    # Suppression de l'entrée expirée
                    del self.memory_cache[key]
            
            # Cache miss
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache: {e}")
            self.cache_stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Stocke une valeur dans le cache
        
        Args:
            key: Clé de cache
            value: Valeur à mettre en cache
            ttl: Durée de vie en secondes
            
        Returns:
            True si le stockage a réussi
        """
        try:
            serialized_value = json.dumps(value, default=str)
            
            # Stockage dans Redis si disponible
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized_value)
            
            # Stockage dans le cache mémoire
            self.memory_cache[key] = {
                'data': value,
                'expires_at': time.time() + ttl
            }
            
            # Nettoyage périodique du cache mémoire
            if len(self.memory_cache) > 1000:
                self._cleanup_memory_cache()
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du cache: {e}")
            self.cache_stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si la suppression a réussi
        """
        try:
            # Suppression de Redis
            if self.redis_client:
                self.redis_client.delete(key)
            
            # Suppression du cache mémoire
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")
            self.cache_stats['errors'] += 1
            return False
    
    def clear(self) -> bool:
        """
        Vide complètement le cache
        
        Returns:
            True si le nettoyage a réussi
        """
        try:
            # Nettoyage de Redis
            if self.redis_client:
                self.redis_client.flushdb()
            
            # Nettoyage du cache mémoire
            self.memory_cache.clear()
            
            logger.info("Cache vidé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du cache: {e}")
            self.cache_stats['errors'] += 1
            return False
    
    def get_hit_rate(self) -> float:
        """
        Calcule le taux de cache hit
        
        Returns:
            Taux de cache hit entre 0 et 1
        """
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests == 0:
            return 0.0
        
        return self.cache_stats['hits'] / total_requests
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques du cache
        
        Returns:
            Dictionnaire avec les statistiques du cache
        """
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.get_hit_rate()
        
        metrics = {
            'backend': 'redis' if self.redis_client else 'memory',
            'total_requests': total_requests,
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate': round(hit_rate, 3),
            'hit_rate_percent': round(hit_rate * 100, 1),
            'sets': self.cache_stats['sets'],
            'errors': self.cache_stats['errors'],
            'memory_cache_size': len(self.memory_cache)
        }
        
        # Métriques Redis supplémentaires si disponible
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                metrics['redis_info'] = {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory_human': redis_info.get('used_memory_human', 'N/A'),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0)
                }
            except Exception as e:
                logger.warning(f"Impossible de récupérer les infos Redis: {e}")
        
        return metrics
    
    def _cleanup_memory_cache(self) -> None:
        """
        Nettoie le cache mémoire des entrées expirées
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry['expires_at'] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        logger.debug(f"Nettoyage du cache mémoire: {len(expired_keys)} entrées expirées supprimées")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du cache
        
        Returns:
            Dictionnaire avec l'état de santé
        """
        health = {
            'status': 'healthy',
            'backend': 'memory',
            'redis_available': False,
            'memory_cache_functional': True
        }
        
        # Test de Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                health['redis_available'] = True
                health['backend'] = 'redis'
            except Exception as e:
                health['redis_available'] = False
                health['redis_error'] = str(e)
                health['status'] = 'degraded'
        
        # Test du cache mémoire
        try:
            test_key = f"health_check_{int(time.time())}"
            test_value = {'test': True}
            
            # Test set/get
            self.set(test_key, test_value, ttl=10)
            retrieved_value = self.get(test_key)
            
            if retrieved_value != test_value:
                health['memory_cache_functional'] = False
                health['status'] = 'unhealthy'
            
            # Nettoyage
            self.delete(test_key)
            
        except Exception as e:
            health['memory_cache_functional'] = False
            health['memory_cache_error'] = str(e)
            health['status'] = 'unhealthy'
        
        return health
    
    def reset_stats(self) -> None:
        """
        Remet à zéro les statistiques du cache
        """
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
        logger.info("Statistiques du cache remises à zéro")
