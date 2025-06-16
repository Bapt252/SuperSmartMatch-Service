#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitor - Monitoring des performances SuperSmartMatch
"""

import time
from typing import Dict, List, Any
from collections import defaultdict, deque

class PerformanceMonitor:
    """
    Moniteur de performances pour SuperSmartMatch
    """
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.requests = deque(maxlen=max_records)
        self.algorithm_stats = defaultdict(list)
        self.start_time = time.time()
    
    def record_request(self, algorithm: str, execution_time: float, 
                      job_count: int, match_count: int):
        """Enregistre une requête de matching"""
        record = {
            'timestamp': time.time(),
            'algorithm': algorithm,
            'execution_time_ms': execution_time,
            'job_count': job_count,
            'match_count': match_count,
            'performance_score': self._calculate_performance_score(execution_time, job_count)
        }
        
        self.requests.append(record)
        self.algorithm_stats[algorithm].append(record)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance"""
        if not self.requests:
            return self._empty_metrics()
        
        recent_requests = list(self.requests)
        
        # Calculs globaux
        total_requests = len(recent_requests)
        avg_execution_time = sum(r['execution_time_ms'] for r in recent_requests) / total_requests
        avg_job_count = sum(r['job_count'] for r in recent_requests) / total_requests
        avg_match_count = sum(r['match_count'] for r in recent_requests) / total_requests
        
        # Performance par algorithme
        algorithm_performance = {}
        for algo in self.algorithm_stats:
            algo_requests = self.algorithm_stats[algo]
            if algo_requests:
                algorithm_performance[algo] = {
                    'request_count': len(algo_requests),
                    'avg_execution_time_ms': sum(r['execution_time_ms'] for r in algo_requests) / len(algo_requests),
                    'avg_performance_score': sum(r['performance_score'] for r in algo_requests) / len(algo_requests)
                }
        
        # Statistiques temporelles
        uptime_seconds = time.time() - self.start_time
        requests_per_minute = (total_requests / uptime_seconds) * 60 if uptime_seconds > 0 else 0
        
        return {
            'total_requests': total_requests,
            'uptime_seconds': uptime_seconds,
            'requests_per_minute': requests_per_minute,
            'average_execution_time_ms': avg_execution_time,
            'average_jobs_per_request': avg_job_count,
            'average_matches_per_request': avg_match_count,
            'algorithm_performance': algorithm_performance,
            'performance_status': self._get_performance_status(avg_execution_time)
        }
    
    def get_algorithm_usage(self) -> Dict[str, Any]:
        """Statistiques d'usage des algorithmes"""
        if not self.requests:
            return {}
        
        algorithm_counts = defaultdict(int)
        for request in self.requests:
            algorithm_counts[request['algorithm']] += 1
        
        total = len(self.requests)
        usage_percentages = {
            algo: (count / total) * 100 
            for algo, count in algorithm_counts.items()
        }
        
        return {
            'algorithm_counts': dict(algorithm_counts),
            'algorithm_percentages': usage_percentages,
            'most_used': max(algorithm_counts.items(), key=lambda x: x[1])[0] if algorithm_counts else None
        }
    
    def _calculate_performance_score(self, execution_time: float, job_count: int) -> float:
        """Calcule un score de performance (plus c'est bas, mieux c'est)"""
        if job_count == 0:
            return 100.0
        
        # Score basé sur le temps par job
        time_per_job = execution_time / job_count
        
        # Échelle : excellent < 20ms/job, bon < 50ms/job, acceptable < 100ms/job
        if time_per_job < 20:
            return 95  # Excellent
        elif time_per_job < 50:
            return 80  # Bon
        elif time_per_job < 100:
            return 60  # Acceptable
        else:
            return 30  # À améliorer
    
    def _get_performance_status(self, avg_execution_time: float) -> str:
        """Détermine le statut de performance"""
        if avg_execution_time < 1000:  # < 1s
            return "excellent"
        elif avg_execution_time < 3000:  # < 3s
            return "good"
        elif avg_execution_time < 5000:  # < 5s
            return "acceptable"
        else:
            return "needs_optimization"
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Métriques par défaut quand aucune donnée"""
        return {
            'total_requests': 0,
            'uptime_seconds': time.time() - self.start_time,
            'requests_per_minute': 0,
            'average_execution_time_ms': 0,
            'average_jobs_per_request': 0,
            'average_matches_per_request': 0,
            'algorithm_performance': {},
            'performance_status': 'no_data'
        }
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.requests.clear()
        self.algorithm_stats.clear()
        self.start_time = time.time()
    
    def get_recent_requests(self, count: int = 10) -> List[Dict[str, Any]]:
        """Retourne les N dernières requêtes"""
        return list(self.requests)[-count:]
