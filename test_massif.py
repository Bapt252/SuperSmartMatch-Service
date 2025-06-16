#!/usr/bin/env python3
"""
SuperSmartMatch V2.1 - Script de Test Massif
Automatise les tests de matching CV vs Fiches de Poste
Génère rapports complets CSV + HTML
"""

import os
import json
import requests
import re
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any, Optional

# Gestion des imports PDF avec fallback
try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
    print("✅ pdfplumber disponible (recommandé)")
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = "PyPDF2"
        print("⚠️  pdfplumber non disponible, utilisation de PyPDF2")
        print("💡 Pour de meilleurs résultats: pip install pdfplumber")
    except ImportError:
        print("❌ Aucune librairie PDF disponible!")
        print("📦 Installez: pip install pdfplumber PyPDF2")
        exit(1)

class SuperSmartMatchTester:
    def __init__(self):
        """Initialise le testeur massif SuperSmartMatch V2.1"""
        self.api_base = "http://localhost:5061/api/v1"
        self.cv_folder = "/Users/baptistecomas/Desktop/CV TEST/"
        self.job_folder = "/Users/baptistecomas/Desktop/FDP TEST/"
        
        # Secteurs supportés par SuperSmartMatch V2.1
        self.secteurs = [
            "commercial", "juridique", "comptabilite", "informatique", 
            "marketing", "rh", "finance", "production", "management"
        ]
        
        # Mots-clés pour détection automatique des secteurs
        self.secteur_keywords = {
            "commercial": ["vente", "commercial", "vendeur", "business", "client", "prospection", "crm", "chiffre d'affaires"],
            "juridique": ["droit", "juridique", "avocat", "juriste", "contrat", "contentieux", "legal", "tribunal"],
            "comptabilite": ["comptable", "comptabilité", "bilan", "fiscalité", "audit", "expert-comptable", "sage"],
            "informatique": ["développeur", "programmeur", "python", "javascript", "sql", "développement", "informatique", "software"],
            "marketing": ["marketing", "communication", "digital", "seo", "campagne", "brand", "publicité"],
            "rh": ["ressources humaines", "recrutement", "paie", "formation", "rh", "talent", "hr"],
            "finance": ["finance", "financier", "trésorerie", "budget", "contrôle de gestion", "analyste financier"],
            "production": ["production", "industriel", "qualité", "lean", "process", "manufacturing"],
            "management": ["manager", "directeur", "chef", "équipe", "leadership", "encadrement", "gestion"]
        }
        
        # Patterns pour extraction automatique
        self.experience_patterns = [
            r'(\d+)\s*(?:à|a|-)?\s*(\d+)?\s*an[s]?\s*(?:d\'|d'|de)?\s*(?:exp[eé]rience)?',
            r'(\d+)\s*années?\s*d\'exp[eé]rience',
            r'exp[eé]rience\s*:\s*(\d+)',
            r'(\d+)\s*ans\s*(?:minimum|mini|min)',
        ]
        
        self.competences_patterns = [
            r'comp[eé]tences?\s*:?\s*([^.]+)',
            r'technologies?\s*:?\s*([^.]+)',
            r'outils?\s*:?\s*([^.]+)',
            r'logiciels?\s*:?\s*([^.]+)',
        ]
        
        # Statistiques globales
        self.stats = {
            "cvs_processed": 0,
            "jobs_processed": 0,
            "total_matches": 0,
            "errors": 0,
            "start_time": None,
            "secteurs_detected": {},
        }
        
        print(f"🚀 SuperSmartMatch V2.1 Mass Tester initialisé")
        print(f"📁 CVs: {self.cv_folder}")
        print(f"📁 Jobs: {self.job_folder}")

    def check_api_health(self) -> bool:
        """Vérifie que l'API SuperSmartMatch est disponible"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API SuperSmartMatch V2.1 disponible")
                return True
            else:
                print(f"❌ API non disponible (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur connexion API: {e}")
            return False

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            if PDF_LIBRARY == "pdfplumber":
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text.lower()
            
            elif PDF_LIBRARY == "PyPDF2":
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.lower()
                    
        except Exception as e:
            print(f"❌ Erreur lecture PDF {file_path}: {e}")
            return ""

    def detect_secteur(self, text: str) -> str:
        """Détecte automatiquement le secteur à partir du texte"""
        secteur_scores = {}
        
        for secteur, keywords in self.secteur_keywords.items():
            score = 0
            for keyword in keywords:
                # Compte les occurrences pondérées
                count = text.count(keyword.lower())
                score += count * (len(keyword) / 5)  # Bonus pour mots plus longs
            secteur_scores[secteur] = score
        
        # Retourne le secteur avec le meilleur score
        best_secteur = max(secteur_scores.items(), key=lambda x: x[1])
        if best_secteur[1] > 0:
            return best_secteur[0]
        return "commercial"  # Secteur par défaut

    def extract_experience(self, text: str) -> int:
        """Extrait les années d'expérience du texte"""
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Prend la première valeur trouvée
                if isinstance(matches[0], tuple):
                    return int(matches[0][0]) if matches[0][0].isdigit() else 0
                elif matches[0].isdigit():
                    return int(matches[0])
        return 0  # Expérience par défaut

    def extract_competences(self, text: str, secteur: str) -> List[str]:
        """Extrait les compétences principales du texte"""
        competences = []
        
        # Ajoute les mots-clés du secteur détecté
        secteur_keywords = self.secteur_keywords.get(secteur, [])
        for keyword in secteur_keywords:
            if keyword.lower() in text:
                competences.append(keyword.title())
        
        # Cherche des sections compétences explicites
        for pattern in self.competences_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split et nettoie
                skills = [s.strip().title() for s in re.split(r'[,;|\n-]', match) if s.strip()]
                competences.extend(skills[:5])  # Limite à 5 par match
        
        # Supprime doublons et limite
        competences = list(dict.fromkeys(competences))[:10]
        
        # Ajoute des compétences par défaut si vide
        if not competences:
            competences = secteur_keywords[:3] if secteur_keywords else ["Polyvalent"]
        
        return competences

    def parse_cv(self, file_path: str) -> Dict[str, Any]:
        """Parse un CV et extrait les informations structured"""
        filename = Path(file_path).name
        text = self.extract_text_from_pdf(file_path)
        
        if not text:
            return None
        
        secteur = self.detect_secteur(text)
        experience = self.extract_experience(text)
        competences = self.extract_competences(text, secteur)
        
        # Stats
        self.stats["secteurs_detected"][secteur] = self.stats["secteurs_detected"].get(secteur, 0) + 1
        
        return {
            "filename": filename,
            "competences": competences,
            "secteur": secteur,
            "annees_experience": experience,
            "titre_poste": f"Candidat {secteur.title()}"
        }

    def parse_job(self, file_path: str) -> Dict[str, Any]:
        """Parse une fiche de poste et extrait les informations"""
        filename = Path(file_path).name
        text = self.extract_text_from_pdf(file_path)
        
        if not text:
            return None
        
        secteur = self.detect_secteur(text)
        experience = self.extract_experience(text)
        competences = self.extract_competences(text, secteur)
        
        # Extrait le titre (première ligne non vide généralement)
        lines = text.split('\n')
        titre = "Poste " + secteur.title()
        for line in lines:
            if len(line.strip()) > 10 and not line.strip().isdigit():
                titre = line.strip().title()[:50]
                break
        
        return {
            "id": filename.replace('.pdf', ''),
            "filename": filename,
            "titre": titre,
            "competences": competences,
            "secteur": secteur,
            "experience": f"{experience}-{experience+2} ans" if experience > 0 else "Débutant accepté"
        }

    def scan_folder(self, folder_path: str, file_type: str) -> List[str]:
        """Scanne un dossier pour les fichiers PDF"""
        pdf_files = []
        if not os.path.exists(folder_path):
            print(f"❌ Dossier non trouvé: {folder_path}")
            return pdf_files
        
        for file in os.listdir(folder_path):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(folder_path, file))
        
        print(f"✅ {len(pdf_files)} fichiers {file_type} trouvés")
        return pdf_files

    def perform_matching(self, candidate: Dict, jobs: List[Dict]) -> List[Dict]:
        """Effectue le matching via l'API SuperSmartMatch V2.1"""
        try:
            payload = {
                "candidate": candidate,
                "jobs": jobs,
                "algorithm": "enhanced-v2",
                "options": {"include_details": True}
            }
            
            response = requests.post(
                f"{self.api_base}/match", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur API matching: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur matching: {e}")
            self.stats["errors"] += 1
            return None

    def generate_reports(self, results: List[Dict]) -> None:
        """Génère les rapports CSV et HTML"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Prépare les données pour le CSV
        csv_data = []
        for result in results:
            cv_name = result["cv"]["filename"]
            for match in result["matches"]:
                csv_data.append({
                    "CV": cv_name,
                    "CV_Secteur": result["cv"]["secteur"],
                    "CV_Experience": result["cv"]["annees_experience"],
                    "Job": match["job"]["filename"],
                    "Job_Secteur": match["job"]["secteur"],
                    "Job_Titre": match["job"]["titre"],
                    "Score": match["score"],
                    "Détails": match.get("details", ""),
                    "Timestamp": timestamp
                })
        
        # Export CSV
        df = pd.DataFrame(csv_data)
        csv_file = f"resultats_matching_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"📊 CSV exporté: {csv_file}")
        
        # Génère le rapport HTML
        self.generate_html_report(results, csv_data, timestamp)

    def generate_html_report(self, results: List[Dict], csv_data: List[Dict], timestamp: str) -> None:
        """Génère un rapport HTML détaillé"""
        # Calculs statistiques
        scores = [item["Score"] for item in csv_data]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        # Top 10 matches
        top_matches = sorted(csv_data, key=lambda x: x["Score"], reverse=True)[:10]
        worst_matches = sorted(csv_data, key=lambda x: x["Score"])[:10]
        
        # Distribution par secteur
        secteur_stats = {}
        for item in csv_data:
            secteur = item["CV_Secteur"]
            if secteur not in secteur_stats:
                secteur_stats[secteur] = {"count": 0, "avg_score": 0, "scores": []}
            secteur_stats[secteur]["count"] += 1
            secteur_stats[secteur]["scores"].append(item["Score"])
        
        for secteur in secteur_stats:
            scores_list = secteur_stats[secteur]["scores"]
            secteur_stats[secteur]["avg_score"] = sum(scores_list) / len(scores_list)
        
        # Template HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Rapport SuperSmartMatch V2.1 - {timestamp}</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        .score-high {{ background-color: #2ecc71; color: white; }}
        .score-medium {{ background-color: #f39c12; color: white; }}
        .score-low {{ background-color: #e74c3c; color: white; }}
        .section {{ margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SuperSmartMatch V2.1 - Rapport de Test Massif</h1>
        <p>Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
        <p>Durée totale: {time.time() - self.stats['start_time']:.1f} secondes</p>
    </div>

    <div class="stats">
        <div class="stat-box">
            <div class="stat-value">{self.stats['cvs_processed']}</div>
            <div>CVs traités</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{self.stats['jobs_processed']}</div>
            <div>Fiches de poste</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{self.stats['total_matches']}</div>
            <div>Matchings réalisés</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{avg_score:.1f}%</div>
            <div>Score moyen</div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Statistiques Générales</h2>
        <table>
            <tr><th>Métrique</th><th>Valeur</th></tr>
            <tr><td>Score Maximum</td><td>{max_score:.1f}%</td></tr>
            <tr><td>Score Minimum</td><td>{min_score:.1f}%</td></tr>
            <tr><td>Score Moyen</td><td>{avg_score:.1f}%</td></tr>
            <tr><td>Erreurs</td><td>{self.stats['errors']}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>🏆 Top 10 Meilleurs Matchings</h2>
        <table>
            <tr><th>Rang</th><th>CV</th><th>Poste</th><th>Score</th><th>Secteurs</th></tr>
        """
        
        for i, match in enumerate(top_matches, 1):
            score_class = "score-high" if match["Score"] >= 70 else "score-medium" if match["Score"] >= 40 else "score-low"
            html_content += f"""
            <tr>
                <td>{i}</td>
                <td>{match["CV"]}</td>
                <td>{match["Job_Titre"]}</td>
                <td class="{score_class}">{match["Score"]:.1f}%</td>
                <td>{match["CV_Secteur"]} → {match["Job_Secteur"]}</td>
            </tr>
            """
        
        html_content += """
        </table>
    </div>

    <div class="section">
        <h2>📉 Top 10 Pires Matchings</h2>
        <table>
            <tr><th>Rang</th><th>CV</th><th>Poste</th><th>Score</th><th>Secteurs</th></tr>
        """
        
        for i, match in enumerate(worst_matches, 1):
            score_class = "score-high" if match["Score"] >= 70 else "score-medium" if match["Score"] >= 40 else "score-low"
            html_content += f"""
            <tr>
                <td>{i}</td>
                <td>{match["CV"]}</td>
                <td>{match["Job_Titre"]}</td>
                <td class="{score_class}">{match["Score"]:.1f}%</td>
                <td>{match["CV_Secteur"]} → {match["Job_Secteur"]}</td>
            </tr>
            """
        
        html_content += """
        </table>
    </div>

    <div class="section">
        <h2>🎯 Analyse par Secteur</h2>
        <table>
            <tr><th>Secteur</th><th>Nombre CVs</th><th>Score Moyen</th></tr>
        """
        
        for secteur, stats in sorted(secteur_stats.items(), key=lambda x: x[1]["avg_score"], reverse=True):
            html_content += f"""
            <tr>
                <td>{secteur.title()}</td>
                <td>{stats["count"]}</td>
                <td>{stats["avg_score"]:.1f}%</td>
            </tr>
            """
        
        html_content += """
        </table>
    </div>

    <div class="section">
        <h2>💡 Recommandations</h2>
        <ul>
        """
        
        # Recommandations automatiques
        if avg_score < 40:
            html_content += "<li>Score moyen faible: vérifier la cohérence des secteurs détectés</li>"
        if self.stats["errors"] > 0:
            html_content += f"<li>{self.stats['errors']} erreurs détectées: vérifier les logs</li>"
        if len(set(item["CV_Secteur"] for item in csv_data)) < 3:
            html_content += "<li>Peu de diversité sectorielle: ajouter des CVs d'autres secteurs</li>"
        
        html_content += """
        </ul>
    </div>

    <footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">
        <p>Généré par SuperSmartMatch V2.1 Mass Tester - Enhanced Algorithm</p>
    </footer>
</body>
</html>
        """
        
        html_file = f"rapport_matching_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Rapport HTML généré: {html_file}")

    def run_mass_test(self) -> None:
        """Lance le test massif complet"""
        self.stats["start_time"] = time.time()
        
        print("\n🚀 DÉBUT DU TEST MASSIF SUPERSMARTMATCH V2.1")
        print("=" * 60)
        
        # 1. Vérification API
        if not self.check_api_health():
            print("❌ Test annulé: API non disponible")
            return
        
        # 2. Scan des dossiers
        print(f"\n🔍 Scanning {self.cv_folder}...")
        cv_files = self.scan_folder(self.cv_folder, "CV")
        
        print(f"\n🔍 Scanning {self.job_folder}...")
        job_files = self.scan_folder(self.job_folder, "fiche de poste")
        
        if not cv_files or not job_files:
            print("❌ Aucun fichier trouvé, test annulé")
            return
        
        print(f"\n🧠 Traitement prévu: {len(cv_files)} CVs × {len(job_files)} postes = {len(cv_files) * len(job_files)} matchings")
        
        # 3. Parse des CVs
        print(f"\n📄 Traitement des CVs...")
        cvs_data = []
        for i, cv_file in enumerate(cv_files, 1):
            print(f"📄 Processing CV {i}/{len(cv_files)}: {Path(cv_file).name}")
            cv_data = self.parse_cv(cv_file)
            if cv_data:
                cvs_data.append(cv_data)
                self.stats["cvs_processed"] += 1
        
        # 4. Parse des fiches de poste
        print(f"\n📋 Traitement des fiches de poste...")
        jobs_data = []
        for i, job_file in enumerate(job_files, 1):
            print(f"📋 Processing Job {i}/{len(job_files)}: {Path(job_file).name}")
            job_data = self.parse_job(job_file)
            if job_data:
                jobs_data.append(job_data)
                self.stats["jobs_processed"] += 1
        
        # 5. Matchings massifs
        print(f"\n🎯 Exécution des matchings...")
        results = []
        total_matches = len(cvs_data) * len(jobs_data)
        
        for i, cv in enumerate(cvs_data, 1):
            print(f"🧠 Matching CV {i}/{len(cvs_data)}: {cv['filename']}")
            
            # Faire matching avec tous les jobs
            matching_result = self.perform_matching(cv, jobs_data)
            if matching_result:
                results.append({
                    "cv": cv,
                    "matches": matching_result.get("matches", [])
                })
                self.stats["total_matches"] += len(jobs_data)
        
        # 6. Génération des rapports
        print(f"\n📊 Génération des rapports...")
        self.generate_reports(results)
        
        # 7. Résumé final
        duration = time.time() - self.stats["start_time"]
        print(f"\n✅ TEST MASSIF TERMINÉ!")
        print(f"⏱️  Durée totale: {duration:.1f} secondes")
        print(f"📄 CVs traités: {self.stats['cvs_processed']}")
        print(f"📋 Jobs traités: {self.stats['jobs_processed']}")
        print(f"🎯 Matchings réalisés: {self.stats['total_matches']}")
        print(f"❌ Erreurs: {self.stats['errors']}")
        print(f"\n📊 Secteurs détectés:")
        for secteur, count in self.stats["secteurs_detected"].items():
            print(f"   {secteur}: {count} CVs")


def main():
    """Point d'entrée principal"""
    print("🚀 SuperSmartMatch V2.1 - Mass Testing Tool")
    print("=" * 50)
    
    # Vérification des dépendances
    try:
        import pandas as pd
        print("✅ pandas disponible")
    except ImportError:
        print("❌ pandas requis: pip install pandas")
        return
    
    # Lance le test
    tester = SuperSmartMatchTester()
    tester.run_mass_test()


if __name__ == "__main__":
    main()
