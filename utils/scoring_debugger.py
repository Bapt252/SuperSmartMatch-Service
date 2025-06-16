#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scoring Debugger - Diagnostic et correction du problème de scoring V2.1

Ce module identifie pourquoi le score Zachary vs Juridique reste à 79%
malgré la matrice de compatibilité à 15%.

Auteur: SuperSmartMatch V2.1 Debug Suite
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from utils.sector_analyzer import SectorAnalyzer
from algorithms.enhanced_matching_v2 import EnhancedMatchingV2Algorithm

logger = logging.getLogger(__name__)

class ScoringDebugger:
    """
    Debugger avancé pour identifier les problèmes de scoring
    """
    
    def __init__(self):
        self.sector_analyzer = SectorAnalyzer()
        self.enhanced_v2 = EnhancedMatchingV2Algorithm()
        
    def debug_zachary_case(self, zachary_cv: Dict[str, Any], 
                          juridique_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Debug complet du cas Zachary vs Juridique
        
        Returns:
            Rapport détaillé avec toutes les étapes de calcul
        """
        print("🔍 DEBUGGING ZACHARY VS JURIDIQUE")
        print("=" * 50)
        
        debug_report = {
            'case': 'Zachary (Commercial Junior) vs Assistant Juridique',
            'target_score': '≤ 25%',
            'steps': {},
            'issues_found': [],
            'recommendations': []
        }
        
        # ÉTAPE 1 : Analyse sectorielle
        cv_text = self._extract_cv_text(zachary_cv)
        job_text = self._extract_job_text(juridique_job)
        
        print(f"📄 CV Text: {cv_text[:100]}...")
        print(f"💼 Job Text: {job_text[:100]}...")
        
        cv_sector = self.sector_analyzer.detect_sector(cv_text, 'cv')
        job_sector = self.sector_analyzer.detect_sector(job_text, 'job')
        
        debug_report['steps']['sector_detection'] = {
            'cv_sector': cv_sector.primary_sector,
            'cv_confidence': round(cv_sector.confidence, 3),
            'cv_keywords': cv_sector.detected_keywords,
            'job_sector': job_sector.primary_sector,
            'job_confidence': round(job_sector.confidence, 3),
            'job_keywords': job_sector.detected_keywords
        }
        
        print(f"🎯 CV Sector: {cv_sector.primary_sector} (confiance: {cv_sector.confidence:.3f})")
        print(f"🎯 Job Sector: {job_sector.primary_sector} (confiance: {job_sector.confidence:.3f})")
        
        # ÉTAPE 2 : Score de compatibilité sectorielle
        sector_compatibility = self.sector_analyzer.get_compatibility_score(
            cv_sector.primary_sector, job_sector.primary_sector
        )
        
        debug_report['steps']['sector_compatibility'] = {
            'raw_score': sector_compatibility,
            'percentage': round(sector_compatibility * 100, 1),
            'matrix_lookup': f"({cv_sector.primary_sector}, {job_sector.primary_sector})"
        }
        
        print(f"🔗 Compatibilité sectorielle: {sector_compatibility:.3f} ({sector_compatibility*100:.1f}%)")
        
        if sector_compatibility > 0.25:
            debug_report['issues_found'].append({
                'type': 'sector_compatibility_too_high',
                'current': sector_compatibility,
                'expected': '≤ 0.25',
                'impact': 'Score final trop élevé à cause de la compatibilité sectorielle'
            })
        
        # ÉTAPE 3 : Calcul détaillé des composants
        components = self._calculate_all_components(
            zachary_cv, juridique_job, cv_sector, job_sector, sector_compatibility
        )
        
        debug_report['steps']['score_components'] = components
        
        print("\n📊 DÉCOMPOSITION DU SCORE:")
        for component, details in components.items():
            percentage = details['weighted_score'] * 100
            print(f"  {component}: {details['raw_score']:.3f} × {details['weight']} = {percentage:.1f}%")
        
        # ÉTAPE 4 : Score final et analyse
        final_score = sum(comp['weighted_score'] for comp in components.values())
        final_percentage = final_score * 100
        
        debug_report['steps']['final_calculation'] = {
            'raw_final_score': final_score,
            'final_percentage': round(final_percentage, 1),
            'target_percentage': 25,
            'deviation': round(final_percentage - 25, 1)
        }
        
        print(f"\n🎯 SCORE FINAL: {final_percentage:.1f}%")
        
        if final_percentage > 30:
            debug_report['issues_found'].append({
                'type': 'final_score_too_high',
                'current': final_percentage,
                'expected': '≤ 25%',
                'impact': 'Objectif non atteint'
            })
        
        # ÉTAPE 5 : Test avec Enhanced V2.1 complet
        print(f"\n🚀 Test avec Enhanced V2.1 complet...")
        enhanced_results = self.enhanced_v2.calculate_matches(zachary_cv, [juridique_job])
        
        if enhanced_results:
            enhanced_score = enhanced_results[0]['matching_score']
            debug_report['steps']['enhanced_v2_result'] = {
                'score': enhanced_score,
                'blocking_factors': len(enhanced_results[0].get('blocking_factors', [])),
                'has_sector_analysis': 'sector_analysis' in enhanced_results[0]
            }
            
            print(f"Enhanced V2.1 Score: {enhanced_score}%")
            
            if enhanced_score > 30:
                debug_report['issues_found'].append({
                    'type': 'enhanced_algorithm_score_too_high',
                    'current': enhanced_score,
                    'expected': '≤ 25%',
                    'impact': 'Algorithme Enhanced V2.1 ne fonctionne pas comme attendu'
                })
        
        # ÉTAPE 6 : Génération des recommandations
        debug_report['recommendations'] = self._generate_fix_recommendations(debug_report)
        
        return debug_report
    
    def _extract_cv_text(self, cv_data: Dict[str, Any]) -> str:
        """Extrait le texte du CV pour analyse"""
        text_parts = []
        
        if 'competences' in cv_data:
            text_parts.extend(cv_data['competences'])
        
        if 'missions' in cv_data:
            text_parts.extend(cv_data['missions'])
        
        if 'titre_poste' in cv_data:
            text_parts.append(cv_data['titre_poste'])
        
        return ' '.join(text_parts)
    
    def _extract_job_text(self, job_data: Dict[str, Any]) -> str:
        """Extrait le texte de l'offre d'emploi pour analyse"""
        text_parts = []
        
        if 'titre' in job_data:
            text_parts.append(job_data['titre'])
        
        if 'competences' in job_data:
            text_parts.extend(job_data['competences'])
        
        if 'missions' in job_data:
            text_parts.extend(job_data['missions'])
        
        if 'description' in job_data:
            text_parts.append(job_data['description'])
        
        return ' '.join(text_parts)
    
    def _calculate_all_components(self, cv_data: Dict[str, Any], job_data: Dict[str, Any],
                                 cv_sector: Any, job_sector: Any, 
                                 sector_compatibility: float) -> Dict[str, Dict[str, float]]:
        """Calcule tous les composants du score avec détails"""
        
        # Utiliser les poids de l'Enhanced V2.1
        weights = self.enhanced_v2.base_weights
        
        # 1. Compatibilité sectorielle
        sector_component = {
            'raw_score': sector_compatibility,
            'weight': weights['sector_compatibility'],
            'weighted_score': sector_compatibility * weights['sector_compatibility']
        }
        
        # 2. Pertinence de l'expérience
        experience_relevance = self.enhanced_v2._calculate_experience_relevance(
            cv_data, cv_sector, job_sector, sector_compatibility
        )
        experience_component = {
            'raw_score': experience_relevance,
            'weight': weights['experience_relevance'],
            'weighted_score': experience_relevance * weights['experience_relevance']
        }
        
        # 3. Correspondance des compétences
        skills_match = self.enhanced_v2._calculate_skills_match(
            cv_data.get('competences', []),
            job_data.get('competences', [])
        )
        skills_component = {
            'raw_score': skills_match,
            'weight': weights['skills_match'],
            'weighted_score': skills_match * weights['skills_match']
        }
        
        # 4. Localisation (simplifié)
        location_match = 1.0 if cv_data.get('adresse', '').lower() == job_data.get('localisation', '').lower() else 0.6
        location_component = {
            'raw_score': location_match,
            'weight': weights['location_match'],
            'weighted_score': location_match * weights['location_match']
        }
        
        # 5. Contrat (simplifié)
        contract_match = 1.0  # Assume CDI-CDI match
        contract_component = {
            'raw_score': contract_match,
            'weight': weights['contract_match'],
            'weighted_score': contract_match * weights['contract_match']
        }
        
        return {
            'sector_compatibility': sector_component,
            'experience_relevance': experience_component,
            'skills_match': skills_component,
            'location_match': location_component,
            'contract_match': contract_component
        }
    
    def _generate_fix_recommendations(self, debug_report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère des recommandations de correction basées sur le debug"""
        recommendations = []
        
        for issue in debug_report['issues_found']:
            if issue['type'] == 'sector_compatibility_too_high':
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'Réduire le score de compatibilité commercial → juridique',
                    'implementation': 'Modifier utils/sector_analyzer.py ligne ~180',
                    'code': "('commercial', 'juridique'): 0.10,  # Réduire de 0.15 à 0.10"
                })
            
            elif issue['type'] == 'final_score_too_high':
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'Implémenter pondération adaptative pour secteurs incompatibles',
                    'implementation': 'Ajouter adaptive_weights() dans enhanced_matching_v2.py',
                    'code': 'Augmenter poids sectoriel à 60% pour incompatibilités critiques'
                })
            
            elif issue['type'] == 'enhanced_algorithm_score_too_high':
                recommendations.append({
                    'priority': 'CRITICAL',
                    'action': 'Debug l\'algorithme Enhanced V2.1 complet',
                    'implementation': 'Vérifier _calculate_enhanced_match() méthode',
                    'code': 'Tracer chaque étape de calcul dans la méthode'
                })
        
        # Recommandations générales
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Ajouter des tests automatisés pour le cas Zachary',
            'implementation': 'Étendre test_v2_1_validation.py',
            'code': 'assert zachary_juridique_score <= 25'
        })
        
        return recommendations
    
    def run_comprehensive_debug(self) -> Dict[str, Any]:
        """Lance un debug complet avec le cas Zachary réel"""
        
        # Données Zachary exactes du problème
        zachary_data = {
            "competences": [
                "Prospection commerciale",
                "Relation client", 
                "Négociation",
                "CRM",
                "Téléprospection",
                "Business development"
            ],
            "missions": [
                "Développement du portefeuille client",
                "Prospection de nouveaux clients",
                "Négociation commerciale",
                "Suivi relation client",
                "Présentation produits"
            ],
            "titre_poste": "Assistant commercial",
            "annees_experience": 1,
            "adresse": "Paris",
            "contrats_recherches": ["CDI"]
        }
        
        juridique_data = {
            "id": "assistant_juridique_1",
            "titre": "Assistant juridique",
            "competences": [
                "Droit",
                "Rédaction juridique", 
                "Veille juridique",
                "Code civil",
                "Contrats",
                "Contentieux"
            ],
            "missions": [
                "Rédaction d'actes juridiques",
                "Veille réglementaire", 
                "Assistance aux avocats",
                "Gestion des dossiers contentieux"
            ],
            "description": "Poste d'assistant juridique en cabinet d'avocats spécialisé",
            "localisation": "Paris",
            "type_contrat": "CDI",
            "secteur": "Juridique"
        }
        
        print("🚀 LANCEMENT DU DEBUG COMPLET ZACHARY")
        print("=" * 60)
        
        debug_result = self.debug_zachary_case(zachary_data, juridique_data)
        
        print("\n📋 RAPPORT DE DEBUG")
        print("=" * 60)
        print(json.dumps(debug_result, indent=2, ensure_ascii=False))
        
        print(f"\n🎯 RÉSUMÉ:")
        print(f"Issues trouvées: {len(debug_result['issues_found'])}")
        print(f"Recommandations: {len(debug_result['recommendations'])}")
        
        if debug_result['issues_found']:
            print(f"\n⚠️ ACTIONS REQUISES:")
            for i, rec in enumerate(debug_result['recommendations'], 1):
                print(f"{i}. [{rec['priority']}] {rec['action']}")
        else:
            print(f"\n✅ Aucun problème détecté - Score attendu atteint!")
        
        return debug_result

if __name__ == '__main__':
    """Script de debug standalone"""
    debugger = ScoringDebugger()
    debugger.run_comprehensive_debug()
