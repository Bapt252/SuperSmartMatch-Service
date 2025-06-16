#!/usr/bin/env python3
"""
SuperSmartMatch V2.1 - Script de Debug
Diagnostique pourquoi tous les scores sont à 0%
"""

import os
import json
import requests
import re
from pathlib import Path
import pdfplumber

def debug_api_response():
    """Teste l'API avec des données simples pour vérifier le fonctionnement"""
    
    print("🔍 DIAGNOSTIC SUPERSMARTMATCH V2.1")
    print("=" * 50)
    
    # Test simple avec données connues
    test_data = {
        "candidate": {
            "competences": ["Comptabilité", "Excel", "Sage"],
            "secteur": "comptabilite",
            "annees_experience": 3
        },
        "jobs": [{
            "id": "test_job",
            "titre": "Comptable",
            "competences": ["Comptabilité", "Excel"],
            "secteur": "comptabilite",
            "experience": "2-5 ans"
        }],
        "algorithm": "enhanced-v2",
        "options": {"include_details": True}
    }
    
    print("📋 Test avec données de référence...")
    print(f"Candidat: {test_data['candidate']}")
    print(f"Job: {test_data['jobs'][0]}")
    
    try:
        response = requests.post(
            "http://localhost:5061/api/v1/match",
            json=test_data,
            timeout=10
        )
        
        print(f"\n📡 Réponse API (status: {response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Analyse des scores
            if "matches" in result:
                for i, match in enumerate(result["matches"]):
                    score = match.get("score", 0)
                    print(f"\n🎯 Match {i+1}: Score = {score}%")
                    if score == 0:
                        print("❌ PROBLÈME: Score à 0% détecté!")
                        print("🔍 Détails du match:", match.get("details", "Aucun détail"))
            else:
                print("❌ PROBLÈME: Pas de clé 'matches' dans la réponse")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")

def test_real_files():
    """Teste avec de vrais fichiers pour voir le parsing"""
    
    print("\n" + "=" * 50)
    print("🔍 TEST AVEC FICHIERS RÉELS")
    print("=" * 50)
    
    cv_folder = "/Users/baptistecomas/Desktop/CV TEST/"
    job_folder = "/Users/baptistecomas/Desktop/FDP TEST/"
    
    # Test sur un CV et une fiche de poste
    cv_files = [f for f in os.listdir(cv_folder) if f.endswith('.pdf')][:1]
    job_files = [f for f in os.listdir(job_folder) if f.endswith('.pdf')][:1]
    
    if cv_files and job_files:
        print(f"📄 Test CV: {cv_files[0]}")
        print(f"📋 Test Job: {job_files[0]}")
        
        # Parse le CV
        cv_path = os.path.join(cv_folder, cv_files[0])
        cv_data = parse_file_debug(cv_path, "CV")
        
        # Parse la fiche de poste
        job_path = os.path.join(job_folder, job_files[0])
        job_data = parse_file_debug(job_path, "Job")
        
        if cv_data and job_data:
            # Test du matching
            test_real_matching(cv_data, job_data)

def parse_file_debug(file_path, file_type):
    """Parse un fichier et affiche les détails"""
    
    print(f"\n📖 Parsing {file_type}: {Path(file_path).name}")
    
    try:
        # Extraction texte
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        print(f"📝 Texte extrait: {len(text)} caractères")
        print(f"🔍 Aperçu: {text[:200]}...")
        
        # Détection secteur
        secteur = detect_secteur_debug(text)
        print(f"🎯 Secteur détecté: {secteur}")
        
        # Extraction compétences
        competences = extract_competences_debug(text, secteur)
        print(f"🛠️ Compétences: {competences}")
        
        # Extraction expérience
        experience = extract_experience_debug(text)
        print(f"⏰ Expérience: {experience} ans")
        
        if file_type == "CV":
            return {
                "filename": Path(file_path).name,
                "competences": competences,
                "secteur": secteur,
                "annees_experience": experience
            }
        else:
            return {
                "id": Path(file_path).stem,
                "filename": Path(file_path).name,
                "titre": f"Poste {secteur}",
                "competences": competences,
                "secteur": secteur,
                "experience": f"{experience}-{experience+2} ans" if experience > 0 else "Débutant accepté"
            }
            
    except Exception as e:
        print(f"❌ Erreur parsing: {e}")
        return None

def detect_secteur_debug(text):
    """Détection de secteur avec debug"""
    
    secteur_keywords = {
        "commercial": ["vente", "commercial", "vendeur", "business", "client"],
        "juridique": ["droit", "juridique", "avocat", "juriste", "contrat"],
        "comptabilite": ["comptable", "comptabilité", "bilan", "fiscalité", "audit"],
        "informatique": ["développeur", "programmeur", "python", "javascript", "sql"],
        "management": ["manager", "directeur", "chef", "équipe", "leadership"],
        "rh": ["ressources humaines", "recrutement", "paie", "formation", "rh"],
        "finance": ["finance", "financier", "trésorerie", "budget"],
    }
    
    text_lower = text.lower()
    secteur_scores = {}
    
    for secteur, keywords in secteur_keywords.items():
        score = 0
        found_keywords = []
        for keyword in keywords:
            count = text_lower.count(keyword)
            if count > 0:
                score += count
                found_keywords.append(f"{keyword}({count})")
        secteur_scores[secteur] = {"score": score, "keywords": found_keywords}
    
    print(f"🔍 Scores secteurs: {secteur_scores}")
    
    best_secteur = max(secteur_scores.items(), key=lambda x: x[1]["score"])
    return best_secteur[0] if best_secteur[1]["score"] > 0 else "commercial"

def extract_competences_debug(text, secteur):
    """Extraction compétences avec debug"""
    
    secteur_keywords = {
        "comptabilite": ["comptable", "comptabilité", "bilan", "fiscalité", "audit", "sage", "excel"],
        "juridique": ["droit", "juridique", "avocat", "contrat", "legal"],
        "commercial": ["vente", "commercial", "crm", "prospection"],
        "informatique": ["python", "javascript", "sql", "développement"],
        "management": ["management", "équipe", "leadership", "gestion"],
    }
    
    competences = []
    keywords = secteur_keywords.get(secteur, [])
    
    for keyword in keywords:
        if keyword.lower() in text.lower():
            competences.append(keyword.title())
    
    return competences[:5] if competences else ["Polyvalent"]

def extract_experience_debug(text):
    """Extraction expérience avec debug"""
    
    patterns = [
        r'(\d+)\s*an[s]?\s*(?:d\'|de)?\s*(?:exp[eé]rience)?',
        r'(\d+)\s*années?\s*d\'exp[eé]rience',
        r'exp[eé]rience\s*:\s*(\d+)',
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            try:
                return int(matches[0]) if matches[0].isdigit() else 0
            except:
                continue
    
    return 0

def test_real_matching(cv_data, job_data):
    """Teste le matching avec de vraies données"""
    
    print(f"\n🎯 TEST MATCHING RÉEL")
    print("-" * 30)
    
    payload = {
        "candidate": cv_data,
        "jobs": [job_data],
        "algorithm": "enhanced-v2",
        "options": {"include_details": True}
    }
    
    print(f"📤 Données envoyées à l'API:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            "http://localhost:5061/api/v1/match",
            json=payload,
            timeout=10
        )
        
        print(f"\n📥 Réponse API (status: {response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Analyse détaillée du résultat
            if "matches" in result and result["matches"]:
                match = result["matches"][0]
                score = match.get("score", 0)
                
                print(f"\n📊 RÉSULTAT FINAL:")
                print(f"Score: {score}%")
                print(f"Détails: {match.get('details', 'Aucun')}")
                
                if score == 0:
                    print("\n❌ SCORE À 0% - CAUSES POSSIBLES:")
                    print("1. Aucune compétence en commun")
                    print("2. Secteurs incompatibles")
                    print("3. Problème dans l'algorithme Enhanced V2.1")
                    print("4. Données mal formatées")
                    
        else:
            print(f"❌ Erreur API: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    # Test 1: API avec données simples
    debug_api_response()
    
    # Test 2: Fichiers réels
    test_real_files()
