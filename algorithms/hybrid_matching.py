#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algorithme de matching hybride pour SuperSmartMatch

Cet algorithme combine intelligemment plusieurs algorithmes
"""

import logging
from typing import Dict, List, Any
from .base_algorithm import BaseMatchingAlgorithm
from .smart_match import SmartMatchAlgorithm
from .enhanced_matching import EnhancedMatchingAlgorithm
from .semantic_analyzer import SemanticAnalyzerAlgorithm

logger = logging.getLogger(__name__)

class HybridMatchingAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme Hybrid - Combine plusieurs algorithmes pour une précision maximale
    """
    
    def __init__(self):
        super().__init__("Hybrid")
        
        # Initialisation des algorithmes sous-jacents
        self.smart_match = SmartMatchAlgorithm()
        self.enhanced = EnhancedMatchingAlgorithm()
        self.semantic = SemanticAnalyzerAlgorithm()
        
        # Pondérations pour chaque algorithme
        self.algorithm_weights = {
            'enhanced': 0.4,    # Pondération équilibrée
            'semantic': 0.35,   # Focus compétences
            'smart_match': 0.25 # Géolocalisation
        }
        
        # Seuils de confiance
        self.confidence_thresholds = {
            'high': 0.85,
            'medium': 0.70,
            'low': 0.50
        }
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les matches en combinant plusieurs algorithmes
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        # Exécution de tous les algorithmes
        logger.info(f"Exécution hybride sur {len(jobs_data)} offres")
        
        try:
            enhanced_results = self.enhanced.calculate_matches(candidate_data, jobs_data)
            semantic_results = self.semantic.calculate_matches(candidate_data, jobs_data)
            smart_results = self.smart_match.calculate_matches(candidate_data, jobs_data)
            
            # Combinaison des résultats
            hybrid_results = self._combine_results(
                enhanced_results, semantic_results, smart_results
            )
            
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Erreur dans l'algorithme hybride: {e}")
            # Fallback sur Enhanced en cas d'erreur
            return self.enhanced.calculate_matches(candidate_data, jobs_data)
    
    def _combine_results(self, enhanced_results: List[Dict[str, Any]], 
                        semantic_results: List[Dict[str, Any]], 
                        smart_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine les résultats de plusieurs algorithmes
        """
        # Création d'un dictionnaire pour accéder rapidement aux résultats par job_id
        enhanced_dict = {self._get_job_id(job): job for job in enhanced_results}
        semantic_dict = {self._get_job_id(job): job for job in semantic_results}
        smart_dict = {self._get_job_id(job): job for job in smart_results}
        
        combined_results = []
        
        # Prendre tous les jobs uniques
        all_job_ids = set(enhanced_dict.keys()) | set(semantic_dict.keys()) | set(smart_dict.keys())
        
        for job_id in all_job_ids:
            # Récupération des scores de chaque algorithme
            enhanced_job = enhanced_dict.get(job_id)
            semantic_job = semantic_dict.get(job_id)
            smart_job = smart_dict.get(job_id)
            
            # Utilisation du job de référence (premier disponible)
            base_job = enhanced_job or semantic_job or smart_job
            if not base_job:
                continue
            
            # Calcul du score hybride
            hybrid_score = self._calculate_hybrid_score(
                enhanced_job, semantic_job, smart_job
            )
            
            # Analyse de consensus
            consensus_analysis = self._analyze_consensus(
                enhanced_job, semantic_job, smart_job
            )
            
            # Construction du résultat hybride
            hybrid_job = base_job.copy()
            hybrid_job['matching_score'] = hybrid_score
            hybrid_job['algorithm'] = f"{self.name}_v{self.version}"
            hybrid_job['hybrid_details'] = {
                'enhanced_score': enhanced_job['matching_score'] if enhanced_job else 0,
                'semantic_score': semantic_job['matching_score'] if semantic_job else 0,
                'smart_score': smart_job['matching_score'] if smart_job else 0,
                'consensus': consensus_analysis,
                'confidence_level': self._get_confidence_level(hybrid_score, consensus_analysis)
            }
            
            # Détails de matching combinés
            hybrid_job['matching_details'] = self._combine_matching_details(
                enhanced_job, semantic_job, smart_job
            )
            
            combined_results.append(hybrid_job)
        
        # Tri par score hybride décroissant
        combined_results.sort(key=lambda x: x['matching_score'], reverse=True)
        return combined_results
    
    def _get_job_id(self, job: Dict[str, Any]) -> str:
        """
        Génère un ID unique pour un job
        """
        # Utilise plusieurs champs pour créer un ID unique
        return f"{job.get('id', '')}-{job.get('titre', '')}-{job.get('entreprise', '')}"
    
    def _calculate_hybrid_score(self, enhanced_job: Dict[str, Any], 
                               semantic_job: Dict[str, Any], 
                               smart_job: Dict[str, Any]) -> int:
        """
        Calcule le score hybride pondéré
        """
        # Récupération des scores (0 si l'algorithme n'a pas retourné de résultat)
        enhanced_score = enhanced_job['matching_score'] if enhanced_job else 0
        semantic_score = semantic_job['matching_score'] if semantic_job else 0
        smart_score = smart_job['matching_score'] if smart_job else 0
        
        # Calcul pondéré
        weighted_score = (
            enhanced_score * self.algorithm_weights['enhanced'] +
            semantic_score * self.algorithm_weights['semantic'] +
            smart_score * self.algorithm_weights['smart_match']
        )
        
        # Bonus de consensus
        scores = [s for s in [enhanced_score, semantic_score, smart_score] if s > 0]
        if len(scores) >= 2:
            # Calcul de l'écart-type pour mesurer le consensus
            avg_score = sum(scores) / len(scores)
            variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
            std_dev = variance ** 0.5
            
            # Bonus si les scores sont proches (consensus fort)
            if std_dev < 10:  # Scores très proches
                consensus_bonus = 5
            elif std_dev < 15:  # Scores assez proches
                consensus_bonus = 3
            else:
                consensus_bonus = 0
            
            weighted_score += consensus_bonus
        
        return min(100, max(0, int(weighted_score)))
    
    def _analyze_consensus(self, enhanced_job: Dict[str, Any], 
                          semantic_job: Dict[str, Any], 
                          smart_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse le consensus entre les algorithmes
        """
        scores = []
        algorithm_names = []
        
        if enhanced_job:
            scores.append(enhanced_job['matching_score'])
            algorithm_names.append('enhanced')
        
        if semantic_job:
            scores.append(semantic_job['matching_score'])
            algorithm_names.append('semantic')
        
        if smart_job:
            scores.append(smart_job['matching_score'])
            algorithm_names.append('smart_match')
        
        if not scores:
            return {'level': 'none', 'variance': 0, 'agreement': 'no_data'}
        
        if len(scores) == 1:
            return {
                'level': 'single_algorithm',
                'variance': 0,
                'agreement': 'single_source',
                'contributing_algorithms': algorithm_names
            }
        
        # Calcul de la variance
        avg_score = sum(scores) / len(scores)
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Détermination du niveau de consensus
        if std_dev < 5:
            consensus_level = 'very_high'
            agreement = 'strong_agreement'
        elif std_dev < 10:
            consensus_level = 'high'
            agreement = 'good_agreement'
        elif std_dev < 15:
            consensus_level = 'medium'
            agreement = 'moderate_agreement'
        elif std_dev < 25:
            consensus_level = 'low'
            agreement = 'weak_agreement'
        else:
            consensus_level = 'very_low'
            agreement = 'disagreement'
        
        return {
            'level': consensus_level,
            'variance': round(variance, 2),
            'std_deviation': round(std_dev, 2),
            'agreement': agreement,
            'contributing_algorithms': algorithm_names,
            'score_range': f"{min(scores)}-{max(scores)}"
        }
    
    def _get_confidence_level(self, hybrid_score: int, 
                             consensus_analysis: Dict[str, Any]) -> str:
        """
        Détermine le niveau de confiance du résultat
        """
        consensus_level = consensus_analysis['level']
        
        if hybrid_score >= 85 and consensus_level in ['very_high', 'high']:
            return 'very_high'
        elif hybrid_score >= 75 and consensus_level in ['very_high', 'high', 'medium']:
            return 'high'
        elif hybrid_score >= 60 and consensus_level not in ['very_low']:
            return 'medium'
        elif hybrid_score >= 40:
            return 'low'
        else:
            return 'very_low'
    
    def _combine_matching_details(self, enhanced_job: Dict[str, Any], 
                                 semantic_job: Dict[str, Any], 
                                 smart_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine les détails de matching de tous les algorithmes
        """
        combined_details = {}
        
        # Catégories de détails à combiner
        detail_categories = ['skills', 'location', 'contract', 'salary', 'experience']
        
        for category in detail_categories:
            scores = []
            
            # Collecte des scores de chaque algorithme
            if enhanced_job and 'matching_details' in enhanced_job:
                enhanced_score = enhanced_job['matching_details'].get(category, 0)
                if enhanced_score > 0:
                    scores.append(enhanced_score)
            
            if semantic_job and 'matching_details' in semantic_job:
                semantic_score = semantic_job['matching_details'].get(category, 0)
                if semantic_score > 0:
                    scores.append(semantic_score)
            
            if smart_job and 'matching_details' in smart_job:
                smart_score = smart_job['matching_details'].get(category, 0)
                if smart_score > 0:
                    scores.append(smart_score)
            
            # Calcul du score combiné
            if scores:
                # Moyenne pondérée par la confiance
                combined_score = sum(scores) / len(scores)
                
                # Bonus si plusieurs algorithmes sont d'accord
                if len(scores) >= 2:
                    avg = sum(scores) / len(scores)
                    variance = sum((s - avg) ** 2 for s in scores) / len(scores)
                    if variance < 25:  # Consensus
                        combined_score = min(100, combined_score + 2)
                
                combined_details[category] = int(combined_score)
            else:
                combined_details[category] = 0
        
        return combined_details
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme Hybrid
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Combine intelligemment plusieurs algorithmes pour une précision maximale',
            'strengths': [
                'Précision maximale',
                'Analyse de consensus',
                'Niveau de confiance',
                'Robustesse aux erreurs'
            ],
            'best_for': 'Matching critique nécessitant une précision maximale',
            'performance': 'Low (exécute 3 algorithmes)',
            'accuracy': 'Maximum',
            'combining_algorithms': list(self.algorithm_weights.keys()),
            'algorithm_weights': self.algorithm_weights,
            'confidence_thresholds': self.confidence_thresholds
        }
