#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Selector Engine - Sélection automatique d'algorithme
"""

from typing import Dict, List, Any, Optional

class AutoSelectorEngine:
    """
    Moteur de sélection automatique d'algorithmes
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.selection_rules = {
            'enhanced-v3': {
                'priority': 1,
                'description': 'Précision métier fine V3.0',
                'best_for': 'Matching avec granularité métier'
            },
            'enhanced-v2': {
                'priority': 2, 
                'description': 'Intelligence sectorielle V2.1',
                'best_for': 'Matching sectoriel basique'
            },
            'semantic': {
                'priority': 3,
                'description': 'Analyse sémantique',
                'best_for': 'Compétences techniques'
            },
            'hybrid': {
                'priority': 4,
                'description': 'Approche multi-critères',
                'best_for': 'Précision maximale'
            },
            'smart-match': {
                'priority': 5,
                'description': 'Matching basique',
                'best_for': 'Tests rapides'
            }
        }
    
    def select_algorithm(self, candidate_data: Dict[str, Any], 
                        jobs_data: List[Dict[str, Any]], 
                        options: Dict[str, Any] = None) -> str:
        """
        Sélectionne automatiquement le meilleur algorithme
        """
        if options is None:
            options = {}
        
        # Performance mode
        performance_mode = options.get('performance_mode', 'balanced')
        
        if performance_mode == 'fast':
            return 'smart-match'
        elif performance_mode == 'accuracy':
            return 'enhanced-v3'  # V3.0 pour précision maximale
        else:
            # Mode balanced : privilégier Enhanced V3.0
            return 'enhanced-v3'
    
    def get_available_algorithms(self) -> Dict[str, Any]:
        """Retourne les algorithmes disponibles avec leurs infos"""
        return self.selection_rules
    
    def get_recommendation(self, use_case: str) -> str:
        """Recommandation d'algorithme selon le cas d'usage"""
        recommendations = {
            'precision': 'enhanced-v3',
            'performance': 'smart-match', 
            'semantic': 'semantic',
            'hybrid': 'hybrid',
            'sector': 'enhanced-v3',  # V3.0 pour granularité sectorielle
            'default': 'enhanced-v3'  # V3.0 par défaut
        }
        
        return recommendations.get(use_case, 'enhanced-v3')
    
    def analyze_data_complexity(self, candidate_data: Dict[str, Any], 
                               jobs_data: List[Dict[str, Any]]) -> str:
        """Analyse la complexité des données pour recommander un algorithme"""
        
        # Critères de complexité
        job_count = len(jobs_data)
        candidate_skills = len(candidate_data.get('competences', []))
        candidate_experience = candidate_data.get('annees_experience', 0)
        
        # Complexité élevée : utiliser enhanced-v3
        if job_count > 50 or candidate_skills > 10 or candidate_experience > 5:
            return 'enhanced-v3'
        
        # Complexité moyenne : enhanced-v3 aussi (précision)
        elif job_count > 10 or candidate_skills > 5:
            return 'enhanced-v3'
        
        # Complexité faible : smart-match suffit
        else:
            return 'smart-match'
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Informations sur le moteur de sélection"""
        return {
            'name': 'AutoSelectorEngine',
            'version': self.version,
            'description': 'Sélection automatique d\'algorithme optimisée V3.0',
            'default_selection': 'enhanced-v3',
            'selection_criteria': [
                'Performance mode',
                'Complexité des données', 
                'Cas d\'usage spécifique',
                'Priorité à la précision métier V3.0'
            ],
            'available_algorithms': list(self.selection_rules.keys())
        }
