#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration du service SuperSmartMatch
"""

import os
from typing import Dict, Any

class Config:
    """
    Configuration principale du service
    """
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersmartmatch-dev-key-2025')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuration Base de données
    DATABASE_URL = os.getenv(
        'DATABASE_URL', 
        'postgresql://user:password@localhost:5432/nexten'
    )
    
    # Configuration Redis (Cache)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Configuration APIs externes
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Configuration des algorithmes
    DEFAULT_ALGORITHM = os.getenv('DEFAULT_ALGORITHM', 'auto')
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 heure
    
    # Configuration de performance
    MAX_JOBS_PER_REQUEST = int(os.getenv('MAX_JOBS_PER_REQUEST', '100'))
    DEFAULT_RESULT_LIMIT = int(os.getenv('DEFAULT_RESULT_LIMIT', '10'))
    
    # Configuration de monitoring
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'True').lower() == 'true'
    METRICS_RETENTION_DAYS = int(os.getenv('METRICS_RETENTION_DAYS', '30'))
    
    @staticmethod
    def validate_config() -> Dict[str, Any]:
        """
        Valide la configuration et retourne les éléments manquants
        """
        missing = []
        warnings = []
        
        if not Config.OPENAI_API_KEY:
            warnings.append('OPENAI_API_KEY non configurée - Certains algorithmes ne fonctionneront pas')
        
        if not Config.GOOGLE_MAPS_API_KEY:
            warnings.append('GOOGLE_MAPS_API_KEY non configurée - SmartMatch limité')
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'warnings': warnings
        }

class AlgorithmConfig:
    """
    Configuration spécifique des algorithmes
    """
    
    # Pondérations par défaut pour Enhanced Matching
    ENHANCED_WEIGHTS = {
        'junior': {
            'skills': 0.25,
            'experience': 0.20,
            'location': 0.20,
            'contract': 0.15,
            'salary': 0.15,
            'date': 0.05
        },
        'confirmed': {
            'skills': 0.30,
            'location': 0.20,
            'salary': 0.20,
            'contract': 0.15,
            'experience': 0.10,
            'date': 0.05
        },
        'senior': {
            'skills': 0.35,
            'salary': 0.25,
            'location': 0.15,
            'contract': 0.10,
            'experience': 0.05,
            'date': 0.10
        }
    }
    
    # Configuration SmartMatch
    SMARTMATCH_CONFIG = {
        'max_commute_time': 60,  # minutes
        'enable_geocoding': True,
        'distance_weight': 0.3
    }
    
    # Configuration Semantic Analyzer
    SEMANTIC_CONFIG = {
        'similarity_threshold': 0.7,
        'use_wordnet': True,
        'enable_skill_groups': True
    }
    
    # Règles d'auto-sélection
    AUTO_SELECTION_RULES = {
        'junior_developer': {
            'experience_range': (0, 2),
            'preferred_algorithm': 'enhanced',
            'reason': 'Pondération adaptée aux profils juniors'
        },
        'senior_developer': {
            'experience_range': (7, 50),
            'preferred_algorithm': 'semantic',
            'reason': 'Analyse fine des compétences pour les seniors'
        },
        'geo_sensitive': {
            'max_commute_preference': 30,
            'preferred_algorithm': 'smart-match',
            'reason': 'Optimisé pour la géolocalisation'
        },
        'high_precision': {
            'min_job_count': 50,
            'preferred_algorithm': 'hybrid',
            'reason': 'Précision maximale pour un grand nombre d\'offres'
        }
    }

class PerformanceConfig:
    """
    Configuration de performance
    """
    
    # Limites de taux
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '100'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
    
    # Configuration du cache
    CACHE_STRATEGIES = {
        'fast': {
            'enable_cache': True,
            'ttl': 1800,  # 30 minutes
            'compression': True
        },
        'balanced': {
            'enable_cache': True,
            'ttl': 3600,  # 1 heure
            'compression': True
        },
        'accuracy': {
            'enable_cache': False,
            'ttl': 0,
            'compression': False
        }
    }
    
    # Seuils de performance
    PERFORMANCE_THRESHOLDS = {
        'response_time_warning_ms': 1000,
        'response_time_critical_ms': 3000,
        'memory_warning_mb': 512,
        'memory_critical_mb': 1024
    }
