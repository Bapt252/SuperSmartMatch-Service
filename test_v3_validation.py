#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validation SuperSmartMatch V3.0 
Test des améliorations de précision métier

🎯 OBJECTIFS DE VALIDATION :
- Tester la résolution des problèmes identifiés
- Comparer V2.1 vs V3.0 sur cas problématiques
- Valider la granularité métier fine
- Mesurer les performances

Auteur: SuperSmartMatch V3.0 Validation
"""

import requests
import json
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime

class SuperSmartMatchV3Validator:
    """Validateur des améliorations V3.0"""
    
    def __init__(self, api_base: str = "http://localhost:5061/api/v1"):
        self.api_base = api_base
        self.results = {
            'test_cases': [],
            'v2_vs_v3_comparison': [],
            'performance_metrics': {},
            'validation_summary': {}
        }
        
        # Cas de test problématiques identifiés
        self.problematic_test_cases = [
            {
                'name': 'Gestionnaire_Paie_vs_Assistant_Facturation',
                'description': '🎯 CAS PRINCIPAL : Gestionnaire de paie ne doit PAS matcher avec Assistant facturation',
                'candidate': {
                    'titre_poste': 'Gestionnaire de Paie',
                    'competences': ['Sage Paie', 'DADS', 'Urssaf', 'Charges sociales', 'Bulletin de paie'],
                    'missions': [
                        'Gestion de la paie mensuelle pour 150 salariés',
                        'Établissement des bulletins de paie',
                        'Déclarations sociales URSSAF',
                        'Suivi des charges sociales'
                    ],
                    'annees_experience': 3,
                    'secteur': 'ressources humaines'
                },
                'jobs': [
                    {
                        'id': 'assistant_facturation_001',
                        'titre': 'Assistant Facturation',
                        'competences': ['Facturation', 'Relances clients', 'Recouvrement', 'Excel'],
                        'missions': [
                            'Émission des factures clients',
                            'Suivi des encaissements',
                            'Relances clients impayés',
                            'Reporting commercial'
                        ],
                        'secteur': 'comptabilité',
                        'description': 'Assistant facturation pour gestion clientèle'
                    }
                ],
                'expected_v3_score_max': 30,  # Doit être très faible
                'expected_v2_score_issue': 'high'  # V2.1 avait un score élevé problématique
            },
            {
                'name': 'Assistant_Juridique_vs_Manager',
                'description': '🎯 Assistant juridique ne doit PAS être considéré comme Manager',
                'candidate': {
                    'titre_poste': 'Assistant Juridique',
                    'competences': ['Droit des affaires', 'Rédaction juridique', 'Veille juridique'],
                    'missions': [
                        'Assistance à la rédaction de contrats',
                        'Classement et archivage de dossiers juridiques',
                        'Prise de rendez-vous clients',
                        'Saisie de données juridiques'
                    ],
                    'annees_experience': 1,
                    'secteur': 'juridique'
                },
                'jobs': [
                    {
                        'id': 'manager_equipe_001',
                        'titre': 'Manager d\'équipe',
                        'competences': ['Management', 'Leadership', 'Gestion équipe', 'Objectifs'],
                        'missions': [
                            'Encadrement d\'une équipe de 8 personnes',
                            'Définition des objectifs',
                            'Suivi de performance',
                            'Animation de réunions'
                        ],
                        'secteur': 'management',
                        'description': 'Manager opérationnel avec équipe'
                    }
                ],
                'expected_v3_score_max': 25,
                'expected_v2_score_issue': 'high'
            },
            {
                'name': 'Gestionnaire_Paie_vs_Directeur',
                'description': '🎯 Gestionnaire de paie ne doit PAS être considéré comme Directeur (management)',
                'candidate': {
                    'titre_poste': 'Gestionnaire de Paie ADP',
                    'competences': ['ADP', 'Paie', 'Silae', 'Charges sociales'],
                    'missions': [
                        'Gestionnaire de paie expérimenté ADP',
                        'Traitement paie multi-conventions',
                        'Formation utilisateurs Silae'
                    ],
                    'annees_experience': 5,
                    'secteur': 'rh'
                },
                'jobs': [
                    {
                        'id': 'directeur_001',
                        'titre': 'Directeur Régional',
                        'competences': ['Direction', 'Stratégie', 'Management', 'P&L'],
                        'missions': [
                            'Direction d\'une région de 50 personnes',
                            'Définition de la stratégie régionale',
                            'Gestion du P&L',
                            'Développement commercial'
                        ],
                        'secteur': 'direction',
                        'description': 'Directeur avec responsabilité P&L'
                    }
                ],
                'expected_v3_score_max': 20,
                'expected_v2_score_issue': 'high'
            },
            {
                'name': 'Comptable_vs_Assistant_Facturation',
                'description': '✅ CAS POSITIF : Comptable DOIT bien matcher avec Assistant facturation',
                'candidate': {
                    'titre_poste': 'Comptable',
                    'competences': ['Comptabilité générale', 'Sage', 'Facturation', 'TVA'],
                    'missions': [
                        'Comptabilité générale',
                        'Saisie factures fournisseurs',
                        'Rapprochements bancaires',
                        'Déclarations TVA'
                    ],
                    'annees_experience': 2,
                    'secteur': 'comptabilité'
                },
                'jobs': [
                    {
                        'id': 'assistant_facturation_002',
                        'titre': 'Assistant Facturation',
                        'competences': ['Facturation', 'Sage', 'Clients', 'Excel'],
                        'missions': [
                            'Émission factures',
                            'Suivi encaissements',
                            'Saisie comptable'
                        ],
                        'secteur': 'comptabilité',
                        'description': 'Assistant facturation avec comptabilité'
                    }
                ],
                'expected_v3_score_min': 70,  # Doit être élevé
                'positive_case': True
            },
            {
                'name': 'Gestionnaire_Paie_vs_Gestionnaire_Paie',
                'description': '✅ CAS PARFAIT : Même métier doit avoir score maximum',
                'candidate': {
                    'titre_poste': 'Gestionnaire de Paie',
                    'competences': ['Sage Paie', 'DADS', 'Urssaf'],
                    'missions': ['Gestion paie mensuelle'],
                    'annees_experience': 3,
                    'secteur': 'rh'
                },
                'jobs': [
                    {
                        'id': 'gestionnaire_paie_001',
                        'titre': 'Gestionnaire de Paie Senior',
                        'competences': ['Sage Paie', 'DADS', 'Urssaf', 'Formation'],
                        'missions': ['Gestion paie', 'Formation équipe'],
                        'secteur': 'rh',
                        'description': 'Gestionnaire paie avec formation'
                    }
                ],
                'expected_v3_score_min': 90,
                'perfect_case': True
            }
        ]
    
    def test_health_api(self) -> bool:
        """Teste la disponibilité de l'API V3.0"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API V3.0 disponible - Version: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ API non disponible - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion API: {e}")
            return False
    
    def test_job_analysis_v3(self) -> Dict[str, Any]:
        """Teste le nouveau endpoint d'analyse métier V3.0"""
        print("\n🔍 Test de l'analyse métier V3.0...")
        
        test_texts = [
            {
                'text': 'Gestionnaire de paie avec 3 ans d\'expérience Sage Paie URSSAF',
                'expected_job': 'gestionnaire_paie',
                'expected_sector': 'comptabilite_finance'
            },
            {
                'text': 'Assistant facturation relances clients recouvrement',
                'expected_job': 'assistant_facturation', 
                'expected_sector': 'comptabilite_finance'
            },
            {
                'text': 'Manager d\'équipe leadership encadrement 10 personnes',
                'expected_job': 'manager',
                'expected_sector': 'management_direction'
            }
        ]
        
        results = {}
        
        for i, test in enumerate(test_texts):
            try:
                response = requests.post(
                    f"{self.api_base.replace('/v1', '')}/v3.0/job-analysis",
                    json={'text': test['text'], 'context': 'cv'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data.get('enhanced_analysis_v3', {})
                    
                    detected_job = analysis.get('specific_job', 'unknown')
                    detected_sector = analysis.get('primary_sector', 'unknown')
                    confidence = analysis.get('confidence', 0)
                    
                    success = (detected_job == test['expected_job'] and 
                              detected_sector == test['expected_sector'])
                    
                    results[f"test_{i+1}"] = {
                        'text': test['text'],
                        'expected_job': test['expected_job'],
                        'detected_job': detected_job,
                        'expected_sector': test['expected_sector'],
                        'detected_sector': detected_sector,
                        'confidence': confidence,
                        'success': success
                    }
                    
                    status = "✅" if success else "❌"
                    print(f"  {status} Test {i+1}: {detected_job} ({confidence:.2f}) vs attendu {test['expected_job']}")
                    
                else:
                    print(f"  ❌ Test {i+1}: Erreur API - {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Test {i+1}: Exception - {e}")
        
        return results
    
    def run_matching_test(self, test_case: Dict[str, Any], algorithm: str) -> Dict[str, Any]:
        """Exécute un test de matching pour un algorithme donné"""
        try:
            payload = {
                'candidate': test_case['candidate'],
                'jobs': test_case['jobs'],
                'algorithm': algorithm,
                'options': {'include_details': True}
            }
            
            start_time = time.time()
            response = requests.post(f"{self.api_base}/match", json=payload, timeout=30)
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                
                if matches:
                    top_match = matches[0]
                    score = top_match.get('matching_score', 0)
                    
                    return {
                        'success': True,
                        'score': score,
                        'execution_time_ms': execution_time,
                        'algorithm_used': data.get('algorithm_used', algorithm),
                        'match_details': top_match.get('matching_details', {}),
                        'blocking_factors': top_match.get('blocking_factors', []),
                        'recommendations': top_match.get('recommendations', []),
                        'job_analysis_v3': top_match.get('job_analysis_v3', {}),
                        'raw_response': data
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Aucun match retourné',
                        'execution_time_ms': execution_time
                    }
            else:
                return {
                    'success': False,
                    'error': f"API Error {response.status_code}: {response.text}",
                    'execution_time_ms': execution_time
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': 0
            }
    
    def compare_v2_vs_v3(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Compare les résultats V2.1 vs V3.0 pour un cas de test"""
        print(f"\n🔬 Test: {test_case['name']}")
        print(f"📝 {test_case['description']}")
        
        # Test V2.1
        print("  🔹 Test Enhanced V2.1...")
        v2_result = self.run_matching_test(test_case, 'enhanced-v2')
        
        # Test V3.0
        print("  🔹 Test Enhanced V3.0...")
        v3_result = self.run_matching_test(test_case, 'enhanced-v3')
        
        # Analyse des résultats
        comparison = {
            'test_name': test_case['name'],
            'description': test_case['description'],
            'v2_result': v2_result,
            'v3_result': v3_result,
            'improvement_analysis': {}
        }
        
        if v2_result['success'] and v3_result['success']:
            v2_score = v2_result['score']
            v3_score = v3_result['score']
            score_diff = v2_score - v3_score
            
            # Analyse selon le type de cas
            if test_case.get('positive_case'):
                # Cas positif : on veut un score élevé
                expected_min = test_case.get('expected_v3_score_min', 70)
                v3_success = v3_score >= expected_min
                status = "✅" if v3_success else "❌"
                print(f"    {status} V3.0 Score: {v3_score:.1f}% (attendu ≥{expected_min}%)")
                
            elif test_case.get('perfect_case'):
                # Cas parfait : on veut un score très élevé
                expected_min = test_case.get('expected_v3_score_min', 90)
                v3_success = v3_score >= expected_min
                status = "✅" if v3_success else "❌"
                print(f"    {status} V3.0 Score: {v3_score:.1f}% (attendu ≥{expected_min}%)")
                
            else:
                # Cas problématique : on veut un score faible
                expected_max = test_case.get('expected_v3_score_max', 30)
                v3_success = v3_score <= expected_max
                improvement = score_diff > 0  # V3 doit être plus bas que V2
                
                status = "✅" if v3_success else "❌"
                improvement_status = "📈" if improvement else "📉"
                
                print(f"    V2.1 Score: {v2_score:.1f}%")
                print(f"    {status} V3.0 Score: {v3_score:.1f}% (attendu ≤{expected_max}%)")
                print(f"    {improvement_status} Amélioration: {score_diff:+.1f} points")
                
                comparison['improvement_analysis'] = {
                    'score_reduction': score_diff,
                    'meets_expectation': v3_success,
                    'improvement_achieved': improvement,
                    'expected_max_score': expected_max
                }
        
        else:
            print("    ❌ Erreur dans un des tests")
            if not v2_result['success']:
                print(f"      V2.1 Error: {v2_result.get('error', 'Unknown')}")
            if not v3_result['success']:
                print(f"      V3.0 Error: {v3_result.get('error', 'Unknown')}")
        
        return comparison
    
    def run_performance_test(self) -> Dict[str, Any]:
        """Test des performances avec plusieurs requêtes"""
        print("\n⚡ Test de performance...")
        
        # Utilise le premier cas de test pour mesurer les performances
        test_case = self.problematic_test_cases[0]
        algorithms_to_test = ['enhanced-v2', 'enhanced-v3']
        
        performance_results = {}
        
        for algorithm in algorithms_to_test:
            print(f"  🔹 Performance {algorithm}...")
            
            times = []
            scores = []
            
            # Fait 5 requêtes pour avoir une moyenne
            for i in range(5):
                result = self.run_matching_test(test_case, algorithm)
                if result['success']:
                    times.append(result['execution_time_ms'])
                    scores.append(result['score'])
            
            if times:
                avg_time = sum(times) / len(times)
                avg_score = sum(scores) / len(scores)
                
                performance_results[algorithm] = {
                    'avg_execution_time_ms': avg_time,
                    'avg_score': avg_score,
                    'times': times,
                    'scores': scores
                }
                
                print(f"    ⏱️  Temps moyen: {avg_time:.1f}ms")
                print(f"    📊 Score moyen: {avg_score:.1f}%")
        
        return performance_results
    
    def generate_validation_report(self) -> str:
        """Génère un rapport de validation détaillé"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Calcul des statistiques globales
        total_tests = len(self.results['v2_vs_v3_comparison'])
        successful_improvements = 0
        problematic_cases_fixed = 0
        
        for comparison in self.results['v2_vs_v3_comparison']:
            if comparison['v2_result']['success'] and comparison['v3_result']['success']:
                # Cherche le cas de test correspondant
                test_case = next((tc for tc in self.problematic_test_cases 
                                if tc['name'] == comparison['test_name']), None)
                
                if test_case and not test_case.get('positive_case', False) and not test_case.get('perfect_case', False):
                    # Cas problématique
                    v3_score = comparison['v3_result']['score']
                    expected_max = test_case.get('expected_v3_score_max', 30)
                    
                    if v3_score <= expected_max:
                        problematic_cases_fixed += 1
                    
                    v2_score = comparison['v2_result']['score']
                    if v2_score > v3_score:
                        successful_improvements += 1
        
        report = f"""
🎯 RAPPORT DE VALIDATION SUPERSMARTMATCH V3.0
================================================================
Généré le: {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}

📊 RÉSUMÉ EXÉCUTIF
----------------------------------------------------------------
✅ Tests exécutés: {total_tests}
🎯 Améliorations réussies: {successful_improvements}/{total_tests}
🔧 Cas problématiques résolus: {problematic_cases_fixed}
📈 Taux de réussite: {(successful_improvements/max(total_tests,1)*100):.1f}%

🎯 VALIDATION DES PROBLÈMES IDENTIFIÉS
----------------------------------------------------------------
"""
        
        for comparison in self.results['v2_vs_v3_comparison']:
            report += f"\n📋 {comparison['test_name'].replace('_', ' ')}\n"
            report += f"   📝 {comparison['description']}\n"
            
            if comparison['v2_result']['success'] and comparison['v3_result']['success']:
                v2_score = comparison['v2_result']['score']
                v3_score = comparison['v3_result']['score']
                score_diff = v2_score - v3_score
                
                # Trouve le cas de test pour les attentes
                test_case = next((tc for tc in self.problematic_test_cases 
                                if tc['name'] == comparison['test_name']), None)
                
                if test_case:
                    if test_case.get('positive_case') or test_case.get('perfect_case'):
                        expected_min = test_case.get('expected_v3_score_min', 70)
                        success = v3_score >= expected_min
                        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
                        report += f"   {status}: Score V3.0 = {v3_score:.1f}% (attendu ≥{expected_min}%)\n"
                    else:
                        expected_max = test_case.get('expected_v3_score_max', 30)
                        success = v3_score <= expected_max
                        improvement = score_diff > 0
                        
                        status = "✅ RÉSOLU" if success else "❌ NON RÉSOLU"
                        report += f"   V2.1: {v2_score:.1f}% → V3.0: {v3_score:.1f}% (attendu ≤{expected_max}%)\n"
                        report += f"   {status}: Amélioration de {score_diff:+.1f} points\n"
            else:
                report += "   ❌ ERREUR: Test non exécutable\n"
        
        # Section performance
        if 'performance_metrics' in self.results and self.results['performance_metrics']:
            report += "\n⚡ PERFORMANCES\n"
            report += "----------------------------------------------------------------\n"
            
            for algo, metrics in self.results['performance_metrics'].items():
                report += f"{algo}: {metrics['avg_execution_time_ms']:.1f}ms (score moyen: {metrics['avg_score']:.1f}%)\n"
        
        # Recommandations
        report += "\n💡 RECOMMANDATIONS\n"
        report += "----------------------------------------------------------------\n"
        
        if problematic_cases_fixed >= 3:
            report += "✅ V3.0 résout efficacement les problèmes de précision identifiés\n"
            report += "✅ Déploiement en production recommandé\n"
            report += "✅ Mise à jour des clients vers enhanced-v3\n"
        elif problematic_cases_fixed >= 2:
            report += "⚠️ Améliorations significatives mais perfectibles\n"
            report += "🔧 Ajustements recommandés avant production\n"
        else:
            report += "❌ Problèmes de précision non résolus\n"
            report += "🔧 Révision de l'algorithme V3.0 nécessaire\n"
        
        report += f"\n📈 Utiliser l'algorithme 'enhanced-v3' pour la précision métier optimale\n"
        report += f"🔄 Endpoint V3.0: /api/v3.0/job-analysis pour analyse métier fine\n"
        
        return report
    
    def run_full_validation(self) -> None:
        """Exécute la validation complète V3.0"""
        print("🚀 VALIDATION SUPERSMARTMATCH V3.0 - PRÉCISION MÉTIER FINE")
        print("=" * 70)
        
        # 1. Test de l'API
        if not self.test_health_api():
            print("❌ Validation annulée: API non disponible")
            return
        
        # 2. Test de l'analyse métier V3.0
        job_analysis_results = self.test_job_analysis_v3()
        
        # 3. Tests de matching V2.1 vs V3.0
        print(f"\n🔬 Comparaison V2.1 vs V3.0 sur {len(self.problematic_test_cases)} cas problématiques...")
        
        for test_case in self.problematic_test_cases:
            comparison = self.compare_v2_vs_v3(test_case)
            self.results['v2_vs_v3_comparison'].append(comparison)
        
        # 4. Test de performance
        performance_metrics = self.run_performance_test()
        self.results['performance_metrics'] = performance_metrics
        
        # 5. Génération du rapport
        print("\n📊 Génération du rapport de validation...")
        report = self.generate_validation_report()
        
        # Sauvegarde du rapport
        report_filename = f"validation_v3_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 Rapport sauvegardé: {report_filename}")
        
        # Sauvegarde des résultats détaillés
        results_filename = f"validation_v3_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Résultats détaillés sauvegardés: {results_filename}")

def main():
    """Point d'entrée principal"""
    print("🎯 SuperSmartMatch V3.0 - Validation des Améliorations de Précision")
    print("Objectif: Valider la résolution des problèmes de matching identifiés")
    print()
    
    # Configuration
    api_base = "http://localhost:5061/api/v1"  # Port V3.0
    
    # Vérification préalable
    print("⚙️ Configuration:")
    print(f"   API Base: {api_base}")
    print(f"   Tests: Cas problématiques V2.1 vs améliorations V3.0")
    print()
    
    # Lancement de la validation
    validator = SuperSmartMatchV3Validator(api_base)
    validator.run_full_validation()

if __name__ == "__main__":
    main()
