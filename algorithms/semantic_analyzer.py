#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algorithme d'analyse sémantique pour SuperSmartMatch

Cet algorithme se concentre sur l'analyse sémantique des compétences
"""

import logging
from typing import Dict, List, Any, Optional
from .base_algorithm import BaseMatchingAlgorithm
from config.settings import AlgorithmConfig

logger = logging.getLogger(__name__)

class SemanticAnalyzerAlgorithm(BaseMatchingAlgorithm):
    """
    Algorithme Semantic Analyzer - Focus sur l'analyse sémantique des compétences
    """
    
    def __init__(self):
        super().__init__("SemanticAnalyzer")
        self.config = AlgorithmConfig.SEMANTIC_CONFIG
        
        # Dictionnaire étendu de compétences sémantiques
        self.skill_taxonomy = {
            "programming_languages": {
                "python": {
                    "synonyms": ["python", "py"],
                    "related": ["django", "flask", "fastapi", "pandas", "numpy"],
                    "level": "language",
                    "similarity": 1.0
                },
                "javascript": {
                    "synonyms": ["javascript", "js", "ecmascript"],
                    "related": ["react", "vue", "angular", "node.js", "typescript"],
                    "level": "language",
                    "similarity": 1.0
                },
                "java": {
                    "synonyms": ["java"],
                    "related": ["spring", "hibernate", "maven", "gradle"],
                    "level": "language",
                    "similarity": 1.0
                }
            },
            "frameworks": {
                "react": {
                    "synonyms": ["react", "reactjs", "react.js"],
                    "related": ["javascript", "jsx", "redux", "next.js"],
                    "level": "framework",
                    "similarity": 0.9
                },
                "django": {
                    "synonyms": ["django"],
                    "related": ["python", "drf", "orm"],
                    "level": "framework",
                    "similarity": 0.9
                },
                "spring": {
                    "synonyms": ["spring", "spring boot"],
                    "related": ["java", "hibernate", "mvc"],
                    "level": "framework",
                    "similarity": 0.9
                }
            },
            "databases": {
                "postgresql": {
                    "synonyms": ["postgresql", "postgres", "psql"],
                    "related": ["sql", "database", "rdbms"],
                    "level": "database",
                    "similarity": 0.8
                },
                "mysql": {
                    "synonyms": ["mysql"],
                    "related": ["sql", "database", "rdbms"],
                    "level": "database",
                    "similarity": 0.8
                },
                "mongodb": {
                    "synonyms": ["mongodb", "mongo"],
                    "related": ["nosql", "database", "document"],
                    "level": "database",
                    "similarity": 0.7
                }
            },
            "tools": {
                "git": {
                    "synonyms": ["git"],
                    "related": ["github", "gitlab", "version control"],
                    "level": "tool",
                    "similarity": 0.8
                },
                "docker": {
                    "synonyms": ["docker"],
                    "related": ["containers", "kubernetes", "devops"],
                    "level": "tool",
                    "similarity": 0.8
                }
            }
        }
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les matches avec focus sur l'analyse sémantique
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        candidate_skills = self._normalize_skills(candidate_data.get('competences', []))
        
        for job in jobs_data:
            job_skills = self._normalize_skills(job.get('competences', []))
            
            # Score sémantique des compétences (pondération élevée)
            semantic_score = self._calculate_semantic_similarity(candidate_skills, job_skills)
            
            # Scores supplémentaires (pondération plus faible)
            location_score = self._simple_location_match(candidate_data, job)
            contract_score = self._simple_contract_match(candidate_data, job)
            experience_score = self._simple_experience_match(candidate_data, job)
            
            # Pondération focalisée sur les compétences
            total_score = (
                semantic_score * 0.70 +  # Focus principal
                experience_score * 0.15 +
                location_score * 0.10 +
                contract_score * 0.05
            )
            
            # Formatage du résultat
            job_result = job.copy()
            job_result['matching_score'] = self.normalize_score(total_score)
            job_result['algorithm'] = f"{self.name}_v{self.version}"
            job_result['semantic_details'] = {
                'skill_matches': self._get_skill_matches(candidate_skills, job_skills),
                'semantic_score': self.normalize_score(semantic_score),
                'skill_coverage': self._calculate_skill_coverage(candidate_skills, job_skills)
            }
            job_result['matching_details'] = {
                'skills': self.normalize_score(semantic_score),
                'experience': self.normalize_score(experience_score),
                'location': self.normalize_score(location_score),
                'contract': self.normalize_score(contract_score)
            }
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _normalize_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Normalise et enrichit la liste des compétences
        """
        normalized = []
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            
            # Recherche dans la taxonomie
            skill_info = self._find_skill_in_taxonomy(skill_lower)
            
            if skill_info:
                normalized.append({
                    'original': skill,
                    'normalized': skill_info['canonical'],
                    'category': skill_info['category'],
                    'level': skill_info['level'],
                    'related': skill_info['related'],
                    'similarity_base': skill_info['similarity']
                })
            else:
                # Compétence inconnue
                normalized.append({
                    'original': skill,
                    'normalized': skill_lower,
                    'category': 'unknown',
                    'level': 'unknown',
                    'related': [],
                    'similarity_base': 1.0
                })
        
        return normalized
    
    def _find_skill_in_taxonomy(self, skill: str) -> Optional[Dict[str, Any]]:
        """
        Trouve une compétence dans la taxonomie
        """
        for category, skills_group in self.skill_taxonomy.items():
            for canonical_skill, skill_data in skills_group.items():
                # Vérification des synonymes
                if skill in skill_data['synonyms']:
                    return {
                        'canonical': canonical_skill,
                        'category': category,
                        'level': skill_data['level'],
                        'related': skill_data['related'],
                        'similarity': skill_data['similarity']
                    }
                
                # Vérification des compétences liées
                if skill in skill_data['related']:
                    return {
                        'canonical': skill,
                        'category': category,
                        'level': 'related',
                        'related': [canonical_skill],
                        'similarity': skill_data['similarity'] * 0.8
                    }
        
        return None
    
    def _calculate_semantic_similarity(self, candidate_skills: List[Dict[str, Any]], 
                                      job_skills: List[Dict[str, Any]]) -> float:
        """
        Calcule la similarité sémantique entre les compétences
        """
        if not job_skills:
            return 0.5
        
        if not candidate_skills:
            return 0.1
        
        total_score = 0
        max_possible_score = len(job_skills)
        
        for job_skill in job_skills:
            best_match_score = 0
            
            for candidate_skill in candidate_skills:
                similarity = self._calculate_skill_similarity(candidate_skill, job_skill)
                best_match_score = max(best_match_score, similarity)
            
            total_score += best_match_score
        
        base_score = total_score / max_possible_score
        
        # Bonus pour diversité des compétences
        if len(candidate_skills) > len(job_skills):
            diversity_bonus = min(0.15, (len(candidate_skills) - len(job_skills)) * 0.03)
            base_score += diversity_bonus
        
        # Bonus pour compétences de même catégorie
        category_bonus = self._calculate_category_bonus(candidate_skills, job_skills)
        base_score += category_bonus
        
        return min(1.0, base_score)
    
    def _calculate_skill_similarity(self, candidate_skill: Dict[str, Any], 
                                   job_skill: Dict[str, Any]) -> float:
        """
        Calcule la similarité entre deux compétences
        """
        # Correspondance exacte
        if candidate_skill['normalized'] == job_skill['normalized']:
            return 1.0
        
        # Compétences liées dans la même catégorie
        if (candidate_skill['category'] == job_skill['category'] and 
            candidate_skill['category'] != 'unknown'):
            
            # Vérifier les relations
            if job_skill['normalized'] in candidate_skill['related']:
                return candidate_skill['similarity_base'] * 0.8
            
            if candidate_skill['normalized'] in job_skill['related']:
                return job_skill['similarity_base'] * 0.8
            
            # Compétences de même catégorie
            return 0.4
        
        # Similarité textuelle pour compétences inconnues
        if (candidate_skill['category'] == 'unknown' or 
            job_skill['category'] == 'unknown'):
            return self._calculate_textual_similarity(
                candidate_skill['normalized'], 
                job_skill['normalized']
            )
        
        return 0.0
    
    def _calculate_textual_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calcule la similarité textuelle entre deux compétences
        """
        # Inclusion mutuelle
        if len(skill1) > 3 and skill1 in skill2:
            return 0.6
        
        if len(skill2) > 3 and skill2 in skill1:
            return 0.6
        
        # Calcul de distance de Levenshtein simplifié
        if len(skill1) > 4 and len(skill2) > 4:
            # Préfixes/suffixes communs
            if skill1[:3] == skill2[:3] or skill1[-3:] == skill2[-3:]:
                return 0.3
        
        return 0.0
    
    def _calculate_category_bonus(self, candidate_skills: List[Dict[str, Any]], 
                                 job_skills: List[Dict[str, Any]]) -> float:
        """
        Calcule un bonus basé sur la diversité des catégories
        """
        candidate_categories = set(skill['category'] for skill in candidate_skills)
        job_categories = set(skill['category'] for skill in job_skills)
        
        common_categories = candidate_categories.intersection(job_categories)
        
        if len(job_categories) > 0:
            category_coverage = len(common_categories) / len(job_categories)
            return category_coverage * 0.1  # Bonus jusqu'à 10%
        
        return 0.0
    
    def _get_skill_matches(self, candidate_skills: List[Dict[str, Any]], 
                          job_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retourne les détails des correspondances de compétences
        """
        matches = []
        
        for job_skill in job_skills:
            best_match = None
            best_score = 0
            
            for candidate_skill in candidate_skills:
                score = self._calculate_skill_similarity(candidate_skill, job_skill)
                if score > best_score:
                    best_score = score
                    best_match = candidate_skill
            
            matches.append({
                'job_skill': job_skill['original'],
                'candidate_skill': best_match['original'] if best_match else None,
                'similarity_score': self.normalize_score(best_score),
                'match_type': self._get_match_type(best_score)
            })
        
        return matches
    
    def _get_match_type(self, score: float) -> str:
        """
        Détermine le type de correspondance
        """
        if score >= 0.9:
            return 'exact'
        elif score >= 0.7:
            return 'semantic'
        elif score >= 0.4:
            return 'related'
        elif score > 0:
            return 'partial'
        else:
            return 'none'
    
    def _calculate_skill_coverage(self, candidate_skills: List[Dict[str, Any]], 
                                 job_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule la couverture des compétences
        """
        if not job_skills:
            return {'coverage_percent': 0, 'missing_skills': [], 'extra_skills': []}
        
        covered_skills = 0
        missing_skills = []
        
        for job_skill in job_skills:
            best_score = 0
            for candidate_skill in candidate_skills:
                score = self._calculate_skill_similarity(candidate_skill, job_skill)
                best_score = max(best_score, score)
            
            if best_score >= self.config['similarity_threshold']:
                covered_skills += 1
            else:
                missing_skills.append(job_skill['original'])
        
        # Compétences supplémentaires du candidat
        candidate_skill_names = set(skill['normalized'] for skill in candidate_skills)
        job_skill_names = set(skill['normalized'] for skill in job_skills)
        extra_skills = list(candidate_skill_names - job_skill_names)
        
        return {
            'coverage_percent': int((covered_skills / len(job_skills)) * 100),
            'missing_skills': missing_skills,
            'extra_skills': extra_skills
        }
    
    def _simple_location_match(self, candidate: Dict[str, Any], 
                              job: Dict[str, Any]) -> float:
        """
        Calcul simplifié de localisation
        """
        candidate_loc = candidate.get('adresse', '').lower()
        job_loc = job.get('localisation', '').lower()
        
        if 'remote' in job_loc or 'télétravail' in job_loc:
            return 1.0
        
        if candidate_loc and job_loc:
            if any(city in candidate_loc and city in job_loc 
                   for city in ['paris', 'lyon', 'marseille']):
                return 1.0
        
        return 0.6
    
    def _simple_contract_match(self, candidate: Dict[str, Any], 
                              job: Dict[str, Any]) -> float:
        """
        Calcul simplifié de contrat
        """
        preferred = candidate.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '').lower()
        
        if not preferred or not job_contract:
            return 0.7
        
        for pref in preferred:
            if pref.lower() in job_contract or job_contract in pref.lower():
                return 1.0
        
        return 0.4
    
    def _simple_experience_match(self, candidate: Dict[str, Any], 
                                job: Dict[str, Any]) -> float:
        """
        Calcul simplifié d'expérience
        """
        candidate_exp = candidate.get('annees_experience', 0)
        job_exp_str = job.get('experience', '').lower()
        
        if not job_exp_str:
            return 0.8
        
        if 'junior' in job_exp_str and candidate_exp <= 3:
            return 1.0
        elif 'senior' in job_exp_str and candidate_exp >= 5:
            return 1.0
        elif 'confirmé' in job_exp_str and 3 <= candidate_exp <= 7:
            return 1.0
        
        return 0.6
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme Semantic
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Analyse sémantique avancée des compétences techniques',
            'strengths': [
                'Reconnaissance des compétences liées',
                'Taxonomie étendue des technologies',
                'Analyse de la couverture des compétences',
                'Détection des compétences manquantes'
            ],
            'best_for': 'Postes techniques avec compétences spécifiques',
            'performance': 'Medium',
            'accuracy': 'Very High',
            'focus': 'Skills (70% weighting)',
            'taxonomy_categories': list(self.skill_taxonomy.keys()),
            'similarity_threshold': self.config['similarity_threshold']
        }
