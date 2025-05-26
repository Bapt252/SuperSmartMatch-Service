#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptation de l'Enhanced Matching Engine pour SuperSmartMatch

Cet algorithme intègre votre Enhanced Matching avec pondération adaptative
"""

import logging
from typing import Dict, List, Any
from .base_algorithm import BaseMatchingAlgorithm
from config.settings import AlgorithmConfig

logger = logging.getLogger(__name__)

class EnhancedMatchingAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme Enhanced Matching - Pondération adaptative selon expérience
    """
    
    def __init__(self):
        super().__init__("Enhanced")
        self.weights_config = AlgorithmConfig.ENHANCED_WEIGHTS
        
        # Dictionnaire de compétences sémantiques
        self.skill_groups = {
            "python_ecosystem": {
                "core": ["Python"],
                "web_frameworks": ["Django", "FastAPI", "Flask"],
                "data_science": ["Pandas", "NumPy", "Matplotlib"],
                "similarity": 0.8
            },
            "javascript_ecosystem": {
                "core": ["JavaScript", "TypeScript"],
                "frontend": ["React", "Vue.js", "Angular"],
                "backend": ["Node.js", "Express"],
                "similarity": 0.8
            },
            "databases": {
                "sql": ["PostgreSQL", "MySQL", "SQLite"],
                "nosql": ["MongoDB", "Redis", "Cassandra"],
                "similarity": 0.6
            }
        }
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les matches avec l'algorithme Enhanced
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        candidate_experience = candidate_data.get('annees_experience', 0)
        
        # Sélection de la pondération adaptative
        weights = self._get_adaptive_weights(candidate_experience)
        
        for job in jobs_data:
            # Calcul des scores avec algorithme amélioré
            skills_score = self._calculate_enhanced_skills_score(candidate_data, job)
            location_score = self._calculate_enhanced_location_score(candidate_data, job)
            contract_score = self._calculate_enhanced_contract_score(candidate_data, job)
            salary_score = self._calculate_enhanced_salary_score(candidate_data, job)
            experience_score = self._calculate_enhanced_experience_score(candidate_data, job)
            date_score = self._calculate_enhanced_availability_score(candidate_data, job)
            
            # Score global avec pondération adaptative
            total_score = (
                skills_score * weights['skills'] +
                location_score * weights['location'] +
                contract_score * weights['contract'] +
                salary_score * weights['salary'] +
                experience_score * weights['experience'] +
                date_score * weights['date']
            )
            
            # Formatage du résultat
            job_result = job.copy()
            job_result['matching_score'] = self.normalize_score(total_score)
            job_result['algorithm'] = f"{self.name}_v{self.version}"
            job_result['adaptive_weights'] = weights
            job_result['matching_details'] = {
                'skills': self.normalize_score(skills_score),
                'location': self.normalize_score(location_score),
                'contract': self.normalize_score(contract_score),
                'salary': self.normalize_score(salary_score),
                'experience': self.normalize_score(experience_score),
                'date': self.normalize_score(date_score)
            }
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _get_adaptive_weights(self, experience: int) -> Dict[str, float]:
        """
        Retourne les pondérations adaptatives selon l'expérience
        """
        if experience >= 7:
            return self.weights_config['senior']
        elif experience >= 3:
            return self.weights_config['confirmed']
        else:
            return self.weights_config['junior']
    
    def _calculate_enhanced_skills_score(self, candidate: Dict[str, Any], 
                                        job: Dict[str, Any]) -> float:
        """
        Calcul amélioré du score de compétences avec matching sémantique
        """
        cv_skills = [skill.lower().strip() for skill in candidate.get('competences', [])]
        job_skills = [skill.lower().strip() for skill in job.get('competences', [])]
        
        if not job_skills:
            return 0.5
        
        if not cv_skills:
            return 0.1
        
        total_score = 0
        max_possible_score = len(job_skills)
        
        for job_skill in job_skills:
            best_match_score = 0
            
            # 1. Correspondance exacte
            if job_skill in cv_skills:
                best_match_score = 1.0
            else:
                # 2. Matching sémantique
                for group_name, group_data in self.skill_groups.items():
                    job_skill_found = False
                    cv_skill_found = False
                    
                    # Vérifier si la compétence du job est dans ce groupe
                    for category, skills in group_data.items():
                        if category != 'similarity' and isinstance(skills, list):
                            if any(s.lower() in job_skill for s in skills) or job_skill in [s.lower() for s in skills]:
                                job_skill_found = True
                                break
                    
                    if job_skill_found:
                        # Vérifier si le candidat a une compétence du même groupe
                        for category, skills in group_data.items():
                            if category != 'similarity' and isinstance(skills, list):
                                for cv_skill in cv_skills:
                                    if any(s.lower() in cv_skill for s in skills) or cv_skill in [s.lower() for s in skills]:
                                        cv_skill_found = True
                                        best_match_score = max(best_match_score, group_data.get('similarity', 0.5))
                                        break
                                if cv_skill_found:
                                    break
                    
                    if cv_skill_found:
                        break
                
                # 3. Matching partiel
                if best_match_score == 0:
                    for cv_skill in cv_skills:
                        if len(job_skill) > 3 and job_skill in cv_skill:
                            best_match_score = max(best_match_score, 0.3)
                        elif len(cv_skill) > 3 and cv_skill in job_skill:
                            best_match_score = max(best_match_score, 0.3)
            
            total_score += best_match_score
        
        # Score final avec bonus
        final_score = total_score / max_possible_score
        
        # Bonus pour candidats avec plus de compétences
        if len(cv_skills) > len(job_skills):
            bonus = min(0.1, (len(cv_skills) - len(job_skills)) * 0.02)
            final_score = min(1.0, final_score + bonus)
        
        return final_score
    
    def _calculate_enhanced_location_score(self, candidate: Dict[str, Any], 
                                          job: Dict[str, Any]) -> float:
        """
        Calcul amélioré du score de localisation par zones intelligentes
        """
        candidate_address = candidate.get('adresse', '').lower().strip()
        job_address = job.get('localisation', '').lower().strip()
        
        if not candidate_address or not job_address:
            return 0.6
        
        # Zones géographiques intelligentes
        location_zones = {
            "paris": {
                "keywords": ["paris", "ile-de-france", "idf", "75"],
                "score": 1.0
            },
            "lyon": {
                "keywords": ["lyon", "rhone", "69"],
                "score": 0.9
            },
            "remote": {
                "keywords": ["remote", "télétravail", "distance"],
                "score": 1.0
            }
        }
        
        # Détection de zone du candidat
        candidate_zone = None
        for zone, zone_data in location_zones.items():
            if any(keyword in candidate_address for keyword in zone_data['keywords']):
                candidate_zone = zone
                break
        
        # Détection de zone du job
        job_zone = None
        for zone, zone_data in location_zones.items():
            if any(keyword in job_address for keyword in zone_data['keywords']):
                job_zone = zone
                break
        
        # Calcul du score
        if job_zone == "remote":
            return 1.0
        elif candidate_zone == job_zone and candidate_zone is not None:
            return 1.0
        elif candidate_zone == "paris" and job_zone in ["lyon"]:
            return 0.4
        elif job_zone is not None:
            return 0.6
        else:
            return 0.3
    
    def _calculate_enhanced_contract_score(self, candidate: Dict[str, Any], 
                                          job: Dict[str, Any]) -> float:
        """
        Calcul amélioré du score de type de contrat
        """
        preferred_contracts = candidate.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '').lower().strip()
        
        if not preferred_contracts or not job_contract:
            return 0.7
        
        # Synonymes pour types de contrats
        contract_synonyms = {
            "cdi": ["cdi", "permanent", "indefinite"],
            "cdd": ["cdd", "temporary", "fixed-term"],
            "freelance": ["freelance", "consultant", "contractor"]
        }
        
        # Normalisation
        normalized_job_contract = None
        for contract_type, synonyms in contract_synonyms.items():
            if any(synonym in job_contract for synonym in synonyms):
                normalized_job_contract = contract_type
                break
        
        normalized_preferences = []
        for pref in preferred_contracts:
            pref_lower = pref.lower().strip()
            for contract_type, synonyms in contract_synonyms.items():
                if any(synonym in pref_lower for synonym in synonyms):
                    normalized_preferences.append(contract_type)
                    break
        
        # Scoring
        if normalized_job_contract in normalized_preferences:
            return 1.0
        elif normalized_job_contract == "cdi" and "cdd" in normalized_preferences:
            return 0.8
        elif normalized_job_contract == "freelance" and any(x in normalized_preferences for x in ["cdd", "cdi"]):
            return 0.6
        else:
            return 0.3
    
    def _calculate_enhanced_salary_score(self, candidate: Dict[str, Any], 
                                        job: Dict[str, Any]) -> float:
        """
        Calcul amélioré du score de salaire
        """
        min_salary = candidate.get('salaire_souhaite', 0)
        job_salary_str = job.get('salaire', '')
        
        if not min_salary:
            return 0.8
        
        if not job_salary_str:
            return 0.6
        
        try:
            import re
            
            # Nettoyage et extraction
            salary_clean = job_salary_str.replace(' ', '').replace('k', '000').replace('K', '000').replace('€', '')
            numbers = re.findall(r'\d+', salary_clean)
            
            if len(numbers) >= 2:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[1])
            elif len(numbers) == 1:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[0]) * 1.2
            else:
                return 0.6
            
            # Scoring amélioré
            if job_min_salary >= min_salary:
                if job_min_salary >= min_salary * 1.2:
                    return 1.0
                else:
                    return 0.9
            elif job_max_salary >= min_salary:
                coverage = (job_max_salary - min_salary) / (job_max_salary - job_min_salary)
                return 0.6 + 0.3 * coverage
            else:
                ratio = job_max_salary / min_salary
                return max(0.2, min(0.5, ratio))
        
        except Exception as e:
            logger.warning(f"Erreur calcul salaire: {e}")
            return 0.6
    
    def _calculate_enhanced_experience_score(self, candidate: Dict[str, Any], 
                                            job: Dict[str, Any]) -> float:
        """
        Calcul amélioré du score d'expérience
        """
        candidate_experience = candidate.get('annees_experience', 0)
        job_experience_str = job.get('experience', '')
        
        if not job_experience_str:
            return 0.8
        
        if candidate_experience == 0:
            return 0.4
        
        try:
            import re
            
            numbers = re.findall(r'\d+', job_experience_str)
            job_experience_str_lower = job_experience_str.lower()
            
            # Détection par mots-clés
            if "débutant" in job_experience_str_lower or "junior" in job_experience_str_lower:
                job_min_exp, job_max_exp = 0, 2
            elif "senior" in job_experience_str_lower:
                job_min_exp, job_max_exp = 5, 15
            elif "confirmé" in job_experience_str_lower:
                job_min_exp, job_max_exp = 3, 7
            elif len(numbers) >= 2:
                job_min_exp, job_max_exp = int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                job_min_exp = int(numbers[0])
                job_max_exp = job_min_exp + 3
            else:
                return 0.7
            
            # Scoring intelligent
            if job_min_exp <= candidate_experience <= job_max_exp:
                return 1.0
            elif candidate_experience < job_min_exp:
                if job_min_exp - candidate_experience <= 1:
                    return 0.8
                elif job_min_exp - candidate_experience <= 2:
                    return 0.6
                else:
                    return 0.3
            else:
                excess = candidate_experience - job_max_exp
                if excess <= 2:
                    return 0.9
                elif excess <= 5:
                    return 0.7
                else:
                    return 0.5
        
        except Exception as e:
            logger.warning(f"Erreur calcul expérience: {e}")
            return 0.7
    
    def _calculate_enhanced_availability_score(self, candidate: Dict[str, Any], 
                                              job: Dict[str, Any]) -> float:
        """
        Calcul amélioré du score de disponibilité
        """
        try:
            availability_date_str = candidate.get('disponibilite', '')
            job_start_date_str = job.get('date_debut', '')
            
            if not availability_date_str or not job_start_date_str:
                return 0.8
            
            # Parsing simplifié des dates
            if availability_date_str.lower() in ['immediate', 'immédiat', 'asap']:
                return 1.0
            
            # Pour l'instant, retourner un score neutre
            # TODO: Implémenter parsing de dates complet si nécessaire
            return 0.8
        
        except Exception as e:
            logger.warning(f"Erreur calcul disponibilité: {e}")
            return 0.7
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme Enhanced
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Algorithme avec pondération adaptative selon expérience',
            'strengths': [
                'Pondération adaptative',
                'Matching sémantique des compétences',
                'Gestion des synonymes',
                'Scoring graduel (pas de 0% brutal)'
            ],
            'best_for': 'Matching équilibré et intelligent',
            'performance': 'High',
            'accuracy': 'Very High',
            'adaptive_weights': {
                'junior': self.weights_config['junior'],
                'confirmed': self.weights_config['confirmed'],
                'senior': self.weights_config['senior']
            }
        }
