#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Settings - SuperSmartMatch V3.0
"""

import os
from typing import Dict, Any

class Config:
    """
    Configuration de base pour SuperSmartMatch V3.0
    """
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersmartmatch-v3-enhanced-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuration base de données et cache
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Configuration SuperSmartMatch
    SUPERSMARTMATCH_VERSION = '3.0.0'
    DEFAULT_ALGORITHM = 'enhanced-v3'  # V3.0 par défaut
    
    # Limites et performances
    MAX_JOBS_PER_REQUEST = int(os.getenv('MAX_JOBS_PER_REQUEST', '1000'))
    MAX_EXECUTION_TIME_SECONDS = int(os.getenv('MAX_EXECUTION_TIME_SECONDS', '30'))
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '3600'))
    
    # Configuration algorithmes
    ALGORITHM_WEIGHTS = {
        'enhanced-v3': {
            'job_specificity_match': 0.35,
            'sector_compatibility': 0.25,
            'experience_relevance': 0.20,
            'skills_match': 0.15,
            'location_match': 0.05
        },
        'enhanced-v2': {
            'sector_compatibility': 0.40,
            'skills_match': 0.25,
            'experience_relevance': 0.20,
            'location_match': 0.10,
            'contract_match': 0.05
        }
    }
    
    # Configuration secteurs V3.0
    SECTOR_ANALYSIS_ENABLED = True
    JOB_SPECIFICITY_ENABLED = True
    BLOCKING_FACTORS_ENABLED = True
    
    # Seuils de performance
    PERFORMANCE_THRESHOLDS = {
        'excellent_ms': 1000,
        'good_ms': 3000,
        'acceptable_ms': 5000
    }
    
    # Configuration logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuration API
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100/hour')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Chemins et fichiers
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    
    @classmethod
    def get_algorithm_config(cls, algorithm_name: str) -> Dict[str, Any]:
        """Retourne la configuration d'un algorithme"""
        return {
            'weights': cls.ALGORITHM_WEIGHTS.get(algorithm_name, {}),
            'version': cls.SUPERSMARTMATCH_VERSION,
            'performance_thresholds': cls.PERFORMANCE_THRESHOLDS
        }
    
    @classmethod
    def get_feature_flags(cls) -> Dict[str, bool]:
        """Retourne les feature flags activés"""
        return {
            'sector_analysis_v3': cls.SECTOR_ANALYSIS_ENABLED,
            'job_specificity_v3': cls.JOB_SPECIFICITY_ENABLED,
            'blocking_factors_v3': cls.BLOCKING_FACTORS_ENABLED,
            'cache_enabled': bool(cls.REDIS_URL),
            'debug_mode': cls.DEBUG
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Valide la configuration et retourne les erreurs"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validation des limites
        if cls.MAX_JOBS_PER_REQUEST > 10000:
            validation_results['warnings'].append(
                "MAX_JOBS_PER_REQUEST très élevé, performances possiblement dégradées"
            )
        
        if cls.MAX_EXECUTION_TIME_SECONDS > 60:
            validation_results['warnings'].append(
                "MAX_EXECUTION_TIME_SECONDS très élevé, risque de timeout"
            )
        
        # Validation des algorithmes
        if cls.DEFAULT_ALGORITHM not in cls.ALGORITHM_WEIGHTS:
            validation_results['errors'].append(
                f"DEFAULT_ALGORITHM '{cls.DEFAULT_ALGORITHM}' non configuré dans ALGORITHM_WEIGHTS"
            )
            validation_results['is_valid'] = False
        
        return validation_results

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CACHE_TTL_SECONDS = 300  # Cache plus court en dev
    MAX_JOBS_PER_REQUEST = 100  # Limite réduite pour tests

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    SECRET_KEY = os.getenv('SECRET_KEY')  # Obligatoire en production
    
    # Validation en production
    @classmethod
    def validate_production_config(cls):
        """Validation spécifique production"""
        if not os.getenv('SECRET_KEY'):
            raise ValueError("SECRET_KEY obligatoire en production")
        
        if cls.DEBUG:
            raise ValueError("DEBUG doit être False en production")

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DEBUG = True
    CACHE_TTL_SECONDS = 60  # Cache très court pour tests
    REDIS_URL = None  # Pas de Redis en test
    MAX_JOBS_PER_REQUEST = 10  # Très limité pour tests

# Configuration par environnement
config_by_env = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}

def get_config(env_name: str = None) -> Config:
    """Retourne la configuration selon l'environnement"""
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'default')
    
    return config_by_env.get(env_name, Config)
