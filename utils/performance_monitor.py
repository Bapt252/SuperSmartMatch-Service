#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitoring des performances pour SuperSmartMatch
"""

import time
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Monitore les performances du service SuperSmartMatch
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # Historique des requêtes
        self.request_history = deque(maxlen=max_history_size)
        
        # Métriques par algorithme
        self.algorithm_metrics = defaultdict(lambda: {
            'request_count': 0,
            'total_execution_time': 0,
            'average_execution_time': 0,
            'min_execution_time': float('inf'),
            'max_execution_time': 0,
            'success_count': 0,
            'error_count': 0
        })
        
        # Métriques globales
        self.global_metrics = {
            'total_requests': 0,
            'total_execution_time': 0,
            'average_response_time': 0,
            'requests_per_minute': 0,
            'uptime_start': time.time()
        }
        
        # Cache des métriques calculées
        self._metrics_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 30  # 30 secondes
    
    def record_request(self, algorithm: str, execution_time: float, 
                      job_count: int, match_count: int, 
                      success: bool = True) -> None:
        """
        Enregistre une requête de matching
        
        Args:
            algorithm: Nom de l'algorithme utilisé
            execution_time: Temps d'exécution en millisecondes
            job_count: Nombre d'offres analysées
            match_count: Nombre de matches retournés
            success: Si la requête a réussi
        """
        timestamp = time.time()
        
        # Enregistrement dans l'historique
        request_record = {
            'timestamp': timestamp,
            'algorithm': algorithm,
            'execution_time': execution_time,
            'job_count': job_count,
            'match_count': match_count,
            'success': success
        }
        
        self.request_history.append(request_record)
        
        # Mise à jour des métriques par algorithme
        algo_metrics = self.algorithm_metrics[algorithm]
        algo_metrics['request_count'] += 1
        
        if success:
            algo_metrics['success_count'] += 1
            algo_metrics['total_execution_time'] += execution_time
            algo_metrics['min_execution_time'] = min(
                algo_metrics['min_execution_time'], execution_time
            )
            algo_metrics['max_execution_time'] = max(
                algo_metrics['max_execution_time'], execution_time
            )
            algo_metrics['average_execution_time'] = (
                algo_metrics['total_execution_time'] / algo_metrics['success_count']
            )
        else:
            algo_metrics['error_count'] += 1
        
        # Mise à jour des métriques globales
        self.global_metrics['total_requests'] += 1
        if success:
            self.global_metrics['total_execution_time'] += execution_time
            self.global_metrics['average_response_time'] = (
                self.global_metrics['total_execution_time'] / 
                sum(algo['success_count'] for algo in self.algorithm_metrics.values())
            )
        
        # Invalidation du cache
        self._cache_timestamp = 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques complètes
        """
        current_time = time.time()
        
        # Vérification du cache
        if (current_time - self._cache_timestamp) < self._cache_ttl:
            return self._metrics_cache
        
        # Calcul des nouvelles métriques
        metrics = {
            'global': self._calculate_global_metrics(),
            'algorithms': dict(self.algorithm_metrics),
            'recent_performance': self._calculate_recent_performance(),
            'trends': self._calculate_trends(),
            'health_status': self._calculate_health_status()
        }
        
        # Mise en cache
        self._metrics_cache = metrics
        self._cache_timestamp = current_time
        
        return metrics
    
    def _calculate_global_metrics(self) -> Dict[str, Any]:
        """
        Calcule les métriques globales
        """
        current_time = time.time()
        uptime_seconds = current_time - self.global_metrics['uptime_start']
        
        # Calcul des requêtes par minute
        recent_requests = [
            req for req in self.request_history
            if current_time - req['timestamp'] <= 60
        ]
        
        return {
            'total_requests': self.global_metrics['total_requests'],
            'average_response_time_ms': round(self.global_metrics['average_response_time'], 2),
            'requests_per_minute': len(recent_requests),
            'uptime_seconds': round(uptime_seconds, 2),
            'uptime_formatted': self._format_uptime(uptime_seconds),
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_recent_performance(self, window_minutes: int = 5) -> Dict[str, Any]:
        """
        Calcule les performances récentes
        """
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        recent_requests = [
            req for req in self.request_history
            if req['timestamp'] >= window_start
        ]
        
        if not recent_requests:
            return {
                'window_minutes': window_minutes,
                'request_count': 0,
                'average_response_time': 0,
                'success_rate': 0
            }
        
        successful_requests = [req for req in recent_requests if req['success']]
        
        avg_response_time = 0
        if successful_requests:
            avg_response_time = sum(
                req['execution_time'] for req in successful_requests
            ) / len(successful_requests)
        
        return {
            'window_minutes': window_minutes,
            'request_count': len(recent_requests),
            'average_response_time_ms': round(avg_response_time, 2),
            'success_rate': len(successful_requests) / len(recent_requests) if recent_requests else 0,
            'algorithms_used': list(set(req['algorithm'] for req in recent_requests))
        }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """
        Calcule les tendances de performance
        """
        if len(self.request_history) < 10:
            return {'insufficient_data': True}
        
        # Comparaison dernières 5 minutes vs 5 minutes précédentes
        current_time = time.time()
        
        recent_window = [
            req for req in self.request_history
            if current_time - req['timestamp'] <= 300  # 5 minutes
        ]
        
        previous_window = [
            req for req in self.request_history
            if 300 < current_time - req['timestamp'] <= 600  # 5-10 minutes
        ]
        
        if not recent_window or not previous_window:
            return {'insufficient_data': True}
        
        # Calcul des moyennes
        recent_avg = sum(req['execution_time'] for req in recent_window if req['success']) / max(1, len([req for req in recent_window if req['success']]))
        previous_avg = sum(req['execution_time'] for req in previous_window if req['success']) / max(1, len([req for req in previous_window if req['success']]))
        
        # Calcul de la tendance
        if previous_avg > 0:
            performance_trend = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            performance_trend = 0
        
        return {
            'performance_trend_percent': round(performance_trend, 2),
            'trend_direction': 'improving' if performance_trend < 0 else 'degrading' if performance_trend > 5 else 'stable',
            'recent_avg_ms': round(recent_avg, 2),
            'previous_avg_ms': round(previous_avg, 2)
        }
    
    def _calculate_health_status(self) -> Dict[str, Any]:
        """
        Calcule le statut de santé du service
        """
        success_rate = self._calculate_success_rate()
        avg_response_time = self.global_metrics['average_response_time']
        
        # Détermination du statut
        if success_rate >= 0.98 and avg_response_time < 500:
            status = 'excellent'
            color = 'green'
        elif success_rate >= 0.95 and avg_response_time < 1000:
            status = 'good'
            color = 'green'
        elif success_rate >= 0.90 and avg_response_time < 2000:
            status = 'fair'
            color = 'yellow'
        else:
            status = 'poor'
            color = 'red'
        
        # Alertes
        alerts = []
        if success_rate < 0.95:
            alerts.append(f'Taux de succès bas: {success_rate:.1%}')
        
        if avg_response_time > 1000:
            alerts.append(f'Temps de réponse élevé: {avg_response_time:.0f}ms')
        
        return {
            'status': status,
            'color': color,
            'success_rate': success_rate,
            'average_response_time_ms': round(avg_response_time, 2),
            'alerts': alerts
        }
    
    def _calculate_success_rate(self) -> float:
        """
        Calcule le taux de succès global
        """
        total_success = sum(algo['success_count'] for algo in self.algorithm_metrics.values())
        total_requests = self.global_metrics['total_requests']
        
        return total_success / max(1, total_requests)
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """
        Formate le temps de fonctionnement
        """
        uptime_delta = timedelta(seconds=int(uptime_seconds))
        
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    def get_algorithm_usage(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation des algorithmes
        """
        total_requests = sum(algo['request_count'] for algo in self.algorithm_metrics.values())
        
        if total_requests == 0:
            return {'no_data': True}
        
        usage_stats = {}
        
        for algo_name, metrics in self.algorithm_metrics.items():
            usage_percentage = (metrics['request_count'] / total_requests) * 100
            
            usage_stats[algo_name] = {
                'request_count': metrics['request_count'],
                'usage_percentage': round(usage_percentage, 1),
                'success_rate': metrics['success_count'] / max(1, metrics['request_count']),
                'average_execution_time_ms': round(metrics['average_execution_time'], 2),
                'performance_rating': self._calculate_performance_rating(
                    metrics['average_execution_time'], 
                    metrics['success_count'] / max(1, metrics['request_count'])
                )
            }
        
        return {
            'total_requests': total_requests,
            'algorithms': usage_stats,
            'most_used': max(usage_stats.items(), key=lambda x: x[1]['request_count'])[0] if usage_stats else None,
            'best_performance': max(
                usage_stats.items(), 
                key=lambda x: x[1]['performance_rating']
            )[0] if usage_stats else None
        }
    
    def _calculate_performance_rating(self, avg_time: float, success_rate: float) -> float:
        """
        Calcule une note de performance (0-10)
        """
        # Note basée sur le temps de réponse (0-5 points)
        if avg_time < 200:
            time_score = 5
        elif avg_time < 500:
            time_score = 4
        elif avg_time < 1000:
            time_score = 3
        elif avg_time < 2000:
            time_score = 2
        else:
            time_score = 1
        
        # Note basée sur le taux de succès (0-5 points)
        success_score = success_rate * 5
        
        return round(time_score + success_score, 1)
    
    def reset_metrics(self) -> None:
        """
        Remet à zéro toutes les métriques
        """
        self.request_history.clear()
        self.algorithm_metrics.clear()
        self.global_metrics = {
            'total_requests': 0,
            'total_execution_time': 0,
            'average_response_time': 0,
            'requests_per_minute': 0,
            'uptime_start': time.time()
        }
        self._cache_timestamp = 0
        
        logger.info("Métriques remises à zéro")
