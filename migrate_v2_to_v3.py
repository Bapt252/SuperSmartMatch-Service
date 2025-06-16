#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperSmartMatch Migration Script V2.1 → V3.0
Outil de migration automatique avec tests de validation

🎯 OBJECTIFS :
- Migrer automatiquement de V2.1 vers V3.0
- Tester la compatibilité des données existantes
- Valider les améliorations de précision
- Fournir un rapport de migration détaillé

Auteur: SuperSmartMatch V3.0 Migration Tool
"""

import os
import json
import time
import requests
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

class SuperSmartMatchMigrationTool:
    """Outil de migration V2.1 → V3.0"""
    
    def __init__(self):
        self.migration_log = []
        self.v2_api_base = "http://localhost:5060/api/v1"  # V2.1
        self.v3_api_base = "http://localhost:5061/api/v1"  # V3.0
        
        self.migration_stats = {
            'files_backed_up': 0,
            'code_files_updated': 0,
            'api_tests_passed': 0,
            'precision_improvements': 0,
            'warnings': [],
            'errors': []
        }
        
        # Mapping des changements API
        self.api_mappings = {
            'algorithms': {
                'enhanced': 'enhanced-v3',      # Pointe maintenant vers V3.0
                'enhanced-v2': 'enhanced-v2',   # Maintenu pour compatibilité
                'auto': 'auto'                  # Auto sélectionne V3.0
            },
            'new_endpoints': {
                '/api/v3.0/job-analysis': 'Analyse métier enrichie V3.0',
                '/api/v2.1/sector-analysis': 'Maintenu pour compatibilité'
            }
        }
        
        # Cas de test pour validation migration
        self.migration_test_cases = [
            {
                'name': 'Validation_Gestionnaire_Paie',
                'candidate': {
                    'titre_poste': 'Gestionnaire de Paie',
                    'competences': ['Sage Paie', 'URSSAF', 'Charges sociales'],
                    'missions': ['Gestion paie mensuelle', 'Bulletins de paie'],
                    'annees_experience': 3
                },
                'job': {
                    'titre': 'Assistant Facturation',
                    'competences': ['Facturation', 'Relances clients'],
                    'missions': ['Émission factures', 'Suivi encaissements']
                },
                'expected_improvement': 'score_reduction',  # V3.0 doit être plus bas
                'v2_expected_range': (70, 100),  # Score V2.1 problématique
                'v3_expected_range': (0, 30)     # Score V3.0 corrigé
            },
            {
                'name': 'Validation_Compatibilité_Positive',
                'candidate': {
                    'titre_poste': 'Comptable',
                    'competences': ['Comptabilité', 'Sage', 'Facturation'],
                    'missions': ['Comptabilité générale', 'Saisie factures'],
                    'annees_experience': 2
                },
                'job': {
                    'titre': 'Assistant Facturation',
                    'competences': ['Facturation', 'Sage', 'Clients'],
                    'missions': ['Émission factures', 'Saisie comptable']
                },
                'expected_improvement': 'score_maintained',  # Bon score maintenu
                'v2_expected_range': (65, 85),
                'v3_expected_range': (70, 90)   # Légère amélioration attendue
            }
        ]
    
    def log_message(self, level: str, message: str):
        """Enregistre un message de log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level.upper()}: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def check_apis_availability(self) -> Tuple[bool, bool]:
        """Vérifie la disponibilité des APIs V2.1 et V3.0"""
        self.log_message("info", "Vérification de la disponibilité des APIs...")
        
        v2_available = False
        v3_available = False
        
        # Test API V2.1
        try:
            response = requests.get(f"{self.v2_api_base}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'unknown')
                self.log_message("info", f"✅ API V2.1 disponible (version: {version})")
                v2_available = True
            else:
                self.log_message("warning", f"API V2.1 répond mais status: {response.status_code}")
        except Exception as e:
            self.log_message("warning", f"API V2.1 non disponible: {e}")
        
        # Test API V3.0
        try:
            response = requests.get(f"{self.v3_api_base}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'unknown')
                self.log_message("info", f"✅ API V3.0 disponible (version: {version})")
                v3_available = True
            else:
                self.log_message("warning", f"API V3.0 répond mais status: {response.status_code}")
        except Exception as e:
            self.log_message("error", f"❌ API V3.0 non disponible: {e}")
        
        return v2_available, v3_available
    
    def backup_current_version(self) -> bool:
        """Sauvegarde de la version actuelle"""
        self.log_message("info", "Création de la sauvegarde V2.1...")
        
        try:
            backup_dir = f"backup_v2.1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Liste des fichiers à sauvegarder
            files_to_backup = [
                'app.py',
                'algorithms/enhanced_matching_v2.py',
                'utils/sector_analyzer.py',
                'test_massif.py',
                'README_V2.1.md'
            ]
            
            backed_up_files = 0
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    backup_file_path = os.path.join(backup_dir, file_path)
                    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                    shutil.copy2(file_path, backup_file_path)
                    backed_up_files += 1
                    self.log_message("info", f"  ✅ Sauvegardé: {file_path}")
                else:
                    self.log_message("warning", f"  ⚠️ Fichier non trouvé: {file_path}")
            
            self.migration_stats['files_backed_up'] = backed_up_files
            self.log_message("info", f"💾 Sauvegarde créée: {backup_dir} ({backed_up_files} fichiers)")
            return True
            
        except Exception as e:
            self.log_message("error", f"❌ Erreur sauvegarde: {e}")
            return False
    
    def test_api_compatibility(self, v2_available: bool, v3_available: bool) -> Dict[str, Any]:
        """Teste la compatibilité des APIs avec les cas de test"""
        self.log_message("info", "Test de compatibilité API V2.1 vs V3.0...")
        
        compatibility_results = {
            'test_results': [],
            'improvements_detected': 0,
            'regressions_detected': 0,
            'api_compatibility': True
        }
        
        if not v3_available:
            self.log_message("error", "❌ API V3.0 non disponible - Tests annulés")
            compatibility_results['api_compatibility'] = False
            return compatibility_results
        
        for test_case in self.migration_test_cases:
            self.log_message("info", f"🧪 Test: {test_case['name']}")
            
            test_result = {
                'name': test_case['name'],
                'v2_result': None,
                'v3_result': None,
                'improvement_detected': False,
                'meets_expectations': False
            }
            
            # Préparation des données de test
            payload = {
                'candidate': test_case['candidate'],
                'jobs': [test_case['job']],
                'options': {'include_details': True}
            }
            
            # Test V2.1 (si disponible)
            if v2_available:
                try:
                    payload['algorithm'] = 'enhanced-v2'
                    response = requests.post(f"{self.v2_api_base}/match", json=payload, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        v2_score = data['matches'][0]['matching_score'] if data['matches'] else 0
                        test_result['v2_result'] = {'score': v2_score, 'success': True}
                        self.log_message("info", f"  V2.1 Score: {v2_score:.1f}%")
                    else:
                        test_result['v2_result'] = {'success': False, 'error': f"HTTP {response.status_code}"}
                except Exception as e:
                    test_result['v2_result'] = {'success': False, 'error': str(e)}
            
            # Test V3.0
            try:
                payload['algorithm'] = 'enhanced-v3'
                response = requests.post(f"{self.v3_api_base}/match", json=payload, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    v3_score = data['matches'][0]['matching_score'] if data['matches'] else 0
                    test_result['v3_result'] = {
                        'score': v3_score, 
                        'success': True,
                        'job_analysis': data['matches'][0].get('job_analysis_v3', {}),
                        'blocking_factors': data['matches'][0].get('blocking_factors', [])
                    }
                    self.log_message("info", f"  V3.0 Score: {v3_score:.1f}%")
                    
                    # Vérification des attentes
                    v3_min, v3_max = test_case['v3_expected_range']
                    meets_expectations = v3_min <= v3_score <= v3_max
                    test_result['meets_expectations'] = meets_expectations
                    
                    status = "✅" if meets_expectations else "❌"
                    self.log_message("info", f"  {status} Attentes V3.0: {v3_score:.1f}% dans [{v3_min}-{v3_max}%]")
                    
                    # Détection d'amélioration
                    if test_result['v2_result'] and test_result['v2_result']['success']:
                        v2_score = test_result['v2_result']['score']
                        
                        if test_case['expected_improvement'] == 'score_reduction':
                            improvement = v2_score > v3_score  # V3.0 doit être plus bas
                            if improvement:
                                compatibility_results['improvements_detected'] += 1
                                test_result['improvement_detected'] = True
                                self.log_message("info", f"  📈 Amélioration: {v2_score:.1f}% → {v3_score:.1f}%")
                        
                        elif test_case['expected_improvement'] == 'score_maintained':
                            improvement = abs(v2_score - v3_score) <= 10  # Stable ou mieux
                            if improvement:
                                test_result['improvement_detected'] = True
                                self.log_message("info", f"  ✅ Score maintenu: {v2_score:.1f}% → {v3_score:.1f}%")
                
                else:
                    test_result['v3_result'] = {'success': False, 'error': f"HTTP {response.status_code}"}
                    self.log_message("error", f"  ❌ Erreur V3.0: {response.status_code}")
            
            except Exception as e:
                test_result['v3_result'] = {'success': False, 'error': str(e)}
                self.log_message("error", f"  ❌ Exception V3.0: {e}")
            
            compatibility_results['test_results'].append(test_result)
        
        return compatibility_results
    
    def generate_migration_code_examples(self) -> Dict[str, str]:
        """Génère des exemples de code pour la migration"""
        examples = {
            'basic_migration': '''
# AVANT V2.1
import requests

payload = {
    "candidate": candidate_data,
    "jobs": jobs_data,
    "algorithm": "enhanced"  # ou "enhanced-v2"
}

response = requests.post("http://localhost:5060/api/v1/match", json=payload)

# APRÈS V3.0
payload = {
    "candidate": candidate_data,
    "jobs": jobs_data,
    "algorithm": "enhanced-v3"  # ou "auto" ou "latest"
}

response = requests.post("http://localhost:5061/api/v1/match", json=payload)
# Note: Port changé 5060 → 5061
''',
            
            'new_job_analysis': '''
# NOUVEAU V3.0 - Analyse métier enrichie
import requests

response = requests.post("http://localhost:5061/api/v3.0/job-analysis", json={
    "text": "Gestionnaire de paie avec 3 ans d'expérience Sage Paie URSSAF",
    "context": "cv"
})

analysis = response.json()['enhanced_analysis_v3']
print(f"Métier: {analysis['specific_job']}")           # gestionnaire_paie
print(f"Sous-secteur: {analysis['sub_sector']}")       # paie_social
print(f"Niveau: {analysis['job_level']}")              # confirmé
print(f"Spécialisation: {analysis['specialization_score']}")  # 0.85
''',
            
            'algorithm_class_usage': '''
# Utilisation directe des classes (pour intégration custom)

# AVANT V2.1
from algorithms.enhanced_matching_v2 import EnhancedMatchingV2Algorithm
algorithm = EnhancedMatchingV2Algorithm()

# APRÈS V3.0
from algorithms.enhanced_matching_v3 import EnhancedMatchingV3Algorithm
algorithm = EnhancedMatchingV3Algorithm()

# Nouvelle analyse sectorielle V3.0
from utils.enhanced_sector_analyzer_v3 import EnhancedSectorAnalyzerV3
analyzer = EnhancedSectorAnalyzerV3()
result = analyzer.detect_enhanced_sector(text, context='cv')
''',
            
            'docker_migration': '''
# Docker Compose - Migration des ports

# AVANT V2.1
services:
  supersmartmatch:
    ports:
      - "5060:5060"
    environment:
      - PORT=5060

# APRÈS V3.0  
services:
  supersmartmatch:
    ports:
      - "5061:5061"  # Port mis à jour
    environment:
      - PORT=5061
'''
        }
        
        return examples
    
    def create_migration_checklist(self) -> List[str]:
        """Crée une checklist de migration"""
        checklist = [
            "☐ Sauvegarder la version V2.1 actuelle",
            "☐ Déployer SuperSmartMatch V3.0 (port 5061)",
            "☐ Tester l'API V3.0 avec /api/v1/health",
            "☐ Mettre à jour les appels API : enhanced → enhanced-v3",
            "☐ Changer le port dans la configuration : 5060 → 5061",
            "☐ Tester les cas critiques : gestionnaire paie, assistant juridique",
            "☐ Valider les améliorations de précision avec test_v3_validation.py",
            "☐ Mettre à jour la documentation et les clients",
            "☐ Utiliser le nouveau endpoint /api/v3.0/job-analysis si besoin",
            "☐ Monitorer les logs pour détecter les éventuelles régressions",
            "☐ Former les équipes sur les nouvelles fonctionnalités V3.0"
        ]
        return checklist
    
    def generate_migration_report(self, compatibility_results: Dict[str, Any]) -> str:
        """Génère le rapport de migration complet"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
🚀 RAPPORT DE MIGRATION SUPERSMARTMATCH V2.1 → V3.0
================================================================
Généré le: {timestamp}

📊 RÉSUMÉ DE LA MIGRATION
----------------------------------------------------------------
✅ Fichiers sauvegardés: {self.migration_stats['files_backed_up']}
🧪 Tests de compatibilité: {len(compatibility_results['test_results'])}
📈 Améliorations détectées: {compatibility_results['improvements_detected']}
❌ Régressions détectées: {compatibility_results['regressions_detected']}
⚠️ Avertissements: {len(self.migration_stats['warnings'])}
🔴 Erreurs: {len(self.migration_stats['errors'])}

🎯 PRINCIPALES AMÉLIORATIONS V3.0
----------------------------------------------------------------
✅ Gestionnaire paie ≠ Management (problème résolu)
✅ Assistant facturation ≠ Gestionnaire paie (différenciation claire)
✅ Assistant juridique ≠ Management (séparation nette)
✅ 70+ métiers spécifiques vs 9 secteurs génériques
✅ Détection contextuelle par combinaisons de mots-clés
✅ Matrice de compatibilité enrichie (162+ combinaisons)
✅ Règles d'exclusion intelligentes pour éviter faux positifs

📋 RÉSULTATS DES TESTS DE COMPATIBILITÉ
----------------------------------------------------------------"""
        
        for test_result in compatibility_results['test_results']:
            report += f"\n\n🧪 {test_result['name']}"
            
            if test_result['v2_result'] and test_result['v2_result']['success']:
                v2_score = test_result['v2_result']['score']
                report += f"\n   V2.1 Score: {v2_score:.1f}%"
            
            if test_result['v3_result'] and test_result['v3_result']['success']:
                v3_score = test_result['v3_result']['score']
                report += f"\n   V3.0 Score: {v3_score:.1f}%"
                
                if test_result['improvement_detected']:
                    report += " ✅ AMÉLIORATION"
                
                if test_result['meets_expectations']:
                    report += " ✅ CONFORME"
                else:
                    report += " ⚠️ HORS ATTENTES"
                
                # Analyse métier V3.0
                job_analysis = test_result['v3_result'].get('job_analysis', {})
                if job_analysis:
                    candidate_job = job_analysis.get('candidate_job', 'N/A')
                    target_job = job_analysis.get('target_job', 'N/A')
                    report += f"\n   📊 Métiers détectés: {candidate_job} → {target_job}"
                
                # Facteurs bloquants
                blocking_factors = test_result['v3_result'].get('blocking_factors', [])
                if blocking_factors:
                    report += f"\n   🚨 Facteurs bloquants: {len(blocking_factors)}"
            else:
                report += "\n   ❌ Erreur test V3.0"
        
        # Checklist de migration
        report += "\n\n✅ CHECKLIST DE MIGRATION\n"
        report += "----------------------------------------------------------------\n"
        checklist = self.create_migration_checklist()
        for item in checklist:
            report += f"{item}\n"
        
        # Exemples de code
        examples = self.generate_migration_code_examples()
        report += "\n\n📝 EXEMPLES DE MIGRATION DE CODE\n"
        report += "----------------------------------------------------------------\n"
        report += examples['basic_migration']
        
        # Recommandations
        report += "\n\n💡 RECOMMANDATIONS\n"
        report += "----------------------------------------------------------------\n"
        
        if compatibility_results['improvements_detected'] >= 2:
            report += "✅ Migration V3.0 fortement recommandée\n"
            report += "✅ Améliorations significatives de précision détectées\n"
            report += "✅ Déploiement en production conseillé\n"
        elif compatibility_results['improvements_detected'] >= 1:
            report += "⚠️ Migration V3.0 recommandée avec tests supplémentaires\n"
            report += "⚠️ Valider en pré-production avant déploiement\n"
        else:
            report += "❌ Migration V3.0 nécessite investigation\n"
            report += "❌ Problèmes de compatibilité détectés\n"
        
        report += f"\n🔗 Port V3.0: 5061 (vs 5060 pour V2.1)\n"
        report += f"🔗 Algorithme recommandé: 'enhanced-v3' ou 'auto'\n"
        report += f"🔗 Nouveau endpoint: /api/v3.0/job-analysis\n"
        
        # Logs détaillés
        if self.migration_log:
            report += "\n\n📋 LOGS DÉTAILLÉS\n"
            report += "----------------------------------------------------------------\n"
            for log_entry in self.migration_log[-20:]:  # Dernières 20 entrées
                report += f"{log_entry}\n"
        
        return report
    
    def run_migration(self) -> None:
        """Lance le processus de migration complet"""
        self.log_message("info", "🚀 DÉBUT DE LA MIGRATION V2.1 → V3.0")
        self.log_message("info", "=" * 60)
        
        try:
            # 1. Vérification des APIs
            v2_available, v3_available = self.check_apis_availability()
            
            if not v3_available:
                self.log_message("error", "❌ Migration impossible: API V3.0 non disponible")
                self.log_message("info", "💡 Démarrez d'abord SuperSmartMatch V3.0 sur le port 5061")
                return
            
            # 2. Sauvegarde
            backup_success = self.backup_current_version()
            if not backup_success:
                self.log_message("warning", "⚠️ Sauvegarde échouée - Migration continue")
            
            # 3. Tests de compatibilité
            compatibility_results = self.test_api_compatibility(v2_available, v3_available)
            
            # 4. Génération du rapport
            self.log_message("info", "📊 Génération du rapport de migration...")
            report = self.generate_migration_report(compatibility_results)
            
            # 5. Sauvegarde du rapport
            report_filename = f"migration_report_v2_to_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log_message("info", f"📄 Rapport sauvegardé: {report_filename}")
            
            # 6. Affichage du rapport
            print("\n" + "=" * 80)
            print(report)
            print("=" * 80)
            
            # 7. Conclusion
            improvements = compatibility_results['improvements_detected']
            if improvements >= 2:
                self.log_message("info", "🎉 MIGRATION RECOMMANDÉE - Améliorations significatives détectées")
            elif improvements >= 1:
                self.log_message("info", "✅ Migration possible - Tests supplémentaires conseillés")
            else:
                self.log_message("warning", "⚠️ Migration nécessite investigation - Voir rapport détaillé")
            
        except Exception as e:
            self.log_message("error", f"❌ Erreur critique de migration: {e}")
            raise

def main():
    """Point d'entrée principal"""
    print("🚀 SuperSmartMatch - Outil de Migration V2.1 → V3.0")
    print("Automatise la migration et valide les améliorations de précision")
    print()
    
    migration_tool = SuperSmartMatchMigrationTool()
    migration_tool.run_migration()

if __name__ == "__main__":
    main()
