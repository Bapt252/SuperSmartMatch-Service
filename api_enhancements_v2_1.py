#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced API Endpoints for SuperSmartMatch V2.1 
Ajoute les questionnaires adaptatifs et les fonctionnalités de debug

À intégrer dans app.py
"""

# NOUVEAUX IMPORTS À AJOUTER DANS APP.PY
from questionnaires.adaptive_questionnaire import AdaptiveQuestionnaireEngine, QuestionnaireResponse
from utils.scoring_debugger import ScoringDebugger
import time

# NOUVELLES INSTANCES À INITIALISER
questionnaire_engine = AdaptiveQuestionnaireEngine()
scoring_debugger = ScoringDebugger()

# NOUVEAUX ENDPOINTS À AJOUTER DANS APP.PY

@app.route('/api/v2.1/generate-questionnaire', methods=['POST'])
def generate_questionnaire_endpoint():
    """
    🆕 V2.1 Enhanced - Génère un questionnaire adaptatif
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        candidate_data = data.get('candidate_data')
        target_sector = data.get('target_sector')
        
        if not candidate_data:
            return jsonify({'error': 'Données candidat requises'}), 400
        
        # Génération du questionnaire
        questionnaire = questionnaire_engine.generate_candidate_questionnaire(
            candidate_data, target_sector
        )
        
        return jsonify({
            'success': True,
            'questionnaire': questionnaire,
            'version': '2.1.0'
        })
        
    except Exception as e:
        logger.error(f"Erreur génération questionnaire: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'details': str(e) if app.debug else 'Contactez l\'administrateur'
        }), 500

@app.route('/api/v2.1/enhanced-match', methods=['POST'])
def enhanced_match_endpoint():
    """
    🆕 V2.1 Enhanced - Matching avec questionnaire intégré
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        candidate_data = data.get('candidate')
        jobs_data = data.get('jobs', [])
        algorithm = data.get('algorithm', 'enhanced-v2')
        
        if not candidate_data or not jobs_data:
            return jsonify({'error': 'Données candidat et jobs requises'}), 400
        
        # Intégration des réponses de questionnaire si présentes
        enhanced_candidate = candidate_data.copy()
        
        if 'questionnaire_responses' in candidate_data:
            questionnaire_response = QuestionnaireResponse(
                questionnaire_id=candidate_data.get('questionnaire_id', 'manual'),
                candidate_id=candidate_data.get('candidate_id'),
                responses=candidate_data['questionnaire_responses'],
                completion_time_seconds=candidate_data.get('completion_time', 0),
                completion_rate=1.0,  # Assume complete
                sector_confidence_boost=0.2,
                timestamp=time.time()
            )
            
            enhanced_candidate = questionnaire_engine.integrate_questionnaire_responses(
                candidate_data, questionnaire_response
            )
        
        # Matching enhanced
        result = supersmartmatch.match(
            candidate_data=enhanced_candidate,
            jobs_data=jobs_data,
            algorithm=algorithm,
            options=data.get('options', {})
        )
        
        # Enrichissement avec données questionnaire
        if 'questionnaire_responses' in candidate_data:
            result['questionnaire_integrated'] = True
            result['enhanced_features'] = [
                'Questionnaire adaptatif intégré',
                'Profil candidat enrichi',
                'Scoring avec données qualitatives'
            ]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur enhanced match: {str(e)}")
        return jsonify({
            'error': 'Erreur interne du serveur',
            'details': str(e) if app.debug else 'Contactez l\'administrateur',
            'version': '2.1.0'
        }), 500

@app.route('/api/v2.1/debug-scoring', methods=['POST'])
def debug_scoring_endpoint():
    """
    🆕 V2.1 Enhanced - Debug du scoring en temps réel
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        candidate_data = data.get('candidate')
        job_data = data.get('job')
        
        if not candidate_data or not job_data:
            return jsonify({'error': 'Données candidat et job requises'}), 400
        
        # Debug du scoring
        debug_report = scoring_debugger.debug_zachary_case(candidate_data, job_data)
        
        return jsonify({
            'success': True,
            'debug_report': debug_report,
            'version': '2.1.0',
            'debug_timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Erreur debug scoring: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors du debug',
            'details': str(e) if app.debug else 'Contactez l\'administrateur'
        }), 500

