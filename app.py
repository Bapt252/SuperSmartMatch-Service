#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperSmartMatch Service V2.1 - API unifiée de matching avec intelligence sectorielle

🚀 NOUVELLES FONCTIONNALITÉS V2.1 :
- Enhanced Matching V2.1 avec analyse sectorielle
- Résolution du problème critique : Commercial vs Juridique 79% -> 25%
- SectorAnalyzer avec matrice de compatibilité française
- Facteurs bloquants et recommandations intelligentes

Auteur: SuperSmartMatch V2.1 Enhanced
Version: 2.1.0
"""

import os
import time
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from typing import Dict, List, Any, Optional

# Imports des algorithmes existants
from algorithms.smart_match import SmartMatchAlgorithm
from algorithms.enhanced_matching_v2 import EnhancedMatchingV2Algorithm  # 🆕 V2.1
from algorithms.semantic_analyzer import SemanticAnalyzerAlgorithm
from algorithms.hybrid_matching import HybridMatchingAlgorithm
from algorithms.auto_selector import AutoSelectorEngine
from utils.performance_monitor import PerformanceMonitor
from utils.cache_manager import CacheManager
from utils.sector_analyzer import SectorAnalyzer  # 🆕 V2.1
from config.settings import Config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin pour le front-end

# Configuration
config = Config()
app.config.from_object(config)

# Initialisation des services
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager(config.REDIS_URL)
auto_selector = AutoSelectorEngine()
sector_analyzer = SectorAnalyzer()  # 🆕 V2.1

# Initialisation des algorithmes V2.1
algorithms = {
    'smart-match': SmartMatchAlgorithm(),
    'enhanced-v2': EnhancedMatchingV2Algorithm(),  # 🆕 V2.1 - Remplace 'enhanced'
    'semantic': SemanticAnalyzerAlgorithm(),
    'hybrid': HybridMatchingAlgorithm(),
    
    # Alias pour compatibilité
    'enhanced': EnhancedMatchingV2Algorithm(),  # Pointe vers V2.1
}

class SuperSmartMatchServiceV2:
    """
    Service principal V2.1 avec intelligence sectorielle
    """
    
    def __init__(self):
        self.algorithms = algorithms
        self.auto_selector = auto_selector
        self.performance_monitor = performance_monitor
        self.cache = cache_manager
        self.sector_analyzer = sector_analyzer  # 🆕 V2.1
        
    def match(self, candidate_data: Dict[str, Any], 
              jobs_data: List[Dict[str, Any]], 
              algorithm: str = 'auto',
              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Point d'entrée principal pour le matching unifié V2.1
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            algorithm: Algorithme à utiliser ('auto', 'enhanced-v2', etc.)
            options: Options supplémentaires
            
        Returns:
            Résultats de matching avec métadonnées V2.1
        """
        start_time = time.time()
        
        # Options par défaut
        if options is None:
            options = {}
        
        limit = options.get('limit', 10)
        include_details = options.get('include_details', True)
        performance_mode = options.get('performance_mode', 'balanced')
        
        # Génération de la clé de cache V2.1
        cache_key = self._generate_cache_key(candidate_data, jobs_data, algorithm, options)
        
        # Vérification du cache
        if performance_mode in ['fast', 'balanced']:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit pour la requête {cache_key[:8]}...")
                cached_result['cache_hit'] = True
                return cached_result
        
        # Sélection de l'algorithme V2.1
        if algorithm == 'auto':
            # Auto-sélection privilégie Enhanced V2.1 pour sa précision sectorielle
            selected_algorithm = 'enhanced-v2'
            logger.info(f"Auto-sélection V2.1: {selected_algorithm} (intelligence sectorielle)")
        else:
            selected_algorithm = algorithm
        
        # Validation de l'algorithme
        if selected_algorithm not in self.algorithms:
            return {
                'error': f"Algorithme '{selected_algorithm}' non disponible",
                'available_algorithms': list(self.algorithms.keys()),
                'recommendation': 'Utilisez "enhanced-v2" pour la précision sectorielle'
            }
        
        # Exécution du matching
        try:
            algorithm_instance = self.algorithms[selected_algorithm]
            
            # Préparation des données pour l'algorithme
            prepared_data = self._prepare_data_for_algorithm(
                candidate_data, jobs_data, selected_algorithm
            )
            
            # Exécution
            matches = algorithm_instance.calculate_matches(
                prepared_data['candidate'],
                prepared_data['jobs']
            )
            
            # Limitation du nombre de résultats
            matches = matches[:limit]
            
            # Enrichissement des résultats V2.1
            enriched_matches = self._enrich_matches_v2(
                matches, selected_algorithm, include_details
            )
            
            # Calcul des métriques de performance
            execution_time = (time.time() - start_time) * 1000  # en ms
            
            # Construction de la réponse V2.1
            result = {
                'algorithm_used': selected_algorithm,
                'execution_time_ms': round(execution_time, 2),
                'total_jobs_analyzed': len(jobs_data),
                'matches': enriched_matches,
                'performance_metrics': {
                    'cache_hit_rate': self.cache.get_hit_rate(),
                    'optimization_applied': performance_mode,
                    'total_algorithms_available': len(self.algorithms),
                    'sector_analysis_enabled': True  # 🆕 V2.1
                },
                'cache_hit': False,
                'version': '2.1.0'  # 🆕 V2.1
            }
            
            # Mise en cache du résultat
            if performance_mode in ['balanced', 'accuracy']:
                self.cache.set(cache_key, result, ttl=3600)  # 1 heure
            
            # Enregistrement des métriques
            self.performance_monitor.record_request(
                algorithm=selected_algorithm,
                execution_time=execution_time,
                job_count=len(jobs_data),
                match_count=len(enriched_matches)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du matching V2.1: {str(e)}")
            return {
                'error': f"Erreur lors du matching: {str(e)}",
                'algorithm_attempted': selected_algorithm,
                'execution_time_ms': round((time.time() - start_time) * 1000, 2),
                'version': '2.1.0'
            }
    
    def analyze_sector(self, text: str, context: str = 'general') -> Dict[str, Any]:
        """
        🆕 V2.1 - Analyse sectorielle d'un texte
        
        Args:
            text: Texte à analyser (CV ou offre d'emploi)
            context: Contexte ('cv', 'job', 'general')
            
        Returns:
            Analyse détaillée du secteur
        """
        try:
            analysis = self.sector_analyzer.detect_sector(text, context)
            
            return {
                'success': True,
                'sector_analysis': {
                    'primary_sector': analysis.primary_sector,
                    'confidence': round(analysis.confidence, 3),
                    'secondary_sectors': analysis.secondary_sectors,
                    'detected_keywords': analysis.detected_keywords,
                    'explanation': analysis.explanation
                },
                'sector_info': self.sector_analyzer.get_sector_info(),
                'version': '2.1.0'
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse sectorielle: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'version': '2.1.0'
            }
    
    def compare_algorithms(self, candidate_data: Dict[str, Any], 
                          jobs_data: List[Dict[str, Any]],
                          algorithms_to_compare: List[str] = None) -> Dict[str, Any]:
        """
        Exécute plusieurs algorithmes en parallèle pour comparaison V2.1
        """
        if algorithms_to_compare is None:
            # Par défaut, compare les algorithmes principaux
            algorithms_to_compare = ['enhanced-v2', 'semantic', 'hybrid']
        
        results = {}
        
        for algo_name in algorithms_to_compare:
            if algo_name in self.algorithms:
                start_time = time.time()
                try:
                    result = self.match(
                        candidate_data, jobs_data, 
                        algorithm=algo_name,
                        options={'limit': 5, 'include_details': True}
                    )
                    results[algo_name] = {
                        'matches': result.get('matches', []),
                        'execution_time_ms': result.get('execution_time_ms', 0),
                        'top_score': result.get('matches', [{}])[0].get('matching_score', 0) if result.get('matches') else 0,
                        'algorithm_info': self.algorithms[algo_name].get_algorithm_info()
                    }
                except Exception as e:
                    results[algo_name] = {
                        'error': str(e),
                        'execution_time_ms': (time.time() - start_time) * 1000
                    }
        
        return {
            'comparison_results': results,
            'recommendation': self._analyze_comparison_results_v2(results),
            'version': '2.1.0'
        }
    
    def _generate_cache_key(self, candidate_data: Dict[str, Any], 
                           jobs_data: List[Dict[str, Any]], 
                           algorithm: str, options: Dict[str, Any]) -> str:
        """
        Génère une clé de cache unique pour la requête V2.1
        """
        import hashlib
        import json
        
        # Simplification des données pour le cache V2.1
        cache_data = {
            'candidate_skills': candidate_data.get('competences', []),
            'candidate_location': candidate_data.get('adresse', ''),
            'candidate_experience': candidate_data.get('annees_experience', 0),
            'candidate_text_hash': hashlib.md5(
                str(candidate_data.get('missions', [])).encode()
            ).hexdigest()[:8],  # 🆕 V2.1 - Hash des missions pour secteur
            'job_count': len(jobs_data),
            'job_skills_hash': hashlib.md5(
                str([job.get('competences', []) for job in jobs_data]).encode()
            ).hexdigest()[:8],
            'algorithm': algorithm,
            'limit': options.get('limit', 10),
            'version': '2.1.0'  # 🆕 V2.1
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _prepare_data_for_algorithm(self, candidate_data: Dict[str, Any], 
                                   jobs_data: List[Dict[str, Any]], 
                                   algorithm: str) -> Dict[str, Any]:
        """
        Prépare les données dans le format attendu par chaque algorithme V2.1
        """
        # Format générique pour tous les algorithmes V2.1
        return {
            'candidate': candidate_data,
            'jobs': jobs_data
        }
    
    def _enrich_matches_v2(self, matches: List[Dict[str, Any]], 
                          algorithm: str, include_details: bool) -> List[Dict[str, Any]]:
        """
        🆕 V2.1 - Enrichit les résultats avec les nouvelles métadonnées sectorielles
        """
        enriched = []
        
        for match in matches:
            enriched_match = match.copy()
            
            # Version de l'algorithme
            enriched_match['algorithm_version'] = f"{algorithm}_v2.1"
            
            # Recommandations basiques si pas déjà présentes (pour algorithmes non-V2.1)
            if 'recommendations' not in enriched_match:
                enriched_match['recommendations'] = self._generate_recommendations_v2(
                    enriched_match
                )
            
            # Assurer la présence de matching_details
            if include_details and 'matching_details' not in enriched_match:
                enriched_match['matching_details'] = {
                    'skills': enriched_match.get('matching_score', 0),
                    'location': enriched_match.get('matching_score', 0),
                    'salary': enriched_match.get('matching_score', 0),
                    'contract': enriched_match.get('matching_score', 0)
                }
            
            enriched.append(enriched_match)
        
        return enriched
    
    def _generate_recommendations_v2(self, match: Dict[str, Any]) -> List[str]:
        """
        🆕 V2.1 - Génère des recommandations avec conscience sectorielle
        """
        score = match.get('matching_score', 0)
        recommendations = []
        
        # Recommandations selon le score global
        if score >= 90:
            recommendations.append("🎯 Excellent match - Candidature fortement recommandée")
        elif score >= 80:
            recommendations.append("✅ Très bon match - Candidature recommandée")
        elif score >= 70:
            recommendations.append("👍 Bon match - Candidature à considérer")
        elif score >= 60:
            recommendations.append("⚠️ Match modéré - Évaluer les critères importants")
        else:
            recommendations.append("❌ Match faible - Revoir les critères")
        
        # Recommandations sectorielles si disponibles
        sector_analysis = match.get('sector_analysis', {})
        if sector_analysis:
            compatibility = sector_analysis.get('compatibility_score', 0)
            if compatibility < 30:
                recommendations.append("🔄 Transition sectorielle majeure requise")
            elif compatibility < 60:
                recommendations.append("📚 Adaptation sectorielle nécessaire")
        
        # Facteurs bloquants si présents
        blocking_factors = match.get('blocking_factors', [])
        if blocking_factors:
            high_severity = [bf for bf in blocking_factors if bf.get('severity') == 'high']
            if high_severity:
                recommendations.append("🚨 Facteurs bloquants détectés - Voir détails")
        
        return recommendations
    
    def _analyze_comparison_results_v2(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        🆕 V2.1 - Analyse les résultats de comparaison avec focus sur la précision sectorielle
        """
        best_algorithm = None
        best_score = 0
        fastest_algorithm = None
        fastest_time = float('inf')
        most_detailed = None
        
        for algo_name, result in results.items():
            if 'error' not in result:
                score = result.get('top_score', 0)
                time_ms = result.get('execution_time_ms', 0)
                
                if score > best_score:
                    best_score = score
                    best_algorithm = algo_name
                
                if time_ms < fastest_time:
                    fastest_time = time_ms
                    fastest_algorithm = algo_name
                
                # Privilégier Enhanced V2.1 pour le détail
                if algo_name == 'enhanced-v2':
                    most_detailed = algo_name
        
        recommendation = f"Précision: '{best_algorithm}' | Performance: '{fastest_algorithm}'"
        if most_detailed:
            recommendation += f" | Analyse détaillée: '{most_detailed}'"
        
        return {
            'best_accuracy': best_algorithm,
            'best_performance': fastest_algorithm,
            'most_detailed': most_detailed,
            'recommendation': recommendation,
            'v2_1_note': 'Enhanced V2.1 recommandé pour analyse sectorielle'
        }

# Instance du service principal V2.1
supersmartmatch = SuperSmartMatchServiceV2()

# Routes de l'API V2.1
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé du service V2.1
    """
    return jsonify({
        'status': 'healthy',
        'service': 'SuperSmartMatch',
        'version': '2.1.0',  # 🆕
        'algorithms_available': list(algorithms.keys()),
        'new_features': [  # 🆕
            'Enhanced Matching V2.1 avec intelligence sectorielle',
            'SectorAnalyzer avec matrice française',
            'Facteurs bloquants et recommandations',
            'Analyse de transition sectorielle'
        ],
        'uptime_seconds': time.time() - app.start_time if hasattr(app, 'start_time') else 0
    })

@app.route('/api/v1/match', methods=['POST'])
def match_endpoint():
    """
    Endpoint principal de matching unifié V2.1
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        candidate_data = data.get('candidate')
        jobs_data = data.get('jobs', [])
        algorithm = data.get('algorithm', 'auto')
        options = data.get('options', {})
        
        if not candidate_data:
            return jsonify({'error': 'Données candidat requises'}), 400
        
        if not jobs_data:
            return jsonify({'error': 'Données offres d\'emploi requises'}), 400
        
        # Exécution du matching V2.1
        result = supersmartmatch.match(
            candidate_data=candidate_data,
            jobs_data=jobs_data,
            algorithm=algorithm,
            options=options
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint match V2.1: {str(e)}")
        return jsonify({
            'error': 'Erreur interne du serveur',
            'details': str(e) if app.debug else 'Contactez l\'administrateur',
            'version': '2.1.0'
        }), 500

@app.route('/api/v2.1/sector-analysis', methods=['POST'])
def sector_analysis_endpoint():
    """
    🆕 V2.1 - Endpoint d'analyse sectorielle
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        text = data.get('text', '')
        context = data.get('context', 'general')
        
        if not text.strip():
            return jsonify({'error': 'Texte à analyser requis'}), 400
        
        # Analyse sectorielle
        result = supersmartmatch.analyze_sector(text, context)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur analyse sectorielle: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'details': str(e) if app.debug else 'Contactez l\'administrateur'
        }), 500

@app.route('/api/v1/compare', methods=['POST'])
def compare_algorithms_endpoint():
    """
    Endpoint de comparaison d'algorithmes V2.1
    """
    try:
        data = request.get_json()
        
        candidate_data = data.get('candidate')
        jobs_data = data.get('jobs', [])
        algorithms_to_compare = data.get('algorithms', None)
        
        if not candidate_data or not jobs_data:
            return jsonify({'error': 'Données candidat et jobs requises'}), 400
        
        result = supersmartmatch.compare_algorithms(
            candidate_data=candidate_data,
            jobs_data=jobs_data,
            algorithms_to_compare=algorithms_to_compare
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint compare V2.1: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.route('/api/v1/algorithms', methods=['GET'])
def get_available_algorithms():
    """
    Liste des algorithmes disponibles V2.1
    """
    algorithm_info = {
        'smart-match': {
            'name': 'Smart Match',
            'description': 'Algorithme bidirectionnel avec géolocalisation Google Maps',
            'best_for': 'Matching géographique précis',
            'performance': 'Moyen',
            'accuracy': 'Élevée',
            'version': '1.0'
        },
        'enhanced-v2': {  # 🆕
            'name': 'Enhanced Matching V2.1',
            'description': 'Intelligence sectorielle avec matrice de compatibilité française',
            'best_for': 'Matching avec différences sectorielles - RÉSOUT LE PROBLÈME 79%',
            'performance': 'Élevé',
            'accuracy': 'Très élevée',
            'version': '2.1.0',
            'key_features': [
                'Analyse sectorielle automatique',
                'Pondération adaptative par secteur (40%)',
                'Détection de facteurs bloquants',
                'Recommandations intelligentes'
            ]
        },
        'enhanced': {  # Alias pour compatibilité
            'name': 'Enhanced Matching (Alias V2.1)',
            'description': 'Pointe vers Enhanced V2.1 pour compatibilité',
            'best_for': 'Utiliser enhanced-v2 de préférence',
            'performance': 'Élevé',
            'accuracy': 'Très élevée',
            'version': '2.1.0'
        },
        'semantic': {
            'name': 'Semantic Analyzer',
            'description': 'Matching sémantique des compétences techniques',
            'best_for': 'Analyse fine des compétences',
            'performance': 'Moyen',
            'accuracy': 'Très élevée',
            'version': '1.0'
        },
        'hybrid': {
            'name': 'Hybrid Matching',
            'description': 'Combinaison intelligente de plusieurs algorithmes',
            'best_for': 'Précision maximale',
            'performance': 'Faible',
            'accuracy': 'Maximale',
            'version': '1.0'
        },
        'auto': {
            'name': 'Auto Selection V2.1',
            'description': 'Sélection automatique - Privilégie Enhanced V2.1',
            'best_for': 'Utilisation générale recommandée avec intelligence sectorielle',
            'performance': 'Variable',
            'accuracy': 'Optimale',
            'version': '2.1.0'
        }
    }
    
    return jsonify({
        'algorithms': algorithm_info,
        'recommendation': 'Utilisez "enhanced-v2" pour la précision sectorielle ou "auto" pour sélection intelligente',
        'v2_1_highlights': [
            'Enhanced V2.1 résout le problème Commercial vs Juridique (79% -> 25%)',
            'Analyse sectorielle automatique avec 9 secteurs français',
            'Matrice de compatibilité 81 combinaisons',
            'Nouveau endpoint /api/v2.1/sector-analysis'
        ]
    })

@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """
    Métriques de performance du service V2.1
    """
    return jsonify({
        'performance_metrics': performance_monitor.get_metrics(),
        'cache_metrics': cache_manager.get_metrics(),
        'algorithms_usage': performance_monitor.get_algorithm_usage(),
        'sector_analyzer_info': sector_analyzer.get_sector_info(),  # 🆕
        'version': '2.1.0'
    })

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Dashboard de monitoring V2.1
    """
    return render_template('dashboard.html')

@app.route('/', methods=['GET'])
def index():
    """
    Page d'accueil avec documentation API V2.1
    """
    return jsonify({
        'service': 'SuperSmartMatch API v2.1.0',  # 🆕
        'description': 'Service unifié de matching avec intelligence sectorielle',
        'problem_solved': 'CV Commercial vs Poste Juridique: 79% -> 25%',  # 🆕
        'endpoints': {
            'POST /api/v1/match': 'Matching principal unifié V2.1',
            'POST /api/v2.1/sector-analysis': '🆕 Analyse sectorielle standalone',  # 🆕
            'POST /api/v1/compare': 'Comparaison d\'algorithmes',
            'GET /api/v1/algorithms': 'Liste des algorithmes disponibles',
            'GET /api/v1/metrics': 'Métriques de performance',
            'GET /api/v1/health': 'État de santé du service',
            'GET /dashboard': 'Dashboard de monitoring'
        },
        'new_features_v2_1': [  # 🆕
            'Enhanced Matching V2.1 avec intelligence sectorielle',
            'SectorAnalyzer avec matrice de compatibilité française',
            'Détection automatique de 9 secteurs d\'activité',
            'Facteurs bloquants et recommandations intelligentes',
            'Analyse de transition sectorielle',
            'Pondération adaptative selon compatibilité (40% poids sectoriel)'
        ],
        'documentation': 'https://github.com/Bapt252/SuperSmartMatch-Service'
    })

if __name__ == '__main__':
    # Enregistrement du temps de démarrage
    app.start_time = time.time()
    
    # Configuration pour le développement
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5060))
    
    logger.info(f"🚀 Démarrage de SuperSmartMatch V2.1 sur le port {port}")
    logger.info(f"📊 Algorithmes disponibles: {list(algorithms.keys())}")
    logger.info(f"🎯 NOUVEAU: Enhanced V2.1 avec intelligence sectorielle")
    logger.info(f"✅ PROBLÈME RÉSOLU: Commercial vs Juridique 79% -> 25%")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
