#!/usr/bin/env python3
"""
🎯 DÉMONSTRATION IMMÉDIATE : V2.1 vs V3.0
Prouve la résolution des problèmes de précision métier

OBJECTIF : Montrer que V3.0 résout exactement vos problèmes :
- Gestionnaire paie vs Assistant facturation : 90% → 25%
- Assistant juridique vs Management : 79% → 15%

Usage: python demo_precision_v3.py
"""

import requests
import json
import time
from typing import Dict, Any

class PrecisionDemoV3:
    def __init__(self):
        self.api_base = "http://localhost:5061/api/v1"
        self.test_cases = self._setup_test_cases()
    
    def _setup_test_cases(self) -> list:
        """Définit les cas de test problématiques identifiés"""
        return [
            {
                "name": "🔥 CAS CRITIQUE : Gestionnaire Paie → Assistant Facturation",
                "description": "V2.1 donne 90% (faux positif majeur)",
                "expected_v3": "≤ 25%",
                "candidate": {
                    "titre_poste": "Gestionnaire de paie",
                    "competences": [
                        "Sage Paie", "Silae", "Charges sociales", "URSSAF",
                        "Cotisations", "Bulletins paie", "DSN", "Administration personnel"
                    ],
                    "secteur": "rh",
                    "annees_experience": 3,
                    "missions": [
                        "Établissement des bulletins de paie",
                        "Gestion des charges sociales",
                        "Déclarations URSSAF et DSN",
                        "Administration du personnel"
                    ]
                },
                "job": {
                    "id": "facturation_001",
                    "titre": "Assistant Facturation",
                    "competences": [
                        "Facturation", "Sage Commercial", "Recouvrement",
                        "Comptes clients", "Devis", "Relances clients"
                    ],
                    "secteur": "comptabilite",
                    "description": "Gestion de la facturation clients et recouvrement",
                    "missions": [
                        "Établissement des factures clients",
                        "Suivi des comptes clients",
                        "Relances de recouvrement",
                        "Gestion des devis commerciaux"
                    ]
                }
            },
            {
                "name": "🔥 CAS CRITIQUE : Assistant Juridique → Management",
                "description": "V2.1 donne 79% (confusion assistant/manager)",
                "expected_v3": "≤ 15%",
                "candidate": {
                    "titre_poste": "Assistant juridique",
                    "competences": [
                        "Droit", "Procédures", "Contentieux", "Secrétariat juridique",
                        "Dossiers juridiques", "Correspondance", "Archivage"
                    ],
                    "secteur": "juridique",
                    "annees_experience": 2,
                    "missions": [
                        "Assistance aux juristes",
                        "Gestion des dossiers contentieux",
                        "Correspondance avec tribunaux",
                        "Archivage des documents juridiques"
                    ]
                },
                "job": {
                    "id": "management_001",
                    "titre": "Manager d'équipe",
                    "competences": [
                        "Management", "Leadership", "Gestion équipe",
                        "Objectifs", "Coordination", "Encadrement"
                    ],
                    "secteur": "management",
                    "description": "Management d'une équipe de 8 personnes",
                    "missions": [
                        "Encadrement de l'équipe",
                        "Définition des objectifs",
                        "Coordination des projets",
                        "Évaluation des performances"
                    ]
                }
            },
            {
                "name": "✅ CAS POSITIF : Comptable → Comptable",
                "description": "Doit donner un score élevé dans les deux versions",
                "expected_v3": "≥ 80%",
                "candidate": {
                    "titre_poste": "Comptable",
                    "competences": [
                        "Comptabilité générale", "Sage Comptabilité", "Bilan",
                        "TVA", "Écritures comptables", "Lettrage"
                    ],
                    "secteur": "comptabilite",
                    "annees_experience": 4,
                    "missions": [
                        "Saisie des écritures comptables",
                        "Établissement des bilans",
                        "Gestion de la TVA",
                        "Lettrage des comptes"
                    ]
                },
                "job": {
                    "id": "compta_001",
                    "titre": "Comptable",
                    "competences": [
                        "Comptabilité générale", "Sage", "Bilan",
                        "Fiscalité", "Analyse financière"
                    ],
                    "secteur": "comptabilite",
                    "description": "Comptable polyvalent en cabinet",
                    "missions": [
                        "Tenue de la comptabilité",
                        "Révision des comptes",
                        "Conseils fiscaux",
                        "Relations clients"
                    ]
                }
            }
        ]
    
    def check_api_health(self) -> bool:
        """Vérifie que l'API est disponible"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                algorithms = data.get("algorithms_available", [])
                
                v2_available = "enhanced-v2" in algorithms
                v3_available = "enhanced-v3" in algorithms
                
                print(f"✅ API disponible")
                print(f"   Enhanced V2.1: {'✅' if v2_available else '❌'}")
                print(f"   Enhanced V3.0: {'✅' if v3_available else '❌'}")
                
                if not v3_available:
                    print("⚠️  Enhanced V3.0 non détecté - mais test possible")
                
                return True
            else:
                print(f"❌ API non disponible (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur connexion API: {e}")
            return False
    
    def test_algorithm(self, candidate: Dict, job: Dict, algorithm: str) -> Dict[str, Any]:
        """Teste un algorithme spécifique"""
        try:
            payload = {
                "candidate": candidate,
                "jobs": [job],
                "algorithm": algorithm,
                "options": {"include_details": True}
            }
            
            start_time = time.time()
            response = requests.post(f"{self.api_base}/match", json=payload, timeout=10)
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                matches = result.get("matches", [])
                
                if matches:
                    match = matches[0]
                    score = match.get("matching_score", 0)
                    algorithm_used = result.get("algorithm_used", algorithm)
                    
                    return {
                        "success": True,
                        "score": score,
                        "algorithm_used": algorithm_used,
                        "execution_time_ms": execution_time,
                        "details": match.get("matching_details", {}),
                        "explanation": match.get("explanation", ""),
                        "recommendations": match.get("recommendations", [])
                    }
                else:
                    return {"success": False, "error": "Aucun match retourné"}
            else:
                return {"success": False, "error": f"Erreur API: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_algorithms(self, test_case: Dict) -> None:
        """Compare V2.1 vs V3.0 pour un cas de test"""
        print(f"\n{'='*80}")
        print(f"🧪 TEST : {test_case['name']}")
        print(f"📋 {test_case['description']}")
        print(f"🎯 Attendu V3.0 : {test_case['expected_v3']}")
        print(f"{'='*80}")
        
        candidate = test_case["candidate"]
        job = test_case["job"]
        
        print(f"\n📄 CANDIDAT: {candidate['titre_poste']} ({candidate['annees_experience']} ans)")
        print(f"   Compétences: {', '.join(candidate['competences'][:3])}...")
        print(f"\n📋 POSTE: {job['titre']}")
        print(f"   Compétences: {', '.join(job['competences'][:3])}...")
        
        # Test V2.1
        print(f"\n🔄 Test Enhanced V2.1...")
        result_v2 = self.test_algorithm(candidate, job, "enhanced-v2")
        
        # Test V3.0
        print(f"🔄 Test Enhanced V3.0...")
        result_v3 = self.test_algorithm(candidate, job, "enhanced-v3")
        
        # Affichage des résultats
        print(f"\n📊 RÉSULTATS COMPARATIFS:")
        print(f"{'─'*60}")
        
        if result_v2["success"]:
            score_v2 = result_v2["score"]
            print(f"📈 Enhanced V2.1 : {score_v2:.1f}% ({result_v2['execution_time_ms']:.0f}ms)")
        else:
            print(f"❌ Enhanced V2.1 : ERREUR - {result_v2['error']}")
            score_v2 = None
        
        if result_v3["success"]:
            score_v3 = result_v3["score"]
            print(f"📈 Enhanced V3.0 : {score_v3:.1f}% ({result_v3['execution_time_ms']:.0f}ms)")
        else:
            print(f"❌ Enhanced V3.0 : ERREUR - {result_v3['error']}")
            score_v3 = None
        
        # Analyse de l'amélioration
        if score_v2 is not None and score_v3 is not None:
            difference = score_v2 - score_v3
            print(f"{'─'*60}")
            
            if "gestionnaire_paie" in candidate["titre_poste"].lower() and "facturation" in job["titre"].lower():
                # Cas gestionnaire paie → facturation
                if score_v3 <= 25 and score_v2 >= 80:
                    print(f"✅ PROBLÈME RÉSOLU : {score_v2:.1f}% → {score_v3:.1f}% (différence: -{difference:.1f}%)")
                    print(f"🎯 Faux positif V2.1 éliminé ! Score V3.0 ≤ 25% comme attendu")
                elif score_v3 <= 25:
                    print(f"✅ V3.0 CORRECT : {score_v3:.1f}% ≤ 25% (objectif atteint)")
                else:
                    print(f"⚠️  V3.0 À AMÉLIORER : {score_v3:.1f}% > 25% (objectif non atteint)")
            
            elif "assistant juridique" in candidate["titre_poste"].lower() and "manager" in job["titre"].lower():
                # Cas assistant juridique → management
                if score_v3 <= 15 and score_v2 >= 70:
                    print(f"✅ PROBLÈME RÉSOLU : {score_v2:.1f}% → {score_v3:.1f}% (différence: -{difference:.1f}%)")
                    print(f"🎯 Confusion assistant/manager V2.1 résolue ! Score V3.0 ≤ 15%")
                elif score_v3 <= 15:
                    print(f"✅ V3.0 CORRECT : {score_v3:.1f}% ≤ 15% (objectif atteint)")
                else:
                    print(f"⚠️  V3.0 À AMÉLIORER : {score_v3:.1f}% > 15% (objectif non atteint)")
            
            else:
                # Cas positif (score élevé attendu)
                if score_v3 >= 80:
                    print(f"✅ MATCH POSITIF CONFIRMÉ : {score_v3:.1f}% ≥ 80%")
                    if score_v3 > score_v2:
                        print(f"🚀 AMÉLIORATION V3.0 : +{score_v3 - score_v2:.1f}% vs V2.1")
                else:
                    print(f"⚠️  Score V3.0 plus faible qu'attendu : {score_v3:.1f}% < 80%")
        
        # Détails techniques V3.0
        if result_v3["success"] and result_v3.get("details"):
            details = result_v3["details"]
            print(f"\n🔬 DÉTAILS TECHNIQUES V3.0:")
            if "job_specificity_match" in details:
                print(f"   Spécificité métier: {details['job_specificity_match']:.1f}%")
            if "sector_compatibility" in details:
                print(f"   Compatibilité sectorielle: {details['sector_compatibility']:.1f}%")
        
        # Recommandations V3.0
        if result_v3["success"] and result_v3.get("recommendations"):
            print(f"\n💡 RECOMMANDATIONS V3.0:")
            for rec in result_v3["recommendations"][:2]:  # 2 premières seulement
                print(f"   • {rec}")
    
    def run_demo(self) -> None:
        """Lance la démonstration complète"""
        print("🎯 DÉMONSTRATION PRÉCISION V2.1 vs V3.0")
        print("Résolution : Gestionnaire paie vs Assistant facturation 90% → 25%")
        print("=" * 80)
        
        # Vérification API
        if not self.check_api_health():
            print("❌ Démonstration annulée : API non disponible")
            return
        
        print(f"\n🧪 {len(self.test_cases)} cas de test définis")
        
        # Exécution des tests
        results_summary = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n🔄 EXÉCUTION TEST {i}/{len(self.test_cases)}")
            self.compare_algorithms(test_case)
            
            # Collecte résultats pour résumé
            results_summary.append({
                "name": test_case["name"],
                "expected": test_case["expected_v3"]
            })
        
        # Résumé final
        print(f"\n{'🎉 RÉSUMÉ DÉMONSTRATION':<80}")
        print("=" * 80)
        print("✅ Tests terminés - Vérifiez les résultats ci-dessus")
        print("\n🎯 OBJECTIFS V3.0 :")
        for result in results_summary:
            print(f"   • {result['name']}: {result['expected']}")
        
        print(f"\n💡 CONCLUSION :")
        print("Si les objectifs sont atteints, Enhanced V3.0 résout vos problèmes !")
        print("Migrez votre test_massif.py : 'enhanced-v2' → 'enhanced-v3'")
        
        print(f"\n📋 PROCHAINES ÉTAPES :")
        print("1. Vérifiez les scores obtenus vs objectifs")
        print("2. Utilisez le script test_massif_v3_migration.py")
        print("3. Migrez définitivement vers Enhanced V3.0")


def main():
    """Point d'entrée principal"""
    demo = PrecisionDemoV3()
    demo.run_demo()


if __name__ == "__main__":
    main()
