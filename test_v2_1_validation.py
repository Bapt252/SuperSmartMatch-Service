#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script SuperSmartMatch V2.1 - Validation du problème critique

Ce script teste la résolution du problème identifié :
- CV Zachary (commercial junior) vs Assistant juridique : 79% -> ~25%

OBJECTIF : Prouver que Enhanced V2.1 résout le problème sectoriel

Auteur: SuperSmartMatch V2.1 Test Suite
"""

import sys
import os
import json
import requests
import time
from typing import Dict, List, Any

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.enhanced_matching_v2 import EnhancedMatchingV2Algorithm
from algorithms.semantic_analyzer import SemanticAnalyzerAlgorithm
from utils.sector_analyzer import SectorAnalyzer

class SuperSmartMatchV2Tester:
    """
    Suite de tests pour valider SuperSmartMatch V2.1
    """
    
    def __init__(self):
        self.enhanced_v2 = EnhancedMatchingV2Algorithm()
        self.semantic = SemanticAnalyzerAlgorithm()
        self.sector_analyzer = SectorAnalyzer()
        
        # Données de test - Cas Zachary
        self.zachary_cv = {
            "competences": [
                "Prospection commerciale",
                "Relation client",
                "Négociation",
                "CRM",
                "Téléprospection",
                "Vente"
            ],
            "missions": [
                "Prospection de nouveaux clients",
                "Développement du portefeuille client",
                "Négociation commerciale",
                "Suivi de la relation client",
                "Présentation de produits"
            ],
            "titre_poste": "Assistant commercial",
            "annees_experience": 1,
            "adresse": "Paris",
            "contrats_recherches": ["CDI"],
            "salaire_souhaite": 30000
        }
        
        # Offres d'emploi de test
        self.test_jobs = [
            {
                "id": "job_juridique_1",
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
                "description": "Poste d'assistant juridique dans un cabinet d'avocats",
                "localisation": "Paris",
                "type_contrat": "CDI",
                "experience": "Junior accepté",
                "secteur": "Juridique"
            },
            {
                "id": "job_commercial_1",
                "titre": "Commercial junior",
                "competences": [
                    "Vente",
                    "Prospection",
                    "Relation client",
                    "CRM",
                    "Négociation commerciale"
                ],
                "missions": [
                    "Développement commercial",
                    "Prospection téléphonique",
                    "Suivi clientèle",
                    "Présentation produits"
                ],
                "description": "Poste de commercial junior dans entreprise BtoB",
                "localisation": "Paris",
                "type_contrat": "CDI",
                "experience": "1-2 ans",
                "secteur": "Commercial"
            },
            {
                "id": "job_comptable_1",
                "titre": "Assistant comptable",
                "competences": [
                    "Comptabilité",
                    "Sage",
                    "Bilan",
                    "TVA",
                    "Déclarations fiscales"
                ],
                "missions": [
                    "Saisie comptable",
                    "Déclarations TVA",
                    "Rapprochements bancaires",
                    "Assistance expert-comptable"
                ],
                "description": "Poste d'assistant comptable en cabinet",
                "localisation": "Paris",
                "type_contrat": "CDI",
                "experience": "Débutant accepté",
                "secteur": "Comptabilité"
            }
        ]
    
    def test_sector_detection(self):
        """
        Test 1 : Vérification de la détection sectorielle
        """
        print("🔍 TEST 1 : DÉTECTION SECTORIELLE")
        print("=" * 50)
        
        # Test CV Zachary
        cv_text = " ".join(self.zachary_cv["missions"] + self.zachary_cv["competences"])
        cv_analysis = self.sector_analyzer.detect_sector(cv_text, 'cv')
        
        print(f"CV Zachary - Secteur détecté: {cv_analysis.primary_sector}")
        print(f"Confiance: {cv_analysis.confidence:.2f}")
        print(f"Mots-clés: {cv_analysis.detected_keywords}")
        print()
        
        # Test offres d'emploi
        for job in self.test_jobs:
            job_text = " ".join([
                job["titre"],
                " ".join(job["competences"]),
                " ".join(job["missions"])
            ])
            job_analysis = self.sector_analyzer.detect_sector(job_text, 'job')
            
            print(f"Job {job['id']} - Secteur: {job_analysis.primary_sector}")
            print(f"Confiance: {job_analysis.confidence:.2f}")
            print()
        
        # Assertions
        assert cv_analysis.primary_sector == 'commercial', f"CV devrait être 'commercial', got '{cv_analysis.primary_sector}'"
        print("✅ Détection sectorielle CV correcte")
        
        return cv_analysis
    
    def test_compatibility_matrix(self):
        """
        Test 2 : Vérification de la matrice de compatibilité
        """
        print("🔗 TEST 2 : MATRICE DE COMPATIBILITÉ")
        print("=" * 50)
        
        test_cases = [
            ('commercial', 'juridique', 'Très faible'),
            ('commercial', 'commercial', 'Parfaite'),
            ('commercial', 'comptabilité', 'Faible'),
            ('juridique', 'comptabilité', 'Bonne'),
        ]
        
        for cv_sector, job_sector, expected in test_cases:
            score = self.sector_analyzer.get_compatibility_score(cv_sector, job_sector)
            print(f"{cv_sector} -> {job_sector}: {score:.2f} ({expected})")
        
        # Assertion critique
        commercial_juridique = self.sector_analyzer.get_compatibility_score('commercial', 'juridique')
        assert commercial_juridique <= 0.25, f"Commercial->Juridique devrait être ≤ 0.25, got {commercial_juridique}"
        print("✅ Matrice de compatibilité correcte")
        
        return commercial_juridique
    
    def test_enhanced_v2_vs_semantic(self):
        """
        Test 3 : Comparaison Enhanced V2.1 vs Semantic (ancien système)
        """
        print("⚔️ TEST 3 : ENHANCED V2.1 VS SEMANTIC")
        print("=" * 50)
        
        # Test avec Enhanced V2.1
        print("🚀 Enhanced V2.1 Results:")
        enhanced_results = self.enhanced_v2.calculate_matches(
            self.zachary_cv, 
            self.test_jobs
        )
        
        for result in enhanced_results:
            print(f"Job {result['id']}: {result['matching_score']}%")
            if 'sector_analysis' in result:
                print(f"  Secteur compatibility: {result['sector_analysis']['compatibility_score']}%")
            if 'blocking_factors' in result and result['blocking_factors']:
                print(f"  Facteurs bloquants: {len(result['blocking_factors'])}")
        print()
        
        # Test avec Semantic (ancien)
        print("🤖 Semantic Analyzer Results:")
        semantic_results = self.semantic.calculate_matches(
            self.zachary_cv, 
            self.test_jobs
        )
        
        for result in semantic_results:
            print(f"Job {result['id']}: {result['matching_score']}%")
        print()
        
        # Analyse des résultats
        enhanced_juridique = next(r for r in enhanced_results if r['id'] == 'job_juridique_1')
        semantic_juridique = next(r for r in semantic_results if r['id'] == 'job_juridique_1')
        
        enhanced_commercial = next(r for r in enhanced_results if r['id'] == 'job_commercial_1')
        semantic_commercial = next(r for r in semantic_results if r['id'] == 'job_commercial_1')
        
        print(f"📊 RÉSULTATS COMPARATIFS:")
        print(f"Juridique - Enhanced V2.1: {enhanced_juridique['matching_score']}% | Semantic: {semantic_juridique['matching_score']}%")
        print(f"Commercial - Enhanced V2.1: {enhanced_commercial['matching_score']}% | Semantic: {semantic_commercial['matching_score']}%")
        
        # Assertions critiques
        assert enhanced_juridique['matching_score'] <= 30, f"Enhanced V2.1 juridique devrait être ≤ 30%, got {enhanced_juridique['matching_score']}%"
        assert enhanced_commercial['matching_score'] >= 70, f"Enhanced V2.1 commercial devrait être ≥ 70%, got {enhanced_commercial['matching_score']}%"
        
        print("✅ Enhanced V2.1 résout le problème sectoriel")
        
        return enhanced_results, semantic_results
    
    def test_blocking_factors(self):
        """
        Test 4 : Vérification des facteurs bloquants
        """
        print("🚨 TEST 4 : FACTEURS BLOQUANTS")
        print("=" * 50)
        
        results = self.enhanced_v2.calculate_matches(
            self.zachary_cv, 
            [self.test_jobs[0]]  # Poste juridique seulement
        )
        
        juridique_result = results[0]
        blocking_factors = juridique_result.get('blocking_factors', [])
        
        print(f"Facteurs bloquants détectés: {len(blocking_factors)}")
        for factor in blocking_factors:
            print(f"  - {factor['type']}: {factor['description']}")
            print(f"    Sévérité: {factor['severity']}")
            print(f"    Recommandation: {factor['recommendation']}")
        
        # Assertions
        assert len(blocking_factors) > 0, "Des facteurs bloquants devraient être détectés"
        sector_blocking = any(bf['type'] == 'sector_incompatibility' for bf in blocking_factors)
        assert sector_blocking, "Facteur bloquant sectoriel devrait être détecté"
        
        print("✅ Facteurs bloquants correctement détectés")
        
        return blocking_factors
    
    def test_recommendations(self):
        """
        Test 5 : Vérification des recommandations
        """
        print("💡 TEST 5 : RECOMMANDATIONS INTELLIGENTES")
        print("=" * 50)
        
        results = self.enhanced_v2.calculate_matches(
            self.zachary_cv, 
            self.test_jobs
        )
        
        for result in results:
            print(f"\nJob {result['id']} ({result['matching_score']}%):")
            recommendations = result.get('recommendations', [])
            for rec in recommendations:
                print(f"  • {rec}")
        
        # Vérification qu'il y a des recommandations
        for result in results:
            assert 'recommendations' in result, f"Recommandations manquantes pour {result['id']}"
            assert len(result['recommendations']) > 0, f"Pas de recommandations pour {result['id']}"
        
        print("\n✅ Recommandations générées pour tous les postes")
        
        return results
    
    def run_full_test_suite(self):
        """
        Lance la suite complète de tests
        """
        print("🚀 SUITE DE TESTS SUPERSMARTTMATCH V2.1")
        print("=" * 60)
        print(f"Objectif: Prouver que Commercial junior vs Juridique passe de 79% à ~25%")
        print("=" * 60)
        print()
        
        start_time = time.time()
        
        try:
            # Test 1 : Détection sectorielle
            cv_analysis = self.test_sector_detection()
            print()
            
            # Test 2 : Matrice de compatibilité
            compatibility = self.test_compatibility_matrix()
            print()
            
            # Test 3 : Comparaison algorithmes
            enhanced_results, semantic_results = self.test_enhanced_v2_vs_semantic()
            print()
            
            # Test 4 : Facteurs bloquants
            blocking_factors = self.test_blocking_factors()
            print()
            
            # Test 5 : Recommandations
            recommendations_results = self.test_recommendations()
            print()
            
            # Résumé final
            execution_time = time.time() - start_time
            
            print("🎉 RÉSUMÉ DES TESTS")
            print("=" * 50)
            print(f"✅ Tous les tests passés en {execution_time:.2f}s")
            print()
            print(f"🎯 PROBLÈME RÉSOLU :")
            enhanced_juridique = next(r for r in enhanced_results if r['id'] == 'job_juridique_1')
            semantic_juridique = next(r for r in semantic_results if r['id'] == 'job_juridique_1')
            
            print(f"   Commercial junior vs Assistant juridique:")
            print(f"   Ancien (Semantic): {semantic_juridique['matching_score']}%")
            print(f"   Nouveau (Enhanced V2.1): {enhanced_juridique['matching_score']}%")
            print(f"   Amélioration: {semantic_juridique['matching_score'] - enhanced_juridique['matching_score']}% de réduction")
            print()
            print(f"🔍 Secteur détecté CV: {cv_analysis.primary_sector} (confiance: {cv_analysis.confidence:.2f})")
            print(f"🔗 Compatibilité commercial->juridique: {compatibility:.2f}")
            print(f"🚨 Facteurs bloquants détectés: {len(blocking_factors)}")
            print()
            print("🚀 SuperSmartMatch V2.1 est prêt pour la production !")
            
            return True
            
        except AssertionError as e:
            print(f"❌ ÉCHEC DU TEST: {str(e)}")
            return False
        except Exception as e:
            print(f"💥 ERREUR INATTENDUE: {str(e)}")
            return False

def test_api_endpoint():
    """
    Test optionnel de l'API si le serveur est lancé
    """
    try:
        # Test du health check
        response = requests.get('http://localhost:5060/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"🌐 API Health Check: {data['status']} - Version: {data.get('version', 'Unknown')}")
            return True
    except:
        print("⚠️ API non disponible (serveur non lancé)")
        return False

if __name__ == '__main__':
    print("SuperSmartMatch V2.1 - Test Suite")
    print()
    
    # Test API optionnel
    test_api_endpoint()
    print()
    
    # Suite de tests principale
    tester = SuperSmartMatchV2Tester()
    success = tester.run_full_test_suite()
    
    # Code de sortie
    exit_code = 0 if success else 1
    print(f"\nCode de sortie: {exit_code}")
    exit(exit_code)
