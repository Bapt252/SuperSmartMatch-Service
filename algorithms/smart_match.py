#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptation de l'algorithme SmartMatch existant pour SuperSmartMatch

Cet algorithme intègre votre SmartMatch bidirectionnel avec géolocalisation
"""

import logging
import googlemaps
from typing import Dict, List, Any, Optional
from .base_algorithm import BaseMatchingAlgorithm
from config.settings import Config, AlgorithmConfig

logger = logging.getLogger(__name__)

class SmartMatchAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme SmartMatch - Bidirectionnel avec géolocalisation
    """
    
    def __init__(self):
        super().__init__("SmartMatch")
        self.config = AlgorithmConfig.SMARTMATCH_CONFIG
        
        # Initialisation Google Maps si disponible
        self.gmaps = None
        if Config.GOOGLE_MAPS_API_KEY:
            try:
                self.gmaps = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
                logger.info("Google Maps initialisé pour SmartMatch")
            except Exception as e:
                logger.warning(f"Impossible d'initialiser Google Maps: {e}")
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les matches avec l'algorithme SmartMatch
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        
        for job in jobs_data:
            # Calcul des différents critères
            skills_score = self._calculate_skills_match(candidate_data, job)
            location_score = self._calculate_location_match(candidate_data, job)
            contract_score = self._calculate_contract_match(candidate_data, job)
            salary_score = self._calculate_salary_match(candidate_data, job)
            experience_score = self._calculate_experience_match(candidate_data, job)
            
            # Score global avec pondération SmartMatch
            total_score = (
                skills_score * 0.35 +
                location_score * 0.25 +
                salary_score * 0.20 +
                contract_score * 0.15 +
                experience_score * 0.05
            )
            
            # Formatage du résultat
            job_result = job.copy()
            job_result['matching_score'] = self.normalize_score(total_score)
            job_result['algorithm'] = self.name
            job_result['matching_details'] = {
                'skills': self.normalize_score(skills_score),
                'location': self.normalize_score(location_score),
                'contract': self.normalize_score(contract_score),
                'salary': self.normalize_score(salary_score),
                'experience': self.normalize_score(experience_score)
            }
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_skills_match(self, candidate: Dict[str, Any], 
                               job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance des compétences
        """
        candidate_skills = set(skill.lower() for skill in candidate.get('competences', []))
        job_skills = set(skill.lower() for skill in job.get('competences', []))
        
        if not job_skills:
            return 0.8  # Score neutre si pas de compétences spécifiées
        
        if not candidate_skills:
            return 0.1  # Score bas si candidat sans compétences
        
        # Correspondance directe
        matches = candidate_skills.intersection(job_skills)
        match_ratio = len(matches) / len(job_skills)
        
        # Bonus si le candidat a plus de compétences
        if len(candidate_skills) > len(job_skills):
            bonus = min(0.1, (len(candidate_skills) - len(job_skills)) * 0.02)
            match_ratio += bonus
        
        return min(1.0, match_ratio)
    
    def _calculate_location_match(self, candidate: Dict[str, Any], 
                                 job: Dict[str, Any]) -> float:
        """
        Calcule le score de localisation avec géolocalisation
        """
        candidate_location = candidate.get('adresse', '').lower()
        job_location = job.get('localisation', '').lower()
        
        if not candidate_location or not job_location:
            return 0.6  # Score neutre
        
        # Vérification des mots-clés de remote
        remote_keywords = ['remote', 'télétravail', 'teletravail', 'distance']
        if any(keyword in job_location for keyword in remote_keywords):
            return 1.0
        
        # Correspondance directe par ville
        if self._same_city(candidate_location, job_location):
            return 1.0
        
        # Calcul de distance avec Google Maps si disponible
        if self.gmaps:
            try:
                distance_score = self._calculate_travel_time_score(
                    candidate_location, job_location
                )
                if distance_score is not None:
                    return distance_score
            except Exception as e:
                logger.warning(f"Erreur calcul distance Google Maps: {e}")
        
        # Fallback: correspondance par région
        return self._calculate_regional_match(candidate_location, job_location)
    
    def _same_city(self, location1: str, location2: str) -> bool:
        """
        Vérifie si deux localisations sont dans la même ville
        """
        cities = {
            'paris': ['paris', '75', 'ile-de-france', 'idf'],
            'lyon': ['lyon', '69', 'rhone'],
            'marseille': ['marseille', '13', 'bouches-du-rhone'],
            'toulouse': ['toulouse', '31', 'haute-garonne'],
            'lille': ['lille', '59', 'nord']
        }
        
        for city, keywords in cities.items():
            if (any(keyword in location1 for keyword in keywords) and 
                any(keyword in location2 for keyword in keywords)):
                return True
        
        return False
    
    def _calculate_travel_time_score(self, origin: str, destination: str) -> Optional[float]:
        """
        Calcule un score basé sur le temps de trajet Google Maps
        """
        try:
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode="transit",
                units="metric"
            )
            
            if (result['rows'] and result['rows'][0]['elements'] and 
                result['rows'][0]['elements'][0]['status'] == 'OK'):
                
                duration = result['rows'][0]['elements'][0]['duration']['value'] / 60  # en minutes
                max_commute = self.config['max_commute_time']
                
                if duration <= max_commute:
                    return 1.0 - (duration / max_commute) * 0.3  # Score entre 0.7 et 1.0
                else:
                    return max(0.2, 0.7 - (duration - max_commute) / max_commute * 0.5)
        
        except Exception as e:
            logger.warning(f"Erreur Google Maps API: {e}")
        
        return None
    
    def _calculate_regional_match(self, location1: str, location2: str) -> float:
        """
        Calcule un score de correspondance régionale
        """
        regions = {
            'ile_de_france': ['paris', '75', '77', '78', '91', '92', '93', '94', '95'],
            'rhone_alpes': ['lyon', '69', '01', '07', '26', '38', '42', '73', '74'],
            'paca': ['marseille', '13', '04', '05', '06', '83', '84']
        }
        
        for region, keywords in regions.items():
            if (any(keyword in location1 for keyword in keywords) and 
                any(keyword in location2 for keyword in keywords)):
                return 0.7
        
        return 0.3
    
    def _calculate_contract_match(self, candidate: Dict[str, Any], 
                                 job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance du type de contrat
        """
        preferred_contracts = candidate.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '').lower()
        
        if not preferred_contracts or not job_contract:
            return 0.7
        
        # Normalisation des types de contrats
        contract_mapping = {
            'cdi': ['cdi', 'permanent', 'indefinite'],
            'cdd': ['cdd', 'temporary', 'fixed-term'],
            'freelance': ['freelance', 'consultant', 'contractor']
        }
        
        for contract_type, synonyms in contract_mapping.items():
            if any(synonym in job_contract for synonym in synonyms):
                job_contract_normalized = contract_type
                break
        else:
            job_contract_normalized = job_contract
        
        # Vérification de correspondance
        for preferred in preferred_contracts:
            preferred_lower = preferred.lower()
            if preferred_lower == job_contract_normalized:
                return 1.0
            elif (preferred_lower == 'cdd' and job_contract_normalized == 'cdi'):
                return 0.8  # CDI acceptable si on cherche CDD
        
        return 0.4
    
    def _calculate_salary_match(self, candidate: Dict[str, Any], 
                               job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance salariale
        """
        expected_salary = candidate.get('salaire_souhaite', 0)
        job_salary_str = job.get('salaire', '')
        
        if not expected_salary:
            return 0.8  # Pas d'exigence = bon score
        
        if not job_salary_str:
            return 0.6  # Salaire non spécifié
        
        try:
            # Extraction des valeurs numériques
            import re
            numbers = re.findall(r'\d+', job_salary_str.replace('k', '000').replace('K', '000'))
            
            if len(numbers) >= 2:
                job_min = int(numbers[0])
                job_max = int(numbers[1])
            elif len(numbers) == 1:
                job_min = int(numbers[0])
                job_max = job_min * 1.2
            else:
                return 0.6
            
            # Scoring
            if job_min >= expected_salary:
                return 1.0
            elif job_max >= expected_salary:
                return 0.8
            else:
                ratio = job_max / expected_salary
                return max(0.2, min(0.6, ratio))
        
        except Exception:
            return 0.6
    
    def _calculate_experience_match(self, candidate: Dict[str, Any], 
                                   job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance d'expérience
        """
        candidate_exp = candidate.get('annees_experience', 0)
        job_exp_str = job.get('experience', '')
        
        if not job_exp_str:
            return 0.8
        
        try:
            import re
            numbers = re.findall(r'\d+', job_exp_str)
            
            if 'junior' in job_exp_str.lower() or 'débutant' in job_exp_str.lower():
                required_min, required_max = 0, 2
            elif 'senior' in job_exp_str.lower():
                required_min, required_max = 5, 15
            elif len(numbers) >= 2:
                required_min, required_max = int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                required_min = int(numbers[0])
                required_max = required_min + 2
            else:
                return 0.7
            
            if required_min <= candidate_exp <= required_max:
                return 1.0
            elif candidate_exp < required_min:
                diff = required_min - candidate_exp
                return max(0.3, 1.0 - diff * 0.2)
            else:
                diff = candidate_exp - required_max
                return max(0.5, 1.0 - diff * 0.1)
        
        except Exception:
            return 0.7
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme SmartMatch
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Algorithme bidirectionnel avec géolocalisation Google Maps',
            'strengths': [
                'Géolocalisation précise',
                'Calcul de temps de trajet réel',
                'Matching bidirectionnel'
            ],
            'best_for': 'Candidats sensibles à la localisation',
            'requires': {
                'google_maps_api': self.gmaps is not None
            },
            'performance': 'Medium',
            'accuracy': 'High'
        }
