#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Matching Algorithm - Classe de base pour tous les algorithmes de matching
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseMatchingAlgorithm(ABC):
    """
    Classe de base abstraite pour tous les algorithmes de matching
    """
    
    def __init__(self, name: str):
        self.name = name
        self.version = "1.0.0"
    
    @abstractmethod
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Méthode abstraite pour calculer les matches
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            
        Returns:
            Liste des matches avec scores et détails
        """
        pass
    
    def validate_input(self, candidate_data: Dict[str, Any], 
                      jobs_data: List[Dict[str, Any]]) -> bool:
        """
        Valide les données d'entrée
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            
        Returns:
            True si les données sont valides, False sinon
        """
        if not isinstance(candidate_data, dict):
            return False
        
        if not isinstance(jobs_data, list) or len(jobs_data) == 0:
            return False
        
        # Vérifications basiques
        required_candidate_fields = ['competences']  # Minimum requis
        for field in required_candidate_fields:
            if field not in candidate_data:
                candidate_data[field] = []  # Valeur par défaut
        
        # Vérification des jobs
        for job in jobs_data:
            if not isinstance(job, dict):
                return False
        
        return True
    
    def normalize_score(self, score: float) -> float:
        """
        Normalise un score entre 0 et 100
        
        Args:
            score: Score à normaliser (entre 0.0 et 1.0)
            
        Returns:
            Score normalisé entre 0 et 100
        """
        return max(0.0, min(100.0, score * 100))
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme
        
        Returns:
            Dictionnaire avec les infos de l'algorithme
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Algorithme de matching de base',
            'type': 'base_algorithm'
        }
    
    def preprocess_candidate_data(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prétraite les données du candidat
        
        Args:
            candidate_data: Données brutes du candidat
            
        Returns:
            Données prétraitées
        """
        processed_data = candidate_data.copy()
        
        # Normalisation des compétences
        if 'competences' in processed_data:
            competences = processed_data['competences']
            if isinstance(competences, str):
                processed_data['competences'] = [competences]
            elif not isinstance(competences, list):
                processed_data['competences'] = []
        else:
            processed_data['competences'] = []
        
        # Normalisation des années d'expérience
        if 'annees_experience' not in processed_data:
            processed_data['annees_experience'] = 0
        elif not isinstance(processed_data['annees_experience'], (int, float)):
            processed_data['annees_experience'] = 0
        
        # Normalisation du titre
        if 'titre_poste' not in processed_data:
            processed_data['titre_poste'] = ''
        
        return processed_data
    
    def preprocess_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prétraite les données d'une offre d'emploi
        
        Args:
            job_data: Données brutes de l'offre
            
        Returns:
            Données prétraitées
        """
        processed_data = job_data.copy()
        
        # Normalisation des compétences requises
        if 'competences' in processed_data:
            competences = processed_data['competences']
            if isinstance(competences, str):
                processed_data['competences'] = [competences]
            elif not isinstance(competences, list):
                processed_data['competences'] = []
        else:
            processed_data['competences'] = []
        
        # Normalisation du titre
        if 'titre' not in processed_data:
            processed_data['titre'] = ''
        
        # ID unique si pas présent
        if 'id' not in processed_data:
            processed_data['id'] = f"job_{hash(str(processed_data))}"
        
        return processed_data
    
    def calculate_basic_similarity(self, list1: List[str], list2: List[str]) -> float:
        """
        Calcule une similarité basique entre deux listes
        
        Args:
            list1: Première liste (ex: compétences candidat)
            list2: Deuxième liste (ex: compétences requises)
            
        Returns:
            Score de similarité entre 0.0 et 1.0
        """
        if not list2:  # Pas de critères = score neutre
            return 0.7
        
        if not list1:  # Candidat sans compétences
            return 0.0
        
        # Normalisation en minuscules
        normalized_list1 = [item.lower().strip() for item in list1]
        normalized_list2 = [item.lower().strip() for item in list2]
        
        # Correspondances exactes
        exact_matches = len(set(normalized_list1) & set(normalized_list2))
        
        # Score basé sur les correspondances
        similarity = exact_matches / len(normalized_list2)
        
        return min(1.0, similarity)
    
    def format_match_result(self, job_data: Dict[str, Any], 
                           score: float, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Formate le résultat d'un match
        
        Args:
            job_data: Données de l'offre d'emploi
            score: Score de matching (0.0 à 1.0)
            details: Détails optionnels du matching
            
        Returns:
            Résultat formaté
        """
        result = job_data.copy()
        result.update({
            'matching_score': self.normalize_score(score),
            'algorithm': f"{self.name}_v{self.version}",
            'matching_details': details or {},
            'recommendations': []
        })
        
        return result