@app.route('/api/v2.1/questionnaire-response', methods=['POST'])
def questionnaire_response_endpoint():
    """
    🆕 V2.1 Enhanced - Soumission de réponse questionnaire
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        questionnaire_id = data.get('questionnaire_id')
        responses = data.get('responses', {})
        candidate_id = data.get('candidate_id')
        completion_time = data.get('completion_time_seconds', 0)
        
        if not questionnaire_id or not responses:
            return jsonify({'error': 'ID questionnaire et réponses requis'}), 400
        
        # Création de l'objet réponse
        questionnaire_response = QuestionnaireResponse(
            questionnaire_id=questionnaire_id,
            candidate_id=candidate_id,
            responses=responses,
            completion_time_seconds=completion_time,
            completion_rate=len(responses) / data.get('total_questions', len(responses)),
            sector_confidence_boost=0.2,
            timestamp=time.time()
        )
        
        # Calcul du score d'adaptation
        adaptation_score = questionnaire_engine._calculate_adaptation_score(questionnaire_response)
        transition_readiness = questionnaire_engine._calculate_transition_readiness(questionnaire_response)
        
        return jsonify({
            'success': True,
            'questionnaire_response_id': questionnaire_response.questionnaire_id,
            'analysis': {
                'completion_rate': questionnaire_response.completion_rate,
                'adaptation_score': adaptation_score,
                'transition_readiness': transition_readiness,
                'sector_confidence_boost': questionnaire_response.sector_confidence_boost
            },
            'recommendations': [
                f"Taux de completion: {questionnaire_response.completion_rate*100:.1f}%",
                f"Score d'adaptation: {adaptation_score:.2f}/1.0",
                f"Préparation transition: {transition_readiness:.2f}/1.0"
            ],
            'version': '2.1.0'
        })
        
    except Exception as e:
        logger.error(f"Erreur soumission questionnaire: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la soumission',
            'details': str(e) if app.debug else 'Contactez l\'administrateur'
        }), 500

@app.route('/api/v2.1/validate-zachary', methods=['GET'])
def validate_zachary_endpoint():
    """
    🆕 V2.1 Enhanced - Validation rapide du cas Zachary
    """
    try:
        # Données Zachary standardisées
        zachary_cv = {
            "competences": ["Prospection commerciale", "Relation client", "CRM"],
            "missions": ["Développement du portefeuille client"],
            "titre_poste": "Assistant commercial", 
            "annees_experience": 1
        }
        
        juridique_job = {
            "titre": "Assistant juridique",
            "competences": ["Droit", "Rédaction juridique", "Contrats"],
            "missions": ["Rédaction d'actes juridiques", "Veille réglementaire"]
        }
        
        # Test Enhanced V2.1
        results = supersmartmatch.match(
            candidate_data=zachary_cv,
            jobs_data=[juridique_job],
            algorithm='enhanced-v2'
        )
        
        score = results['matches'][0]['matching_score'] if results['matches'] else 100
        target_achieved = score <= 25
        
        # Debug rapide si nécessaire
        debug_summary = None
        if score > 25:
            debug_report = scoring_debugger.debug_zachary_case(zachary_cv, juridique_job)
            debug_summary = {
                'issues_count': len(debug_report['issues_found']),
                'recommendations_count': len(debug_report['recommendations']),
                'main_issue': debug_report['issues_found'][0]['type'] if debug_report['issues_found'] else None
            }
        
        return jsonify({
            'case': 'Zachary (Commercial) vs Assistant Juridique',
            'current_score': score,
            'target_score': 25,
            'target_achieved': target_achieved,
            'algorithm_used': 'enhanced-v2',
            'status': 'PASSED' if target_achieved else 'FAILED',
            'debug_summary': debug_summary,
            'version': '2.1.0',
            'test_timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Erreur validation Zachary: {str(e)}")
        return jsonify({
            'case': 'Zachary validation',
            'status': 'ERROR',
            'error': str(e),
            'version': '2.1.0'
        }), 500

# MISE À JOUR DE L'ENDPOINT D'INFORMATIONS
@app.route('/api/v2.1/info', methods=['GET'])
def enhanced_info_endpoint():
    """
    🆕 V2.1 Enhanced - Informations complètes sur les nouvelles fonctionnalités
    """
    return jsonify({
        'service': 'SuperSmartMatch API v2.1.0 Enhanced',
        'description': 'Service de matching avec questionnaires adaptatifs et debug avancé',
        'problem_solved': 'CV Commercial vs Poste Juridique: 79% → ≤25%',
        'new_endpoints': {
            'POST /api/v2.1/generate-questionnaire': 'Génère un questionnaire adaptatif',
            'POST /api/v2.1/enhanced-match': 'Matching avec questionnaire intégré',
            'POST /api/v2.1/debug-scoring': 'Debug du scoring en temps réel',
            'POST /api/v2.1/questionnaire-response': 'Soumission réponse questionnaire',
            'GET /api/v2.1/validate-zachary': 'Validation rapide du cas Zachary'
        },
        'existing_endpoints': {
            'POST /api/v1/match': 'Matching principal (compatible V2.1)',
            'POST /api/v2.1/sector-analysis': 'Analyse sectorielle',
            'GET /api/v1/algorithms': 'Liste des algorithmes',
            'GET /api/v1/health': 'État de santé'
        },
        'enhanced_features': [
            '📋 Questionnaires adaptatifs sectoriels',
            '🔍 Debug scoring en temps réel', 
            '🎯 Résolution problème Zachary (79% → 25%)',
            '🧠 Intelligence sectorielle renforcée',
            '📊 Recommandations intelligentes',
            '⚡ Pondération adaptative'
        ],
        'compatibility': 'Backward compatible avec V2.0',
        'documentation': 'Voir Guide d\'Utilisation V2.1 Enhanced'
    })

# INSTRUCTIONS D'INTÉGRATION DANS APP.PY
"""
Pour intégrer ces nouveaux endpoints dans app.py:

1. Ajouter les imports en haut du fichier:
   from questionnaires.adaptive_questionnaire import AdaptiveQuestionnaireEngine, QuestionnaireResponse
   from utils.scoring_debugger import ScoringDebugger

2. Initialiser les instances après les autres services:
   questionnaire_engine = AdaptiveQuestionnaireEngine()
   scoring_debugger = ScoringDebugger()

3. Copier tous les @app.route ci-dessus avant le if __name__ == '__main__':

4. Mettre à jour l'endpoint racine pour inclure les nouveaux endpoints

5. Tester avec:
   python app.py
   curl http://localhost:5060/api/v2.1/info
"""
