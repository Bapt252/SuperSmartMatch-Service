#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Match Algorithm - Classe de base pour compatibilité
"""

from .base_algorithm import BaseMatchingAlgorithm
from typing import Dict, List, Any

class SmartMatchAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme Smart Match de base (pour compatibilité)
    """
    
    def __init__(self):
        super().__init__("SmartMatch")
        self.version = "1.0.0"
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcul simple de matching pour compatibilité
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        
        for job in jobs_data:
            # Calcul de base très simple
            score = self._calculate_basic_match(candidate_data, job)
            
            job_result = job.copy()
            job_result.update({
                'matching_score': self.normalize_score(score),
                'algorithm': f"{self.name}_v{self.version}",
                'matching_details': {
                    'basic_match': self.normalize_score(score)
                },
                'recommendations': [f"Score calculé: {self.normalize_score(score)}%"]
            })
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_basic_match(self, candidate_data: Dict[str, Any], 
                              job_data: Dict[str, Any]) -> float:
        """Calcul de matching très basique"""
        score = 0.5  # Score de base
        
        # Compétences
        candidate_skills = candidate_data.get('competences', [])
        job_skills = job_data.get('competences', [])
        
        if candidate_skills and job_skills:
            skill_matches = len(set([s.lower() for s in candidate_skills]) & 
                              set([s.lower() for s in job_skills]))
            skill_score = min(1.0, skill_matches / len(job_skills))
            score += skill_score * 0.4
        
        # Expérience
        experience = candidate_data.get('annees_experience', 0)
        if experience > 0:
            score += min(0.3, experience * 0.05)
        
        return min(1.0, score)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Informations sur l'algorithme"""
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Algorithme de matching simple pour compatibilité',
            'best_for': 'Tests basiques',
            'performance': 'Élevé',
            'accuracy': 'Basique'
        }
