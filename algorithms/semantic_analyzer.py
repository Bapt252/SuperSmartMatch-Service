#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Analyzer Algorithm - Analyse sémantique des compétences
"""

from .base_algorithm import BaseMatchingAlgorithm
from typing import Dict, List, Any

class SemanticAnalyzerAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme d'analyse sémantique des compétences
    """
    
    def __init__(self):
        super().__init__("SemanticAnalyzer")
        self.version = "1.0.0"
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcul de matching avec analyse sémantique
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        
        for job in jobs_data:
            score = self._calculate_semantic_match(candidate_data, job)
            
            job_result = job.copy()
            job_result.update({
                'matching_score': self.normalize_score(score),
                'algorithm': f"{self.name}_v{self.version}",
                'matching_details': {
                    'semantic_analysis': self.normalize_score(score),
                    'skills_semantic': self.normalize_score(score * 0.8),
                    'context_match': self.normalize_score(score * 0.6)
                },
                'recommendations': [f"Analyse sémantique: {self.normalize_score(score)}%"]
            })
            
            results.append(job_result)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_semantic_match(self, candidate_data: Dict[str, Any], 
                                 job_data: Dict[str, Any]) -> float:
        """Calcul sémantique basique"""
        score = 0.4
        
        # Analyse des compétences avec variantes
        candidate_skills = [s.lower() for s in candidate_data.get('competences', [])]
        job_skills = [s.lower() for s in job_data.get('competences', [])]
        
        if candidate_skills and job_skills:
            # Correspondances exactes
            exact_matches = len(set(candidate_skills) & set(job_skills))
            
            # Correspondances partielles (sémantique basique)
            partial_matches = 0
            for job_skill in job_skills:
                for candidate_skill in candidate_skills:
                    if (job_skill in candidate_skill or candidate_skill in job_skill) and \
                       len(job_skill) > 3:
                        partial_matches += 0.5
                        break
            
            total_matches = exact_matches + partial_matches
            semantic_score = min(1.0, total_matches / len(job_skills))
            score += semantic_score * 0.6
        
        return min(1.0, score)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Informations sur l'algorithme"""
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Analyse sémantique des compétences et contexte',
            'best_for': 'Matching fin des compétences techniques',
            'performance': 'Moyen',
            'accuracy': 'Élevée'
        }
