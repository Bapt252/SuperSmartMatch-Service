#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface de base pour tous les algorithmes de matching
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseMatchingAlgorithm(ABC):
    """
    Interface de base que tous les algorithmes doivent implémenter
    """
    
    def __init__(self, name: str):
        self.name = name
        self.version = "1.0.0"
    
    @abstractmethod
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les scores de matching pour un candidat et une liste d'offres
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            
        Returns:
            Liste des offres avec scores de matching
        """
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme
        
        Returns:
            Dictionnaire avec les métadonnées de l'algorithme
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
            True si les données sont valides
        """
        if not isinstance(candidate_data, dict):
            return False
        
        if not isinstance(jobs_data, list):
            return False
        
        # Vérifications basiques
        required_candidate_fields = ['competences']
        for field in required_candidate_fields:
            if field not in candidate_data:
                return False
        
        return True
    
    def normalize_score(self, score: float) -> int:
        """
        Normalise un score float vers un entier 0-100
        
        Args:
            score: Score entre 0 et 1
            
        Returns:
            Score entier entre 0 et 100
        """
        return max(0, min(100, int(score * 100)))
