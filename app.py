#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperSmartMatch Service - API unifiée de matching pour Nexten

Ce service regroupe tous vos algorithmes de matching existants
sous une seule API puissante et simple d'utilisation.

Auteur: Service unifié pour Nexten
Version: 1.0.0
"""

import os
import time
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from typing import Dict, List, Any, Optional

# Imports des algorithmes existants
from algorithms.smart_match import SmartMatchAlgorithm
from algorithms.enhanced_matching import EnhancedMatchingAlgorithm
from algorithms.semantic_analyzer import SemanticAnalyzerAlgorithm
from algorithms.hybrid_matching import HybridMatchingAlgorithm
from algorithms.auto_selector import AutoSelectorEngine
from utils.performance_monitor import PerformanceMonitor
from utils.cache_manager import CacheManager
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

# Initialisation des algorithmes
algorithms = {
    'smart-match': SmartMatchAlgorithm(),
    'enhanced': EnhancedMatchingAlgorithm(),
    'semantic': SemanticAnalyzerAlgorithm(),
    'hybrid': HybridMatchingAlgorithm()
}

class SuperSmartMatchService:
    """
    Service principal qui orchestre tous les algorithmes de matching
    """
    
    def __init__(self):
        self.algorithms = algorithms
        self.auto_selector = auto_selector
        self.performance_monitor = performance_monitor
        self.cache = cache_manager
        
    def match(self, candidate_data: Dict[str, Any], 
              jobs_data: List[Dict[str, Any]], 
              algorithm: str = 'auto',
              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Point d'entrée principal pour le matching unifié
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            algorithm: Algorithme à utiliser ('auto', 'smart-match', etc.)
            options: Options supplémentaires
            
        Returns:
            Résultats de matching avec métadonnées
        """
        start_time = time.time()
        
        # Options par défaut
        if options is None:
            options = {}
        
        limit = options.get('limit', 10)
        include_details = options.get('include_details', True)
        performance_mode = options.get('performance_mode', 'balanced')
        
        # Génération de la clé de cache
        cache_key = self._generate_cache_key(candidate_data, jobs_data, algorithm, options)
        
        # Vérification du cache
        if performance_mode in ['fast', 'balanced']:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit pour la requête {cache_key[:8]}...")
                cached_result['cache_hit'] = True
                return cached_result
        
        # Sélection de l'algorithme
        if algorithm == 'auto':
            selected_algorithm = self.auto_selector.select_optimal_algorithm(
                candidate_data, jobs_data
            )
            logger.info(f"Auto-sélection: {selected_algorithm}")
        else:
            selected_algorithm = algorithm
        
        # Validation de l'algorithme
        if selected_algorithm not in self.algorithms:
            return {
                'error': f"Algorithme '{selected_algorithm}' non disponible",
                'available_algorithms': list(self.algorithms.keys())
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
            
            # Enrichissement des résultats
            enriched_matches = self._enrich_matches(
                matches, selected_algorithm, include_details
            )
            
            # Calcul des métriques de performance
            execution_time = (time.time() - start_time) * 1000  # en ms
            
            # Construction de la réponse
            result = {
                'algorithm_used': selected_algorithm,
                'execution_time_ms': round(execution_time, 2),
                'total_jobs_analyzed': len(jobs_data),
                'matches': enriched_matches,
                'performance_metrics': {
                    'cache_hit_rate': self.cache.get_hit_rate(),
                    'optimization_applied': performance_mode,
                    'total_algorithms_available': len(self.algorithms)
                },
                'cache_hit': False
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
            logger.error(f"Erreur lors du matching: {str(e)}")
            return {
                'error': f"Erreur lors du matching: {str(e)}",
                'algorithm_attempted': selected_algorithm,
                'execution_time_ms': round((time.time() - start_time) * 1000, 2)
            }
    
    def compare_algorithms(self, candidate_data: Dict[str, Any], 
                          jobs_data: List[Dict[str, Any]],
                          algorithms_to_compare: List[str] = None) -> Dict[str, Any]:
        """
        Exécute plusieurs algorithmes en parallèle pour comparaison
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            algorithms_to_compare: Liste des algorithmes à comparer
            
        Returns:
            Résultats comparatifs de tous les algorithmes
        """
        if algorithms_to_compare is None:
            algorithms_to_compare = list(self.algorithms.keys())
        
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
                        'top_score': result.get('matches', [{}])[0].get('matching_score', 0) if result.get('matches') else 0
                    }
                except Exception as e:
                    results[algo_name] = {
                        'error': str(e),
                        'execution_time_ms': (time.time() - start_time) * 1000
                    }
        
        return {
            'comparison_results': results,
            'recommendation': self._analyze_comparison_results(results)
        }
    
    def _generate_cache_key(self, candidate_data: Dict[str, Any], 
                           jobs_data: List[Dict[str, Any]], 
                           algorithm: str, options: Dict[str, Any]) -> str:
        """
        Génère une clé de cache unique pour la requête
        """
        import hashlib
        import json
        
        # Simplification des données pour le cache
        cache_data = {
            'candidate_skills': candidate_data.get('competences', []),
            'candidate_location': candidate_data.get('adresse', ''),
            'candidate_experience': candidate_data.get('annees_experience', 0),
            'job_count': len(jobs_data),
            'job_skills_hash': hashlib.md5(
                str([job.get('competences', []) for job in jobs_data]).encode()
            ).hexdigest()[:8],
            'algorithm': algorithm,
            'limit': options.get('limit', 10)
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _prepare_data_for_algorithm(self, candidate_data: Dict[str, Any], 
                                   jobs_data: List[Dict[str, Any]], 
                                   algorithm: str) -> Dict[str, Any]:
        """
        Prépare les données dans le format attendu par chaque algorithme
        """
        # Normalisation des données selon l'algorithme
        if algorithm == 'smart-match':
            # Format SmartMatch
            return {
                'candidate': candidate_data,
                'jobs': jobs_data
            }
        elif algorithm == 'enhanced':
            # Format Enhanced
            return {
                'candidate': candidate_data,
                'jobs': jobs_data
            }
        else:
            # Format générique
            return {
                'candidate': candidate_data,
                'jobs': jobs_data
            }
    
    def _enrich_matches(self, matches: List[Dict[str, Any]], 
                       algorithm: str, include_details: bool) -> List[Dict[str, Any]]:
        """
        Enrichit les résultats de matching avec des métadonnées
        """
        enriched = []
        
        for match in matches:
            enriched_match = match.copy()
            enriched_match['algorithm_version'] = f"{algorithm}_v1.0"
            
            if include_details and 'matching_details' not in enriched_match:
                enriched_match['matching_details'] = {
                    'skills': enriched_match.get('matching_score', 0),
                    'location': enriched_match.get('matching_score', 0),
                    'salary': enriched_match.get('matching_score', 0),
                    'contract': enriched_match.get('matching_score', 0)
                }
            
            # Ajout de recommandations
            enriched_match['recommendations'] = self._generate_recommendations(
                enriched_match
            )
            
            enriched.append(enriched_match)
        
        return enriched
    
    def _generate_recommendations(self, match: Dict[str, Any]) -> List[str]:
        """
        Génère des recommandations basées sur le score de matching
        """
        score = match.get('matching_score', 0)
        recommendations = []
        
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
        
        # Recommandations spécifiques selon les détails
        details = match.get('matching_details', {})
        if details.get('skills', 0) >= 90:
            recommendations.append("🧠 Excellente correspondance des compétences")
        if details.get('location', 0) >= 90:
            recommendations.append("📍 Localisation parfaite")
        if details.get('salary', 0) >= 90:
            recommendations.append("💰 Attentes salariales alignées")
        
        return recommendations
    
    def _analyze_comparison_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les résultats de comparaison pour donner une recommandation
        """
        # Trouve le meilleur algorithme basé sur le score et le temps
        best_algorithm = None
        best_score = 0
        fastest_algorithm = None
        fastest_time = float('inf')
        
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
        
        return {
            'best_accuracy': best_algorithm,
            'best_performance': fastest_algorithm,
            'recommendation': f"Utilisez '{best_algorithm}' pour la précision ou '{fastest_algorithm}' pour la performance"
        }

# Instance du service principal
supersmartmatch = SuperSmartMatchService()

# Routes de l'API
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé du service
    """
    return jsonify({
        'status': 'healthy',
        'service': 'SuperSmartMatch',
        'version': '1.0.0',
        'algorithms_available': list(algorithms.keys()),
        'uptime_seconds': time.time() - app.start_time if hasattr(app, 'start_time') else 0
    })

@app.route('/api/v1/match', methods=['POST'])
def match_endpoint():
    """
    Endpoint principal de matching unifié
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
        
        # Exécution du matching
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
        logger.error(f"Erreur dans l'endpoint match: {str(e)}")
        return jsonify({
            'error': 'Erreur interne du serveur',
            'details': str(e) if app.debug else 'Contactez l\'administrateur'
        }), 500

@app.route('/api/v1/compare', methods=['POST'])
def compare_algorithms_endpoint():
    """
    Endpoint de comparaison d'algorithmes
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
        logger.error(f"Erreur dans l'endpoint compare: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.route('/api/v1/algorithms', methods=['GET'])
def get_available_algorithms():
    """
    Liste des algorithmes disponibles avec leurs descriptions
    """
    algorithm_info = {
        'smart-match': {
            'name': 'Smart Match',
            'description': 'Algorithme bidirectionnel avec géolocalisation Google Maps',
            'best_for': 'Matching géographique précis',
            'performance': 'Moyen',
            'accuracy': 'Élevée'
        },
        'enhanced': {
            'name': 'Enhanced Matching',
            'description': 'Pondération adaptative selon l\'expérience candidat',
            'best_for': 'Matching équilibré et intelligent',
            'performance': 'Élevé',
            'accuracy': 'Très élevée'
        },
        'semantic': {
            'name': 'Semantic Analyzer',
            'description': 'Matching sémantique des compétences techniques',
            'best_for': 'Analyse fine des compétences',
            'performance': 'Moyen',
            'accuracy': 'Très élevée'
        },
        'hybrid': {
            'name': 'Hybrid Matching',
            'description': 'Combinaison intelligente de plusieurs algorithmes',
            'best_for': 'Précision maximale',
            'performance': 'Faible',
            'accuracy': 'Maximale'
        },
        'auto': {
            'name': 'Auto Selection',
            'description': 'Sélection automatique de l\'algorithme optimal',
            'best_for': 'Utilisation générale recommandée',
            'performance': 'Variable',
            'accuracy': 'Optimale'
        }
    }
    
    return jsonify({
        'algorithms': algorithm_info,
        'recommendation': 'Utilisez "auto" pour une sélection optimale automatique'
    })

@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """
    Métriques de performance du service
    """
    return jsonify({
        'performance_metrics': performance_monitor.get_metrics(),
        'cache_metrics': cache_manager.get_metrics(),
        'algorithms_usage': performance_monitor.get_algorithm_usage()
    })

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Dashboard de monitoring (interface web simple)
    """
    return render_template('dashboard.html')

@app.route('/', methods=['GET'])
def index():
    """
    Page d'accueil avec documentation API
    """
    return jsonify({
        'service': 'SuperSmartMatch API v1.0',
        'description': 'Service unifié de matching pour Nexten',
        'endpoints': {
            'POST /api/v1/match': 'Matching principal unifié',
            'POST /api/v1/compare': 'Comparaison d\'algorithmes',
            'GET /api/v1/algorithms': 'Liste des algorithmes disponibles',
            'GET /api/v1/metrics': 'Métriques de performance',
            'GET /api/v1/health': 'État de santé du service',
            'GET /dashboard': 'Dashboard de monitoring'
        },
        'documentation': 'https://github.com/Bapt252/SuperSmartMatch-Service'
    })

if __name__ == '__main__':
    # Enregistrement du temps de démarrage
    app.start_time = time.time()
    
    # Configuration pour le développement
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5060))
    
    logger.info(f"🚀 Démarrage de SuperSmartMatch sur le port {port}")
    logger.info(f"📊 Algorithmes disponibles: {list(algorithms.keys())}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
