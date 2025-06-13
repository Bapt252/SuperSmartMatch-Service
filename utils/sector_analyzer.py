#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SectorAnalyzer - Module d'analyse sectorielle pour SuperSmartMatch V2.1

Ce module résout le problème critique identifié :
- CV commercial junior vs poste juridique = 79% -> 25%
- Détection automatique des secteurs
- Matrice de compatibilité sectorielle française
- Facteurs bloquants et recommandations

Auteur: SuperSmartMatch V2.1 Enhanced
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SectorAnalysisResult:
    """Résultat d'analyse sectorielle"""
    primary_sector: str
    confidence: float
    secondary_sectors: List[str]
    detected_keywords: List[str]
    explanation: str

class SectorAnalyzer:
    """
    Analyseur de secteurs d'activité avec matrice de compatibilité française
    """
    
    def __init__(self):
        self.sector_keywords = {
            'commercial': {
                'primary': [
                    'commercial', 'vente', 'business development', 'business developer', 
                    'sales', 'développement commercial', 'chargé de clientèle',
                    'account manager', 'responsable commercial', 'vendeur',
                    'prospection', 'négociation commerciale', 'chiffre d\'affaires'
                ],
                'secondary': [
                    'client', 'clientèle', 'prospect', 'pipeline', 'crm',
                    'fidélisation', 'acquisition', 'relation client'
                ],
                'related_sectors': ['marketing', 'communication']
            },
            'juridique': {
                'primary': [
                    'juridique', 'droit', 'legal', 'avocat', 'juriste', 'notaire',
                    'assistant juridique', 'paralegal', 'contentieux', 'contrat',
                    'compliance', 'réglementation', 'législation'
                ],
                'secondary': [
                    'code civil', 'procédure', 'tribunal', 'litige', 'conseil juridique',
                    'veille juridique', 'rédaction juridique'
                ],
                'related_sectors': ['comptabilité', 'finance']
            },
            'comptabilité': {
                'primary': [
                    'comptabilité', 'comptable', 'accounting', 'finance', 'audit',
                    'contrôle de gestion', 'bilan', 'budget', 'fiscal',
                    'expert-comptable', 'trésorerie', 'gestion financière'
                ],
                'secondary': [
                    'sage', 'erp', 'déclaration', 'tva', 'charges', 'analytique',
                    'consolidation', 'reporting financier'
                ],
                'related_sectors': ['juridique', 'audit']
            },
            'informatique': {
                'primary': [
                    'développeur', 'developer', 'programmeur', 'ingénieur logiciel',
                    'software engineer', 'devops', 'data scientist', 'analyste programmeur',
                    'tech lead', 'architecte logiciel', 'full stack'
                ],
                'secondary': [
                    'python', 'java', 'javascript', 'react', 'angular', 'api',
                    'base de données', 'cloud', 'agile', 'scrum'
                ],
                'related_sectors': ['digital', 'innovation']
            },
            'marketing': {
                'primary': [
                    'marketing', 'communication', 'digital marketing', 'community manager',
                    'chargé de communication', 'chef de produit', 'brand manager',
                    'content manager', 'seo', 'sem'
                ],
                'secondary': [
                    'réseaux sociaux', 'campagne', 'stratégie marketing', 'brand',
                    'événementiel', 'relations publiques'
                ],
                'related_sectors': ['commercial', 'communication']
            },
            'ressources_humaines': {
                'primary': [
                    'ressources humaines', 'rh', 'human resources', 'recrutement',
                    'talent acquisition', 'gestionnaire rh', 'chargé de recrutement',
                    'formation', 'paie', 'administration du personnel'
                ],
                'secondary': [
                    'sirh', 'entretien', 'candidat', 'onboarding', 'performance',
                    'développement rh'
                ],
                'related_sectors': ['management', 'formation']
            },
            'finance': {
                'primary': [
                    'analyste financier', 'contrôleur de gestion', 'auditeur',
                    'risk manager', 'trésorier', 'investment', 'crédit',
                    'banque', 'assurance', 'finance d\'entreprise'
                ],
                'secondary': [
                    'excel', 'modélisation financière', 'risque', 'conformité',
                    'indicateurs financiers', 'rentabilité'
                ],
                'related_sectors': ['comptabilité', 'audit']
            },
            'production': {
                'primary': [
                    'production', 'manufacturing', 'industriel', 'qualité',
                    'lean', 'amélioration continue', 'chef d\'équipe',
                    'responsable production', 'planification'
                ],
                'secondary': [
                    'iso', 'process', 'optimisation', 'rendement', 'maintenance',
                    'logistique', 'supply chain'
                ],
                'related_sectors': ['logistique', 'qualité']
            },
            'management': {
                'primary': [
                    'manager', 'chef d\'équipe', 'directeur', 'responsable',
                    'team lead', 'superviseur', 'coordinateur', 'chef de projet',
                    'management', 'leadership'
                ],
                'secondary': [
                    'équipe', 'coordination', 'pilotage', 'stratégie',
                    'organisation', 'objectifs'
                ],
                'related_sectors': ['ressources_humaines', 'stratégie']
            }
        }
        
        # Matrice de compatibilité sectorielle (score de 0 à 1)
        self.compatibility_matrix = {
            # Commercial - Excellent avec marketing, moyenne avec management
            ('commercial', 'commercial'): 1.0,
            ('commercial', 'marketing'): 0.75,
            ('commercial', 'management'): 0.60,
            ('commercial', 'ressources_humaines'): 0.40,
            ('commercial', 'comptabilité'): 0.25,
            ('commercial', 'juridique'): 0.15,  # ⭐ PROBLÈME RÉSOLU : 79% -> 15%
            ('commercial', 'informatique'): 0.20,
            ('commercial', 'finance'): 0.30,
            ('commercial', 'production'): 0.25,
            
            # Juridique - Excellent avec compliance, faible avec commercial
            ('juridique', 'juridique'): 1.0,
            ('juridique', 'comptabilité'): 0.70,
            ('juridique', 'finance'): 0.65,
            ('juridique', 'ressources_humaines'): 0.55,
            ('juridique', 'management'): 0.45,
            ('juridique', 'commercial'): 0.15,  # ⭐ Réciproque
            ('juridique', 'marketing'): 0.20,
            ('juridique', 'informatique'): 0.25,
            ('juridique', 'production'): 0.20,
            
            # Comptabilité - Synergies fortes avec finance
            ('comptabilité', 'comptabilité'): 1.0,
            ('comptabilité', 'finance'): 0.85,
            ('comptabilité', 'juridique'): 0.70,
            ('comptabilité', 'management'): 0.55,
            ('comptabilité', 'ressources_humaines'): 0.50,
            ('comptabilité', 'production'): 0.40,
            ('comptabilité', 'commercial'): 0.25,
            ('comptabilité', 'marketing'): 0.20,
            ('comptabilité', 'informatique'): 0.35,
            
            # Informatique - Transversale mais spécialisée
            ('informatique', 'informatique'): 1.0,
            ('informatique', 'marketing'): 0.60,  # Digital marketing
            ('informatique', 'finance'): 0.50,   # Fintech
            ('informatique', 'management'): 0.45,
            ('informatique', 'production'): 0.40,
            ('informatique', 'comptabilité'): 0.35,
            ('informatique', 'ressources_humaines'): 0.30,
            ('informatique', 'commercial'): 0.20,
            ('informatique', 'juridique'): 0.25,
            
            # Marketing - Forte synergie avec commercial
            ('marketing', 'marketing'): 1.0,
            ('marketing', 'commercial'): 0.75,
            ('marketing', 'informatique'): 0.60,
            ('marketing', 'management'): 0.55,
            ('marketing', 'ressources_humaines'): 0.40,
            ('marketing', 'finance'): 0.30,
            ('marketing', 'comptabilité'): 0.20,
            ('marketing', 'juridique'): 0.20,
            ('marketing', 'production'): 0.25,
            
            # Ressources Humaines - Transversale managériale
            ('ressources_humaines', 'ressources_humaines'): 1.0,
            ('ressources_humaines', 'management'): 0.75,
            ('ressources_humaines', 'juridique'): 0.55,
            ('ressources_humaines', 'comptabilité'): 0.50,
            ('ressources_humaines', 'commercial'): 0.40,
            ('ressources_humaines', 'marketing'): 0.40,
            ('ressources_humaines', 'finance'): 0.35,
            ('ressources_humaines', 'informatique'): 0.30,
            ('ressources_humaines', 'production'): 0.35,
            
            # Finance - Proche de comptabilité et juridique
            ('finance', 'finance'): 1.0,
            ('finance', 'comptabilité'): 0.85,
            ('finance', 'juridique'): 0.65,
            ('finance', 'management'): 0.60,
            ('finance', 'informatique'): 0.50,
            ('finance', 'ressources_humaines'): 0.35,
            ('finance', 'commercial'): 0.30,
            ('finance', 'production'): 0.35,
            ('finance', 'marketing'): 0.30,
            
            # Production - Spécialisée industrielle
            ('production', 'production'): 1.0,
            ('production', 'management'): 0.65,
            ('production', 'informatique'): 0.40,
            ('production', 'comptabilité'): 0.40,
            ('production', 'finance'): 0.35,
            ('production', 'ressources_humaines'): 0.35,
            ('production', 'commercial'): 0.25,
            ('production', 'marketing'): 0.25,
            ('production', 'juridique'): 0.20,
            
            # Management - Transversale leadership
            ('management', 'management'): 1.0,
            ('management', 'ressources_humaines'): 0.75,
            ('management', 'commercial'): 0.60,
            ('management', 'production'): 0.65,
            ('management', 'finance'): 0.60,
            ('management', 'marketing'): 0.55,
            ('management', 'informatique'): 0.45,
            ('management', 'juridique'): 0.45,
            ('management', 'comptabilité'): 0.55
        }
    
    def detect_sector(self, text: str, context: str = 'general') -> SectorAnalysisResult:
        """
        Détecte le secteur principal d'un texte (CV ou offre d'emploi)
        
        Args:
            text: Texte à analyser (missions, titre, description)
            context: Contexte de l'analyse ('cv' ou 'job' ou 'general')
            
        Returns:
            Résultat détaillé de l'analyse sectorielle
        """
        if not text:
            return SectorAnalysisResult(
                primary_sector='inconnu',
                confidence=0.0,
                secondary_sectors=[],
                detected_keywords=[],
                explanation="Aucun texte fourni pour l'analyse"
            )
        
        # Normalisation du texte
        text_normalized = text.lower()
        
        # Scores par secteur
        sector_scores = {}
        all_detected_keywords = []
        
        for sector, keywords_data in self.sector_keywords.items():
            score = 0
            detected_keywords = []
            
            # Recherche de mots-clés primaires (poids fort)
            for keyword in keywords_data['primary']:
                if keyword.lower() in text_normalized:
                    score += 2.0
                    detected_keywords.append(keyword)
            
            # Recherche de mots-clés secondaires (poids moyen)
            for keyword in keywords_data['secondary']:
                if keyword.lower() in text_normalized:
                    score += 1.0
                    detected_keywords.append(keyword)
            
            # Pondération selon le contexte
            if context == 'cv' and len(detected_keywords) > 0:
                # Bonus pour cohérence sur CV
                score *= 1.2
            elif context == 'job' and len(detected_keywords) > 2:
                # Bonus pour spécificité sur offre d'emploi
                score *= 1.1
            
            sector_scores[sector] = {
                'score': score,
                'keywords': detected_keywords
            }
            all_detected_keywords.extend(detected_keywords)
        
        # Détermination du secteur principal
        if not any(data['score'] > 0 for data in sector_scores.values()):
            return SectorAnalysisResult(
                primary_sector='inconnu',
                confidence=0.0,
                secondary_sectors=[],
                detected_keywords=[],
                explanation="Aucun mot-clé sectoriel détecté"
            )
        
        # Tri par score décroissant
        sorted_sectors = sorted(
            sector_scores.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        primary_sector = sorted_sectors[0][0]
        primary_score = sorted_sectors[0][1]['score']
        
        # Calcul de la confidence
        total_score = sum(data['score'] for data in sector_scores.values())
        confidence = min(1.0, primary_score / max(total_score, 1))
        
        # Secteurs secondaires (score > 20% du principal)
        secondary_threshold = primary_score * 0.2
        secondary_sectors = [
            sector for sector, data in sorted_sectors[1:] 
            if data['score'] >= secondary_threshold
        ]
        
        # Explication
        primary_keywords = sector_scores[primary_sector]['keywords']
        explanation = f"Secteur '{primary_sector}' détecté avec {len(primary_keywords)} indicateurs clés"
        
        return SectorAnalysisResult(
            primary_sector=primary_sector,
            confidence=confidence,
            secondary_sectors=secondary_sectors[:2],  # Maximum 2 secteurs secondaires
            detected_keywords=primary_keywords,
            explanation=explanation
        )
    
    def get_compatibility_score(self, cv_sector: str, job_sector: str) -> float:
        """
        Calcule le score de compatibilité entre deux secteurs
        
        Args:
            cv_sector: Secteur du CV
            job_sector: Secteur de l'offre d'emploi
            
        Returns:
            Score de compatibilité (0.0 à 1.0)
        """
        # Recherche directe dans la matrice
        compatibility = self.compatibility_matrix.get((cv_sector, job_sector))
        
        if compatibility is not None:
            return compatibility
        
        # Recherche inverse
        compatibility = self.compatibility_matrix.get((job_sector, cv_sector))
        
        if compatibility is not None:
            return compatibility
        
        # Secteurs identiques non définis
        if cv_sector == job_sector:
            return 1.0
        
        # Secteur inconnu
        if cv_sector == 'inconnu' or job_sector == 'inconnu':
            return 0.5  # Neutre
        
        # Aucune compatibilité définie
        return 0.3  # Score par défaut bas
    
    def analyze_sector_transition(self, cv_sector: str, job_sector: str, 
                                 candidate_experience: int = 0) -> Dict[str, Any]:
        """
        Analyse une transition sectorielle et génère des recommandations
        
        Args:
            cv_sector: Secteur actuel du candidat
            job_sector: Secteur cible
            candidate_experience: Années d'expérience du candidat
            
        Returns:
            Analyse détaillée de la transition
        """
        compatibility = self.get_compatibility_score(cv_sector, job_sector)
        
        analysis = {
            'transition_type': self._get_transition_type(compatibility),
            'compatibility_score': compatibility,
            'difficulty_level': self._get_difficulty_level(compatibility, candidate_experience),
            'blocking_factors': [],
            'success_factors': [],
            'recommendations': []
        }
        
        # Analyse des facteurs bloquants
        if compatibility < 0.3:
            analysis['blocking_factors'].extend([
                f"Secteurs '{cv_sector}' et '{job_sector}' très éloignés",
                "Compétences métier non transférables",
                "Contexte professionnel différent"
            ])
        
        if candidate_experience < 2 and compatibility < 0.5:
            analysis['blocking_factors'].append(
                "Expérience insuffisante pour compenser l'écart sectoriel"
            )
        
        # Facteurs de réussite
        if candidate_experience >= 5:
            analysis['success_factors'].append(
                "Expérience senior facilite l'adaptation sectorielle"
            )
        
        if compatibility >= 0.5:
            analysis['success_factors'].append(
                "Compétences partiellement transférables"
            )
        
        # Recommandations
        analysis['recommendations'] = self._generate_transition_recommendations(
            cv_sector, job_sector, compatibility, candidate_experience
        )
        
        return analysis
    
    def _get_transition_type(self, compatibility: float) -> str:
        """Détermine le type de transition"""
        if compatibility >= 0.8:
            return "évolution_naturelle"
        elif compatibility >= 0.5:
            return "transition_possible"
        elif compatibility >= 0.3:
            return "reconversion_difficile"
        else:
            return "reconversion_majeure"
    
    def _get_difficulty_level(self, compatibility: float, experience: int) -> str:
        """Évalue la difficulté de la transition"""
        base_difficulty = 1 - compatibility
        
        # Bonus expérience
        experience_bonus = min(0.3, experience * 0.05)
        adjusted_difficulty = max(0, base_difficulty - experience_bonus)
        
        if adjusted_difficulty <= 0.2:
            return "facile"
        elif adjusted_difficulty <= 0.5:
            return "modérée"
        elif adjusted_difficulty <= 0.7:
            return "difficile"
        else:
            return "très_difficile"
    
    def _generate_transition_recommendations(self, cv_sector: str, job_sector: str, 
                                           compatibility: float, experience: int) -> List[str]:
        """Génère des recommandations pour la transition"""
        recommendations = []
        
        if compatibility < 0.3:
            recommendations.extend([
                f"Considérer une formation spécialisée en {job_sector}",
                "Rechercher des postes hybrides combinant les deux secteurs",
                "Acquérir une première expérience via stage ou mission courte"
            ])
        
        elif compatibility < 0.6:
            recommendations.extend([
                "Mettre en avant les compétences transversales",
                f"Valoriser les synergies entre {cv_sector} et {job_sector}",
                "Cibler des entreprises en transformation sectorielle"
            ])
        
        if experience < 3:
            recommendations.append(
                "Privilégier les postes junior avec formation intégrée"
            )
        
        return recommendations
    
    def get_sector_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur les secteurs analysés
        """
        return {
            'available_sectors': list(self.sector_keywords.keys()),
            'compatibility_matrix_size': len(self.compatibility_matrix),
            'algorithm_version': '2.1.0',
            'features': [
                'Détection automatique de secteur',
                'Matrice de compatibilité française',
                'Analyse de transition sectorielle',
                'Recommandations personnalisées'
            ]
        }
