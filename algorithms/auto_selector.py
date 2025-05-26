#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteur de sélection automatique d'algorithme pour SuperSmartMatch

Ce moteur analyse le profil candidat et sélectionne l'algorithme optimal
"""

import logging
from typing import Dict, List, Any
from config.settings import AlgorithmConfig

logger = logging.getLogger(__name__)

class AutoSelectorEngine:
    """
    Moteur de sélection automatique de l'algorithme optimal
    """
    
    def __init__(self):
        self.selection_rules = AlgorithmConfig.AUTO_SELECTION_RULES
        
        # Matrice de décision
        self.decision_matrix = {
            'algorithm_performance': {
                'smart-match': {
                    'speed': 7,
                    'accuracy': 8,
                    'geo_precision': 10,
                    'skill_matching': 6
                },
                'enhanced': {
                    'speed': 8,
                    'accuracy': 9,
                    'geo_precision': 7,
                    'skill_matching': 8
                },
                'semantic': {
                    'speed': 6,
                    'accuracy': 9,
                    'geo_precision': 5,
                    'skill_matching': 10
                },
                'hybrid': {
                    'speed': 4,
                    'accuracy': 10,
                    'geo_precision': 8,
                    'skill_matching': 9
                }
            }
        }
    
    def select_optimal_algorithm(self, candidate_data: Dict[str, Any], 
                               jobs_data: List[Dict[str, Any]]) -> str:
        """
        Sélectionne l'algorithme optimal basé sur le profil candidat et les offres
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            
        Returns:
            Nom de l'algorithme optimal
        """
        try:
            # Analyse du contexte
            context = self._analyze_context(candidate_data, jobs_data)
            
            # Application des règles de sélection
            selected_algorithm = self._apply_selection_rules(context)
            
            logger.info(
                f"Auto-sélection: {selected_algorithm} "
                f"(contexte: {context['primary_factor']})"
            )
            
            return selected_algorithm
            
        except Exception as e:
            logger.error(f"Erreur dans auto-sélection: {e}")
            return 'enhanced'  # Fallback par défaut
    
    def _analyze_context(self, candidate_data: Dict[str, Any], 
                        jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse le contexte pour déterminer l'algorithme optimal
        """
        context = {
            'candidate_experience': candidate_data.get('annees_experience', 0),
            'candidate_skills_count': len(candidate_data.get('competences', [])),
            'job_count': len(jobs_data),
            'avg_job_skills': self._calculate_avg_job_skills(jobs_data),
            'geo_sensitive': self._is_geo_sensitive(candidate_data, jobs_data),
            'skill_intensive': self._is_skill_intensive(jobs_data),
            'high_precision_needed': len(jobs_data) > 50,
            'performance_priority': len(jobs_data) < 10
        }
        
        # Détermination du facteur principal
        context['primary_factor'] = self._determine_primary_factor(context)
        
        return context
    
    def _calculate_avg_job_skills(self, jobs_data: List[Dict[str, Any]]) -> float:
        """
        Calcule le nombre moyen de compétences par offre
        """
        if not jobs_data:
            return 0
        
        total_skills = sum(len(job.get('competences', [])) for job in jobs_data)
        return total_skills / len(jobs_data)
    
    def _is_geo_sensitive(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> bool:
        """
        Détermine si la géolocalisation est un facteur critique
        """
        # Vérification des préférences de mobilité
        mobility = candidate_data.get('mobilite', '').lower()
        if mobility in ['presentiel', 'sur site']:
            return True
        
        # Vérification du temps de trajet souhaité
        max_commute = candidate_data.get('temps_trajet_max', 60)
        if max_commute < 45:
            return True
        
        # Vérification de la diversité géographique des offres
        locations = [job.get('localisation', '').lower() for job in jobs_data]
        unique_cities = set()
        for loc in locations:
            if 'paris' in loc:
                unique_cities.add('paris')
            elif 'lyon' in loc:
                unique_cities.add('lyon')
            elif 'marseille' in loc:
                unique_cities.add('marseille')
            elif 'remote' not in loc:
                unique_cities.add('other')
        
        return len(unique_cities) > 2
    
    def _is_skill_intensive(self, jobs_data: List[Dict[str, Any]]) -> bool:
        """
        Détermine si les offres sont intensives en compétences
        """
        if not jobs_data:
            return False
        
        # Seuil de compétences par offre
        high_skill_jobs = sum(
            1 for job in jobs_data 
            if len(job.get('competences', [])) > 5
        )
        
        return (high_skill_jobs / len(jobs_data)) > 0.6
    
    def _determine_primary_factor(self, context: Dict[str, Any]) -> str:
        """
        Détermine le facteur principal pour la sélection
        """
        experience = context['candidate_experience']
        job_count = context['job_count']
        
        # Facteur d'expérience
        if experience <= 2:
            return 'junior_profile'
        elif experience >= 7:
            return 'senior_profile'
        
        # Facteur de géolocalisation
        if context['geo_sensitive']:
            return 'geo_sensitive'
        
        # Facteur de compétences
        if context['skill_intensive']:
            return 'skill_intensive'
        
        # Facteur de précision
        if context['high_precision_needed']:
            return 'high_precision'
        
        # Facteur de performance
        if context['performance_priority']:
            return 'performance_priority'
        
        return 'balanced'
    
    def _apply_selection_rules(self, context: Dict[str, Any]) -> str:
        """
        Applique les règles de sélection basées sur le contexte
        """
        primary_factor = context['primary_factor']
        experience = context['candidate_experience']
        job_count = context['job_count']
        
        # Règles basées sur l'expérience
        if primary_factor == 'junior_profile':
            return 'enhanced'  # Pondération adaptée aux juniors
        
        if primary_factor == 'senior_profile':
            if context['skill_intensive']:
                return 'semantic'  # Focus compétences pour seniors
            else:
                return 'enhanced'
        
        # Règles basées sur la géolocalisation
        if primary_factor == 'geo_sensitive':
            return 'smart-match'  # Optimisé pour la géolocalisation
        
        # Règles basées sur les compétences
        if primary_factor == 'skill_intensive':
            return 'semantic'  # Analyse sémantique avancée
        
        # Règles basées sur la précision
        if primary_factor == 'high_precision':
            return 'hybrid'  # Précision maximale
        
        # Règles basées sur la performance
        if primary_factor == 'performance_priority':
            return 'enhanced'  # Bon compromis vitesse/précision
        
        # Cas par défaut - équilibré
        if job_count > 20:
            return 'enhanced'  # Équilibré pour volume moyen
        else:
            return 'semantic'  # Précision pour petit volume
    
    def get_selection_explanation(self, candidate_data: Dict[str, Any], 
                                 jobs_data: List[Dict[str, Any]], 
                                 selected_algorithm: str) -> Dict[str, Any]:
        """
        Fournit une explication de la sélection d'algorithme
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            selected_algorithm: Algorithme sélectionné
            
        Returns:
            Dictionnaire avec l'explication détaillée
        """
        context = self._analyze_context(candidate_data, jobs_data)
        
        explanations = {
            'enhanced': {
                'junior_profile': 'Pondération adaptée aux profils juniors',
                'balanced': 'Meilleur compromis précision/performance',
                'performance_priority': 'Optimisé pour la rapidité'
            },
            'semantic': {
                'skill_intensive': 'Analyse sémantique avancée des compétences',
                'senior_profile': 'Matching fin pour profils expérimentés',
                'balanced': 'Précision élevée pour volume réduit'
            },
            'smart-match': {
                'geo_sensitive': 'Optimisé pour la géolocalisation précise'
            },
            'hybrid': {
                'high_precision': 'Précision maximale pour volume important'
            }
        }
        
        primary_factor = context['primary_factor']
        explanation = explanations.get(selected_algorithm, {}).get(
            primary_factor, 
            'Sélection basée sur l\'analyse du contexte'
        )
        
        return {
            'selected_algorithm': selected_algorithm,
            'primary_factor': primary_factor,
            'explanation': explanation,
            'context_analysis': context,
            'confidence': self._calculate_selection_confidence(context, selected_algorithm)
        }
    
    def _calculate_selection_confidence(self, context: Dict[str, Any], 
                                       selected_algorithm: str) -> float:
        """
        Calcule la confiance dans la sélection d'algorithme
        """
        base_confidence = 0.8
        
        # Facteurs qui augmentent la confiance
        if context['primary_factor'] in ['geo_sensitive', 'skill_intensive']:
            base_confidence += 0.1  # Facteur clair
        
        if context['job_count'] > 10:
            base_confidence += 0.05  # Plus de données
        
        # Facteurs qui diminuent la confiance
        if context['primary_factor'] == 'balanced':
            base_confidence -= 0.1  # Moins de facteurs discriminants
        
        return min(1.0, max(0.5, base_confidence))
    
    def get_available_algorithms(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des algorithmes disponibles avec leurs caractéristiques
        """
        algorithms = []
        
        for algo_name, performance in self.decision_matrix['algorithm_performance'].items():
            algorithms.append({
                'name': algo_name,
                'performance_scores': performance,
                'recommended_for': self._get_algorithm_recommendations(algo_name)
            })
        
        return algorithms
    
    def _get_algorithm_recommendations(self, algorithm_name: str) -> List[str]:
        """
        Retourne les recommandations d'usage pour un algorithme
        """
        recommendations = {
            'smart-match': [
                'Candidats sensibles à la localisation',
                'Préférences de mobilité limitée',
                'Offres géographiquement dispersées'
            ],
            'enhanced': [
                'Profils équilibrés',
                'Candidats juniors à confirmés',
                'Volume moyen d\'offres (10-50)'
            ],
            'semantic': [
                'Postes techniques spécialisés',
                'Candidats seniors',
                'Compétences nombreuses et variées'
            ],
            'hybrid': [
                'Matching critique',
                'Volume important d\'offres (50+)',
                'Besoin de précision maximale'
            ]
        }
        
        return recommendations.get(algorithm_name, [])
