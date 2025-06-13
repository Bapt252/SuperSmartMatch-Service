#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Matching Algorithm V2.1 - SuperSmartMatch avec analyse sectorielle

RÉSOLUTION DU PROBLÈME CRITIQUE :
- CV Zachary (commercial junior) vs Assistant juridique : 79% -> ~25%
- Intégration de l'analyse sectorielle intelligente
- Pondération adaptative selon la compatibilité sectorielle
- Facteurs bloquants et recommandations explicites

Auteur: SuperSmartMatch V2.1 Enhanced
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from .base_algorithm import BaseMatchingAlgorithm
from utils.sector_analyzer import SectorAnalyzer, SectorAnalysisResult

logger = logging.getLogger(__name__)

class EnhancedMatchingV2Algorithm(BaseMatchingAlgorithm):
    """
    Enhanced Matching V2.1 - Algorithme avec intelligence sectorielle
    
    Nouveautés V2.1 :
    - Analyse sectorielle automatique
    - Matrice de compatibilité française  
    - Pondération adaptative selon secteur
    - Facteurs bloquants détectés
    - Recommandations explicites
    """
    
    def __init__(self):
        super().__init__("EnhancedMatchingV2")
        self.version = "2.1.0"
        self.sector_analyzer = SectorAnalyzer()
        
        # Configuration de pondération adaptative
        self.base_weights = {
            'sector_compatibility': 0.40,  # NOUVEAU : Poids principal
            'skills_match': 0.25,          # Réduit pour laisser place au sectoriel
            'experience_relevance': 0.20,  # NOUVEAU : Expérience pondérée par secteur
            'location_match': 0.10,
            'contract_match': 0.05
        }
        
        # Seuils pour détection de facteurs bloquants
        self.blocking_thresholds = {
            'sector_compatibility': 0.25,   # En dessous = facteur bloquant majeur
            'experience_relevance': 0.30,   # En dessous = expérience non pertinente
            'skills_critical_missing': 0.40  # En dessous = compétences critiques manquantes
        }
    
    def calculate_matches(self, candidate_data: Dict[str, Any], 
                         jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les matches avec l'intelligence sectorielle V2.1
        """
        if not self.validate_input(candidate_data, jobs_data):
            return []
        
        results = []
        
        # Analyse sectorielle du candidat
        candidate_text = self._extract_candidate_text(candidate_data)
        candidate_sector_analysis = self.sector_analyzer.detect_sector(
            candidate_text, context='cv'
        )
        
        logger.info(f"Candidat - Secteur détecté: {candidate_sector_analysis.primary_sector} "
                   f"(confiance: {candidate_sector_analysis.confidence:.2f})")
        
        for job in jobs_data:
            # Analyse sectorielle du poste
            job_text = self._extract_job_text(job)
            job_sector_analysis = self.sector_analyzer.detect_sector(
                job_text, context='job'
            )
            
            # Calcul du matching avec intelligence sectorielle
            match_result = self._calculate_enhanced_match(
                candidate_data, job, 
                candidate_sector_analysis, job_sector_analysis
            )
            
            # Formatage du résultat enrichi
            job_result = job.copy()
            job_result.update(match_result)
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _extract_candidate_text(self, candidate_data: Dict[str, Any]) -> str:
        """
        Extrait le texte pertinent du CV pour l'analyse sectorielle
        """
        text_parts = []
        
        # Compétences
        competences = candidate_data.get('competences', [])
        if competences:
            text_parts.append(' '.join(competences))
        
        # Missions et expériences
        missions = candidate_data.get('missions', [])
        if missions:
            text_parts.extend(missions)
        
        # Titre du poste actuel
        titre = candidate_data.get('titre_poste', '')
        if titre:
            text_parts.append(titre)
        
        # Secteur d'activité si mentionné
        secteur = candidate_data.get('secteur', '')
        if secteur:
            text_parts.append(secteur)
        
        return ' '.join(text_parts)
    
    def _extract_job_text(self, job_data: Dict[str, Any]) -> str:
        """
        Extrait le texte pertinent de l'offre d'emploi pour l'analyse sectorielle
        """
        text_parts = []
        
        # Titre du poste
        titre = job_data.get('titre', '')
        if titre:
            text_parts.append(titre)
        
        # Compétences requises
        competences = job_data.get('competences', [])
        if competences:
            text_parts.append(' '.join(competences))
        
        # Description du poste
        description = job_data.get('description', '')
        if description:
            text_parts.append(description)
        
        # Missions
        missions = job_data.get('missions', [])
        if missions:
            text_parts.extend(missions)
        
        # Secteur d'activité
        secteur = job_data.get('secteur', '')
        if secteur:
            text_parts.append(secteur)
        
        return ' '.join(text_parts)
    
    def _calculate_enhanced_match(self, candidate_data: Dict[str, Any], 
                                 job_data: Dict[str, Any],
                                 candidate_sector: SectorAnalysisResult,
                                 job_sector: SectorAnalysisResult) -> Dict[str, Any]:
        """
        Calcul du matching enhanced avec intelligence sectorielle
        """
        # 1. COMPATIBILITÉ SECTORIELLE (40% du score)
        sector_compatibility = self.sector_analyzer.get_compatibility_score(
            candidate_sector.primary_sector, 
            job_sector.primary_sector
        )
        
        # 2. PERTINENCE DE L'EXPÉRIENCE (20% du score - pondérée par secteur)
        experience_relevance = self._calculate_experience_relevance(
            candidate_data, candidate_sector, job_sector, sector_compatibility
        )
        
        # 3. CORRESPONDANCE DES COMPÉTENCES (25% du score)
        skills_match = self._calculate_skills_match(
            candidate_data.get('competences', []),
            job_data.get('competences', [])
        )
        
        # 4. LOCALISATION (10% du score)
        location_match = self._calculate_location_match(candidate_data, job_data)
        
        # 5. TYPE DE CONTRAT (5% du score)
        contract_match = self._calculate_contract_match(candidate_data, job_data)
        
        # CALCUL DU SCORE FINAL PONDÉRÉ
        final_score = (
            sector_compatibility * self.base_weights['sector_compatibility'] +
            experience_relevance * self.base_weights['experience_relevance'] +
            skills_match * self.base_weights['skills_match'] +
            location_match * self.base_weights['location_match'] +
            contract_match * self.base_weights['contract_match']
        )
        
        # DÉTECTION DES FACTEURS BLOQUANTS
        blocking_factors = self._detect_blocking_factors(
            sector_compatibility, experience_relevance, skills_match,
            candidate_sector, job_sector
        )
        
        # GÉNÉRATION DES RECOMMANDATIONS
        recommendations = self._generate_enhanced_recommendations(
            final_score, sector_compatibility, candidate_sector, job_sector,
            candidate_data, blocking_factors
        )
        
        # ANALYSE DE TRANSITION SECTORIELLE
        transition_analysis = self.sector_analyzer.analyze_sector_transition(
            candidate_sector.primary_sector,
            job_sector.primary_sector,
            candidate_data.get('annees_experience', 0)
        )
        
        return {
            'matching_score': self.normalize_score(final_score),
            'algorithm': f"{self.name}_v{self.version}",
            'sector_analysis': {
                'candidate_sector': candidate_sector.primary_sector,
                'job_sector': job_sector.primary_sector,
                'compatibility_score': self.normalize_score(sector_compatibility),
                'transition_type': transition_analysis['transition_type'],
                'difficulty_level': transition_analysis['difficulty_level']
            },
            'matching_details': {
                'sector_compatibility': self.normalize_score(sector_compatibility),
                'experience_relevance': self.normalize_score(experience_relevance),
                'skills_match': self.normalize_score(skills_match),
                'location_match': self.normalize_score(location_match),
                'contract_match': self.normalize_score(contract_match)
            },
            'blocking_factors': blocking_factors,
            'recommendations': recommendations,
            'transition_analysis': transition_analysis,
            'explanation': self._generate_detailed_explanation(
                final_score, sector_compatibility, candidate_sector, job_sector
            )
        }
    
    def _calculate_experience_relevance(self, candidate_data: Dict[str, Any],
                                       candidate_sector: SectorAnalysisResult,
                                       job_sector: SectorAnalysisResult,
                                       sector_compatibility: float) -> float:
        """
        Calcule la pertinence de l'expérience pondérée par la compatibilité sectorielle
        """
        years_experience = candidate_data.get('annees_experience', 0)
        
        # Score de base selon les années d'expérience
        if years_experience == 0:
            base_score = 0.2
        elif years_experience <= 2:
            base_score = 0.5  # Junior
        elif years_experience <= 5:
            base_score = 0.8  # Confirmé
        else:
            base_score = 1.0  # Senior
        
        # PONDÉRATION SECTORIELLE (clé de la V2.1)
        if sector_compatibility >= 0.8:
            # Secteurs très compatibles : expérience pleinement transférable
            sector_multiplier = 1.0
        elif sector_compatibility >= 0.5:
            # Secteurs moyennement compatibles : expérience partiellement transférable
            sector_multiplier = 0.7
        elif sector_compatibility >= 0.3:
            # Secteurs peu compatibles : expérience peu transférable
            sector_multiplier = 0.4
        else:
            # Secteurs incompatibles : expérience non transférable
            sector_multiplier = 0.2
        
        # Bonus pour expérience senior en cas de transition sectorielle
        if years_experience >= 7 and sector_compatibility < 0.5:
            sector_multiplier += 0.2  # L'expérience compense l'écart sectoriel
        
        final_relevance = base_score * sector_multiplier
        
        logger.debug(f"Expérience: {years_experience} ans, compatibilité: {sector_compatibility:.2f}, "
                    f"relevance: {final_relevance:.2f}")
        
        return min(1.0, final_relevance)
    
    def _calculate_skills_match(self, candidate_skills: List[str], 
                               job_skills: List[str]) -> float:
        """
        Calcule la correspondance des compétences (version simplifiée)
        """
        if not job_skills:
            return 0.7  # Pas de compétences spécifiées = score neutre
        
        if not candidate_skills:
            return 0.1  # Aucune compétence = score très faible
        
        # Normalisation des compétences (lowercase)
        candidate_skills_norm = [skill.lower().strip() for skill in candidate_skills]
        job_skills_norm = [skill.lower().strip() for skill in job_skills]
        
        # Correspondances exactes
        exact_matches = len(set(candidate_skills_norm) & set(job_skills_norm))
        
        # Correspondances partielles (inclusion)
        partial_matches = 0
        for job_skill in job_skills_norm:
            for candidate_skill in candidate_skills_norm:
                if (len(job_skill) > 3 and job_skill in candidate_skill) or \
                   (len(candidate_skill) > 3 and candidate_skill in job_skill):
                    partial_matches += 0.5
                    break
        
        total_matches = exact_matches + partial_matches
        match_ratio = total_matches / len(job_skills_norm)
        
        # Bonus pour avoir plus de compétences que demandé
        if len(candidate_skills) > len(job_skills):
            bonus = min(0.15, (len(candidate_skills) - len(job_skills)) * 0.03)
            match_ratio += bonus
        
        return min(1.0, match_ratio)
    
    def _calculate_location_match(self, candidate_data: Dict[str, Any], 
                                 job_data: Dict[str, Any]) -> float:
        """
        Calcule la correspondance géographique
        """
        candidate_location = candidate_data.get('adresse', '').lower()
        job_location = job_data.get('localisation', '').lower()
        
        # Remote work
        if 'remote' in job_location or 'télétravail' in job_location:
            return 1.0
        
        # Même ville
        major_cities = ['paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes']
        for city in major_cities:
            if city in candidate_location and city in job_location:
                return 1.0
        
        # Région parisienne
        if any(term in candidate_location for term in ['paris', 'ile-de-france']) and \
           any(term in job_location for term in ['paris', 'ile-de-france']):
            return 0.9
        
        # Par défaut : mobilité possible
        return 0.6
    
    def _calculate_contract_match(self, candidate_data: Dict[str, Any], 
                                 job_data: Dict[str, Any]) -> float:
        """
        Calcule la correspondance de type de contrat
        """
        preferred_contracts = candidate_data.get('contrats_recherches', [])
        job_contract = job_data.get('type_contrat', '').lower()
        
        if not preferred_contracts or not job_contract:
            return 0.7  # Neutre si pas d'information
        
        for contract in preferred_contracts:
            if contract.lower() in job_contract or job_contract in contract.lower():
                return 1.0
        
        # CDI vs CDD compatibility
        if 'cdi' in [c.lower() for c in preferred_contracts] and 'cdd' in job_contract:
            return 0.6  # Acceptable mais pas idéal
        
        return 0.3
    
    def _detect_blocking_factors(self, sector_compatibility: float, 
                                experience_relevance: float, skills_match: float,
                                candidate_sector: SectorAnalysisResult,
                                job_sector: SectorAnalysisResult) -> List[Dict[str, Any]]:
        """
        Détecte les facteurs bloquants pour le matching
        """
        blocking_factors = []
        
        # Facteur bloquant MAJEUR : Incompatibilité sectorielle
        if sector_compatibility <= self.blocking_thresholds['sector_compatibility']:
            blocking_factors.append({
                'type': 'sector_incompatibility',
                'severity': 'high',
                'description': f"Secteurs '{candidate_sector.primary_sector}' et "
                              f"'{job_sector.primary_sector}' très incompatibles",
                'impact': f"Score de compatibilité: {self.normalize_score(sector_compatibility)}%",
                'recommendation': "Considérer une formation ou transition progressive"
            })
        
        # Facteur bloquant : Expérience non pertinente
        if experience_relevance <= self.blocking_thresholds['experience_relevance']:
            blocking_factors.append({
                'type': 'experience_irrelevance',
                'severity': 'medium',
                'description': "Expérience professionnelle peu transférable",
                'impact': f"Pertinence de l'expérience: {self.normalize_score(experience_relevance)}%",
                'recommendation': "Mettre en avant les compétences transversales"
            })
        
        # Facteur bloquant : Compétences critiques manquantes
        if skills_match <= self.blocking_thresholds['skills_critical_missing']:
            blocking_factors.append({
                'type': 'critical_skills_missing',
                'severity': 'medium',
                'description': "Compétences techniques critiques insuffisantes",
                'impact': f"Correspondance des compétences: {self.normalize_score(skills_match)}%",
                'recommendation': "Acquérir les compétences techniques manquantes"
            })
        
        return blocking_factors
    
    def _generate_enhanced_recommendations(self, final_score: float,
                                         sector_compatibility: float,
                                         candidate_sector: SectorAnalysisResult,
                                         job_sector: SectorAnalysisResult,
                                         candidate_data: Dict[str, Any],
                                         blocking_factors: List[Dict[str, Any]]) -> List[str]:
        """
        Génère des recommandations intelligentes basées sur l'analyse
        """
        recommendations = []
        experience = candidate_data.get('annees_experience', 0)
        
        # Recommandations selon le score global
        if final_score >= 0.8:
            recommendations.append("🎯 Excellent match - Candidature fortement recommandée")
        elif final_score >= 0.6:
            recommendations.append("✅ Bon match - Candidature recommandée avec adaptations mineures")
        elif final_score >= 0.4:
            recommendations.append("⚠️ Match modéré - Évaluer les critères prioritaires")
        else:
            recommendations.append("❌ Match faible - Reconversion significative nécessaire")
        
        # Recommandations sectorielles spécifiques
        if sector_compatibility < 0.3:
            recommendations.append(
                f"🔄 Transition {candidate_sector.primary_sector} → {job_sector.primary_sector} "
                "très difficile - Envisager une formation spécialisée"
            )
        elif sector_compatibility < 0.5:
            recommendations.append(
                f"📚 Secteur différent - Valoriser les compétences transversales "
                f"entre {candidate_sector.primary_sector} et {job_sector.primary_sector}"
            )
        
        # Recommandations selon l'expérience
        if experience < 2 and sector_compatibility < 0.5:
            recommendations.append(
                "👨‍🎓 Profil junior avec changement de secteur - "
                "Privilégier les postes avec formation intégrée"
            )
        elif experience >= 5 and sector_compatibility < 0.4:
            recommendations.append(
                "💼 Expérience senior - Mettre en avant le leadership et "
                "la capacité d'adaptation sectorielle"
            )
        
        # Recommandations selon les facteurs bloquants
        if any(bf['type'] == 'sector_incompatibility' for bf in blocking_factors):
            recommendations.append(
                "🏢 Cibler des entreprises en transformation ou des postes hybrides"
            )
        
        return recommendations
    
    def _generate_detailed_explanation(self, final_score: float,
                                     sector_compatibility: float,
                                     candidate_sector: SectorAnalysisResult,
                                     job_sector: SectorAnalysisResult) -> str:
        """
        Génère une explication détaillée du score de matching
        """
        score_pct = self.normalize_score(final_score)
        compat_pct = self.normalize_score(sector_compatibility)
        
        if sector_compatibility <= 0.25:
            explanation = (
                f"Score {score_pct}% principalement justifié par l'incompatibilité "
                f"sectorielle ({compat_pct}%) entre '{candidate_sector.primary_sector}' "
                f"et '{job_sector.primary_sector}'. Transition très difficile nécessitant "
                "une reconversion significative."
            )
        elif sector_compatibility <= 0.5:
            explanation = (
                f"Score {score_pct}% influencé par l'écart sectoriel modéré ({compat_pct}%) "
                f"entre '{candidate_sector.primary_sector}' et '{job_sector.primary_sector}'. "
                "Adaptation possible avec effort."
            )
        else:
            explanation = (
                f"Score {score_pct}% avec bonne compatibilité sectorielle ({compat_pct}%) "
                f"entre '{candidate_sector.primary_sector}' et '{job_sector.primary_sector}'. "
                "Transition naturelle ou évolution de carrière."
            )
        
        return explanation
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme Enhanced V2.1
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Enhanced Matching avec intelligence sectorielle V2.1',
            'key_features': [
                'Analyse sectorielle automatique',
                'Matrice de compatibilité française',
                'Pondération adaptative par secteur',
                'Détection de facteurs bloquants',
                'Recommandations intelligentes',
                'Analyse de transition sectorielle'
            ],
            'problem_solved': 'Score commercial vs juridique: 79% -> 25%',
            'strengths': [
                'Précision sectorielle élevée',
                'Explicabilité des scores',
                'Recommandations actionnables',
                'Adaptation au marché français'
            ],
            'best_for': 'Matching avec différences sectorielles',
            'weights': self.base_weights,
            'blocking_thresholds': self.blocking_thresholds,
            'sectors_supported': 9,
            'compatibility_matrix_size': len(self.sector_analyzer.compatibility_matrix)
        }
