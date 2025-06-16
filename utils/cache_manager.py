#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Manager - Gestionnaire de cache pour SuperSmartMatch
"""

import json
import logging
import time
from typing import Any, Optional, Dict
from collections import defaultdict

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestionnaire de cache avec fallback mémoire si Redis indisponible
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
        self.cache_type = 'memory'
        
        # Tentative de connexion Redis
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test de connexion
                self.redis_client.ping()
                self.cache_type = 'redis'
                logger.info("✅ Connexion Redis établie")
            except ImportError:
                logger.warning("Redis non installé, utilisation du cache mémoire")
            except Exception as e:
                logger.warning(f"Impossible de se connecter à Redis: {e}. Utilisation du cache mémoire.")
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            if self.cache_type == 'redis' and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
                else:
                    self.cache_stats['misses'] += 1
                    return None
            else:
                # Cache mémoire
                if key in self.memory_cache:
                    cache_entry = self.memory_cache[key]
                    # Vérifier expiration
                    if cache_entry['expires_at'] > time.time():
                        self.cache_stats['hits'] += 1
                        return cache_entry['value']
                    else:
                        # Expiré
                        del self.memory_cache[key]
                        self.cache_stats['misses'] += 1
                        return None
                else:
                    self.cache_stats['misses'] += 1
                    return None
        
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache: {e}")
            self.cache_stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Stocke une valeur dans le cache"""
        try:
            if self.cache_type == 'redis' and self.redis_client:
                serialized_value = json.dumps(value, ensure_ascii=False)
                result = self.redis_client.setex(key, ttl, serialized_value)
                if result:
                    self.cache_stats['sets'] += 1
                    return True
                else:
                    self.cache_stats['errors'] += 1
                    return False
            else:
                # Cache mémoire avec TTL
                self.memory_cache[key] = {
                    'value': value,
                    'expires_at': time.time() + ttl,
                    'created_at': time.time()
                }
                self.cache_stats['sets'] += 1
                
                # Nettoyage périodique du cache mémoire
                self._cleanup_memory_cache()
                return True
        
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du cache: {e}")
            self.cache_stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime une clé du cache"""
        try:
            if self.cache_type == 'redis' and self.redis_client:
                result = self.redis_client.delete(key)
                return result > 0
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
                return False
        
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Vide tout le cache"""
        try:
            if self.cache_type == 'redis' and self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            
            # Reset des stats
            self.cache_stats = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'errors': 0
            }
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors du vidage du cache: {e}")
            return False
    
    def get_hit_rate(self) -> float:
        """Calcule le taux de cache hits"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests == 0:
            return 0.0
        return (self.cache_stats['hits'] / total_requests) * 100
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du cache"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        
        metrics = {
            'cache_type': self.cache_type,
            'total_requests': total_requests,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'errors': self.cache_stats['errors'],
            'hit_rate_percent': self.get_hit_rate(),
            'status': 'healthy' if self.cache_stats['errors'] < 5 else 'degraded'
        }
        
        if self.cache_type == 'memory':
            metrics.update({
                'memory_cache_size': len(self.memory_cache),
                'memory_cache_keys': list(self.memory_cache.keys())[:10]  # Première 10 clés
            })
        
        return metrics
    
    def _cleanup_memory_cache(self):
        """Nettoie le cache mémoire des entrées expirées"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry['expires_at'] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Limite la taille du cache mémoire (max 1000 entrées)
        if len(self.memory_cache) > 1000:
            # Supprime les plus anciennes
            sorted_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['created_at']
            )
            keys_to_remove = sorted_keys[:100]  # Supprime les 100 plus anciennes
            for key in keys_to_remove:
                del self.memory_cache[key]
    
    def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du cache"""
        health = {
            'cache_type': self.cache_type,
            'is_healthy': True,
            'error_rate': 0.0,
            'response_time_ms': 0.0
        }
        
        # Test de performance
        start_time = time.time()
        test_key = f"health_check_{int(time.time())}"
        test_value = {"test": "data", "timestamp": time.time()}
        
        try:
            # Test set/get
            self.set(test_key, test_value, ttl=10)
            retrieved = self.get(test_key)
            self.delete(test_key)
            
            if retrieved != test_value:
                health['is_healthy'] = False
                health['error'] = "Set/Get test failed"
            
            health['response_time_ms'] = (time.time() - start_time) * 1000
            
        except Exception as e:
            health['is_healthy'] = False
            health['error'] = str(e)
        
        # Calcul du taux d'erreur
        total_operations = sum(self.cache_stats.values())
        if total_operations > 0:
            health['error_rate'] = (self.cache_stats['errors'] / total_operations) * 100
        
        return health
