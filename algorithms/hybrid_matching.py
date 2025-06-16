#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Matching Algorithm - Combinaison intelligente d'algorithmes
"""

from .base_algorithm import BaseMatchingAlgorithm
from typing import Dict, List, Any

class HybridMatchingAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme hybride combinant plusieurs approches
    """
    
    def __init__(self):
        super().__init__("HybridMatching")
        self.version = "1.0.0"
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcul hybride combinant plusieurs méthodes
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        
        for job in jobs_data:
            score = self._calculate_hybrid_match(candidate_data, job)
            
            job_result = job.copy()
            job_result.update({
                'matching_score': self.normalize_score(score),
                'algorithm': f"{self.name}_v{self.version}",
                'matching_details': {
                    'hybrid_score': self.normalize_score(score),
                    'skills_weight': self.normalize_score(score * 0.4),
                    'experience_weight': self.normalize_score(score * 0.3),
                    'context_weight': self.normalize_score(score * 0.3)
                },
                'recommendations': [f"Analyse hybride: {self.normalize_score(score)}%"]
            })
            
            results.append(job_result)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_hybrid_match(self, candidate_data: Dict[str, Any], 
                               job_data: Dict[str, Any]) -> float:
        """Calcul hybride multi-critères"""
        
        # 1. Score compétences (40%)
        skills_score = self._calculate_skills_match(
            candidate_data.get('competences', []),
            job_data.get('competences', [])
        )
        
        # 2. Score expérience (30%)
        experience_score = self._calculate_experience_match(
            candidate_data.get('annees_experience', 0)
        )
        
        # 3. Score contextuel (30%)
        context_score = self._calculate_context_match(candidate_data, job_data)
        
        # Combinaison pondérée
        hybrid_score = (
            skills_score * 0.4 +
            experience_score * 0.3 +
            context_score * 0.3
        )
        
        return min(1.0, hybrid_score)
    
    def _calculate_skills_match(self, candidate_skills: List[str], 
                               job_skills: List[str]) -> float:
        """Calcul correspondance compétences"""
        if not job_skills:
            return 0.7
        if not candidate_skills:
            return 0.1
        
        candidate_norm = [s.lower().strip() for s in candidate_skills]
        job_norm = [s.lower().strip() for s in job_skills]
        
        matches = len(set(candidate_norm) & set(job_norm))
        return min(1.0, matches / len(job_norm))
    
    def _calculate_experience_match(self, years_experience: int) -> float:
        """Calcul score expérience"""
        if years_experience == 0:
            return 0.3
        elif years_experience <= 2:
            return 0.6
        elif years_experience <= 5:
            return 0.8
        else:
            return 1.0
    
    def _calculate_context_match(self, candidate_data: Dict[str, Any], 
                                job_data: Dict[str, Any]) -> float:
        """Calcul score contextuel"""
        score = 0.5
        
        # Titre/secteur
        candidate_title = candidate_data.get('titre_poste', '').lower()
        job_title = job_data.get('titre', '').lower()
        
        if candidate_title and job_title:
            common_words = set(candidate_title.split()) & set(job_title.split())
            if common_words:
                score += 0.3
        
        # Secteur
        candidate_sector = candidate_data.get('secteur', '').lower()
        job_sector = job_data.get('secteur', '').lower()
        
        if candidate_sector and job_sector and candidate_sector == job_sector:
            score += 0.2
        
        return min(1.0, score)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Informations sur l'algorithme"""
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Combinaison intelligente de plusieurs algorithmes',
            'best_for': 'Précision maximale multi-critères',
            'performance': 'Moyen',
            'accuracy': 'Très élevée'
        }
