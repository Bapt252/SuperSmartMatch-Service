#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test immédiat pour identifier le problème de scoring Zachary

Lance le debugger et affiche les résultats de façon claire.
Utilisation: python debug_zachary_now.py
"""

import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.scoring_debugger import ScoringDebugger

def main():
    """Lance le debug immédiat du cas Zachary"""
    
    print("🔧 SuperSmartMatch V2.1 - Debug Immédiat du Cas Zachary")
    print("=" * 80)
    print("Objectif: Identifier pourquoi le score reste à 79% au lieu de 25%")
    print("=" * 80)
    print()
    
    try:
        # Initialiser le debugger
        debugger = ScoringDebugger()
        
        # Lancer le debug complet
        debug_result = debugger.run_comprehensive_debug()
        
        print("\n" + "="*80)
        print("🎯 ANALYSE DES RÉSULTATS")
        print("="*80)
        
        # Analyser les issues trouvées
        if debug_result['issues_found']:
            print(f"❌ {len(debug_result['issues_found'])} problème(s) identifié(s):")
            print()
            
            for i, issue in enumerate(debug_result['issues_found'], 1):
                print(f"{i}. 🚨 {issue['type'].replace('_', ' ').title()}")
                print(f"   Actuel: {issue['current']}")
                print(f"   Attendu: {issue['expected']}")
                print(f"   Impact: {issue['impact']}")
                print()
        else:
            print("✅ Aucun problème détecté - Le scoring fonctionne correctement!")
            print()
        
        # Afficher les recommandations
        if debug_result['recommendations']:
            print("🔧 ACTIONS CORRECTIVES RECOMMANDÉES:")
            print("-" * 50)
            
            for i, rec in enumerate(debug_result['recommendations'], 1):
                priority_emoji = {
                    'CRITICAL': '🔥',
                    'HIGH': '⚠️',
                    'MEDIUM': '📋',
                    'LOW': '💡'
                }.get(rec['priority'], '📝')
                
                print(f"{i}. {priority_emoji} [{rec['priority']}] {rec['action']}")
                print(f"   Implémentation: {rec['implementation']}")
                if 'code' in rec:
                    print(f"   Code: {rec['code']}")
                print()
        
        # Résumé exécutif
        print("="*80)
        print("📊 RÉSUMÉ EXÉCUTIF")
        print("="*80)
        
        final_score = debug_result['steps'].get('final_calculation', {}).get('final_percentage', 'N/A')
        target_score = debug_result['steps'].get('final_calculation', {}).get('target_percentage', 25)
        
        print(f"Score actuel calculé: {final_score}%")
        print(f"Score cible: ≤ {target_score}%")
        
        if isinstance(final_score, (int, float)) and final_score > target_score:
            deviation = final_score - target_score
            print(f"Écart: +{deviation:.1f}% (PROBLÈME)")
            print()
            print("🔴 STATUT: CORRECTION REQUISE")
            print("👉 Suivre les recommandations ci-dessus pour corriger le problème")
        else:
            print("🟢 STATUT: OBJECTIF ATTEINT")
            print("👉 Le système fonctionne comme attendu")
        
        print()
        print("="*80)
        print("🚀 Prêt à implémenter les corrections? Suivez le plan d'amélioration!")
        print("="*80)
        
        return len(debug_result['issues_found']) == 0
        
    except Exception as e:
        print(f"💥 ERREUR LORS DU DEBUG: {str(e)}")
        print("Vérifiez que tous les modules sont correctement installés.")
        return False

def quick_matrix_check():
    """Vérification rapide de la matrice de compatibilité"""
    
    print("\n🔍 VÉRIFICATION RAPIDE DE LA MATRICE")
    print("-" * 50)
    
    try:
        from utils.sector_analyzer import SectorAnalyzer
        
        analyzer = SectorAnalyzer()
        commercial_juridique = analyzer.get_compatibility_score('commercial', 'juridique')
        
        print(f"Score commercial → juridique: {commercial_juridique:.3f} ({commercial_juridique*100:.1f}%)")
        
        if commercial_juridique <= 0.15:
            print("✅ Matrice correcte (≤ 15%)")
        elif commercial_juridique <= 0.25:
            print("⚠️ Matrice acceptable mais peut être améliorée (≤ 25%)")
        else:
            print(f"❌ Matrice problématique (> 25%) - CORRECTION REQUISE")
            
        return commercial_juridique <= 0.25
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        return False

if __name__ == '__main__':
    print()
    
    # Vérification rapide de la matrice
    matrix_ok = quick_matrix_check()
    
    print()
    
    # Debug complet
    debug_ok = main()
    
    # Code de sortie
    if matrix_ok and debug_ok:
        print("\n🎉 SUCCÈS: Tous les tests passent!")
        exit(0)
    else:
        print("\n⚠️ ATTENTION: Des corrections sont nécessaires.")
        exit(1)
