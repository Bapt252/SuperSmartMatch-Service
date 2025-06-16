#!/usr/bin/env python3
"""
SuperSmartMatch V2.1 - Debug Simple
Diagnostique rapide pourquoi tous les scores sont à 0%
"""

import json
import requests

def test_api_simple():
    """Test simple de l'API pour identifier le problème"""
    
    print("🔍 DIAGNOSTIC RAPIDE SUPERSMARTMATCH V2.1")
    print("=" * 60)
    
    # Test 1: Données parfaitement compatibles
    print("\n🧪 TEST 1: Candidat et poste identiques")
    print("-" * 40)
    
    test_perfect_match = {
        "candidate": {
            "competences": ["Comptabilité", "Excel", "Sage"],
            "secteur": "comptabilite",
            "annees_experience": 3,
            "titre_poste": "Comptable"
        },
        "jobs": [{
            "id": "comptable_senior",
            "titre": "Comptable Senior",
            "competences": ["Comptabilité", "Excel", "Sage"],
            "secteur": "comptabilite",
            "experience": "2-5 ans"
        }],
        "algorithm": "enhanced-v2",
        "options": {"include_details": True}
    }
    
    result1 = call_api(test_perfect_match, "Match parfait")
    
    # Test 2: Données moyennement compatibles
    print("\n🧪 TEST 2: Candidat et poste partiellement compatibles")
    print("-" * 40)
    
    test_partial_match = {
        "candidate": {
            "competences": ["Commercial", "Vente"],
            "secteur": "commercial",
            "annees_experience": 2
        },
        "jobs": [{
            "id": "assistant_commercial",
            "titre": "Assistant Commercial",
            "competences": ["Vente", "CRM"],
            "secteur": "commercial",
            "experience": "1-3 ans"
        }],
        "algorithm": "enhanced-v2",
        "options": {"include_details": True}
    }
    
    result2 = call_api(test_partial_match, "Match partiel")
    
    # Test 3: Données incompatibles
    print("\n🧪 TEST 3: Candidat et poste incompatibles")
    print("-" * 40)
    
    test_no_match = {
        "candidate": {
            "competences": ["Développement", "Python", "SQL"],
            "secteur": "informatique",
            "annees_experience": 5
        },
        "jobs": [{
            "id": "avocat",
            "titre": "Avocat Senior",
            "competences": ["Droit", "Contentieux"],
            "secteur": "juridique",
            "experience": "5-10 ans"
        }],
        "algorithm": "enhanced-v2",
        "options": {"include_details": True}
    }
    
    result3 = call_api(test_no_match, "Aucun match")
    
    # Test 4: Avec vos vraies fiches de poste
    print("\n🧪 TEST 4: Avec les titres de vos vraies fiches")
    print("-" * 40)
    
    test_real_jobs = {
        "candidate": {
            "competences": ["Comptabilité", "Excel", "Sage", "Bilan"],
            "secteur": "comptabilite",
            "annees_experience": 3,
            "titre_poste": "Comptable"
        },
        "jobs": [
            {
                "id": "assistant_juridique",
                "titre": "Assistant Juridique",
                "competences": ["Droit", "Juridique", "Contrat"],
                "secteur": "juridique",
                "experience": "2-4 ans"
            },
            {
                "id": "assistant_facturation", 
                "titre": "Assistant Facturation",
                "competences": ["Facturation", "Comptabilité", "Excel"],
                "secteur": "comptabilite",
                "experience": "1-3 ans"
            },
            {
                "id": "responsable_comptable",
                "titre": "Responsable Comptable",
                "competences": ["Comptabilité", "Bilan", "Fiscalité", "Équipe"],
                "secteur": "comptabilite", 
                "experience": "3-7 ans"
            }
        ],
        "algorithm": "enhanced-v2",
        "options": {"include_details": True}
    }
    
    result4 = call_api(test_real_jobs, "Vraies fiches de poste")
    
    # Analyse des résultats
    print("\n" + "=" * 60)
    print("📊 ANALYSE DES RÉSULTATS")
    print("=" * 60)
    
    results = [result1, result2, result3, result4]
    test_names = ["Match parfait", "Match partiel", "Aucun match", "Vraies fiches"]
    
    all_zero = True
    for i, (result, name) in enumerate(zip(results, test_names)):
        if result:
            scores = extract_scores(result)
            max_score = max(scores) if scores else 0
            print(f"📋 {name}: Score max = {max_score}%")
            if max_score > 0:
                all_zero = False
        else:
            print(f"❌ {name}: Erreur API")
    
    if all_zero:
        print("\n🚨 PROBLÈME IDENTIFIÉ: Tous les scores sont à 0%")
        print("📋 CAUSES POSSIBLES:")
        print("   1. Algorithme Enhanced V2.1 défaillant")
        print("   2. Configuration incorrecte")
        print("   3. Problème dans le calcul des scores")
        print("   4. Structure de données incorrecte")
        
        print("\n🔧 SOLUTIONS À ESSAYER:")
        print("   1. Tester avec l'algorithme 'hybrid' ou 'semantic'")
        print("   2. Vérifier les logs du service SuperSmartMatch")
        print("   3. Redémarrer le service")
        print("   4. Vérifier la configuration Enhanced V2.1")
    else:
        print("\n✅ L'API fonctionne partiellement")

def call_api(payload, test_name):
    """Appelle l'API et retourne le résultat"""
    
    try:
        print(f"📤 Test: {test_name}")
        print(f"📝 Candidat: {payload['candidate']['secteur']} - {payload['candidate']['competences']}")
        print(f"📋 Jobs: {len(payload['jobs'])} poste(s)")
        
        response = requests.post(
            "http://localhost:5061/api/v1/match",
            json=payload,
            timeout=10
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Affichage des scores
            if "matches" in result:
                for i, match in enumerate(result["matches"]):
                    score = match.get("score", 0)
                    job_info = match.get("job", {})
                    job_titre = job_info.get("titre", f"Job {i+1}")
                    print(f"   🎯 {job_titre}: {score}%")
                    
                    if score == 0:
                        details = match.get("details", "")
                        if details:
                            print(f"      💡 Détails: {details}")
            else:
                print(f"   ❌ Pas de clé 'matches' dans la réponse")
                print(f"   📄 Réponse: {result}")
            
            return result
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def extract_scores(result):
    """Extrait tous les scores d'un résultat"""
    scores = []
    if "matches" in result:
        for match in result["matches"]:
            score = match.get("score", 0)
            scores.append(score)
    return scores

def test_different_algorithms():
    """Teste avec différents algorithmes"""
    
    print("\n" + "=" * 60)
    print("🔬 TEST AVEC DIFFÉRENTS ALGORITHMES")
    print("=" * 60)
    
    base_payload = {
        "candidate": {
            "competences": ["Comptabilité", "Excel"],
            "secteur": "comptabilite",
            "annees_experience": 3
        },
        "jobs": [{
            "id": "comptable",
            "titre": "Comptable",
            "competences": ["Comptabilité", "Excel"],
            "secteur": "comptabilite",
            "experience": "2-5 ans"
        }],
        "options": {"include_details": True}
    }
    
    algorithms = ["enhanced-v2", "hybrid", "semantic", "smart-match"]
    
    for algo in algorithms:
        print(f"\n🧪 Test avec algorithme: {algo}")
        test_payload = base_payload.copy()
        test_payload["algorithm"] = algo
        
        result = call_api(test_payload, f"Algorithme {algo}")

if __name__ == "__main__":
    # Test principal
    test_api_simple()
    
    # Test des algorithmes
    test_different_algorithms()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC TERMINÉ")
    print("📋 Si tous les scores sont à 0%, le problème vient de SuperSmartMatch V2.1")
    print("📞 Partagez ces résultats pour identifier la cause exacte")
    print("=" * 60)
