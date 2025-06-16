#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptive Questionnaire Engine - Questionnaires intelligents pour SuperSmartMatch V2.1

Ce module génère des questionnaires adaptatifs selon le secteur détecté
pour compenser les limites du parsing automatique des CV/offres.

Fonctionnalités:
- Questionnaires sectoriels personnalisés
- Compensation des données manquantes
- Questions adaptatives selon le niveau d'expérience
- Intégration avec le moteur de matching

Auteur: SuperSmartMatch V2.1 Enhanced
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from utils.sector_analyzer import SectorAnalyzer

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Types de questions disponibles"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    SCALE = "scale"
    MULTISELECT = "multiselect"
    SELECT = "select"
    BOOLEAN = "boolean"
    RANGE = "range"

@dataclass
class Question:
    """Structure d'une question"""
    id: str
    type: QuestionType
    question: str
    required: bool = True
    sector_weight: float = 1.0
    experience_dependent: bool = False
    options: List[str] = None
    min_value: int = None
    max_value: int = None
    unit: str = None
    placeholder: str = None
    help_text: str = None

@dataclass
class QuestionnaireResponse:
    """Réponse à un questionnaire"""
    questionnaire_id: str
    candidate_id: Optional[str]
    responses: Dict[str, Any]
    completion_time_seconds: int
    completion_rate: float
    sector_confidence_boost: float
    timestamp: float

class AdaptiveQuestionnaireEngine:
    """
    Moteur de questionnaires adaptatifs pour SuperSmartMatch V2.1
    """
    
    def __init__(self):
        self.sector_analyzer = SectorAnalyzer()
        self.question_bank = self._initialize_question_bank()
        
    def _initialize_question_bank(self) -> Dict[str, List[Question]]:
        """Initialise la banque de questions par secteur"""
        
        return {
            # Questions communes à tous les secteurs
            'common': [
                Question(
                    id='motivation_principale',
                    type=QuestionType.TEXTAREA,
                    question='Quelle est votre principale motivation pour ce changement de poste ?',
                    sector_weight=0.8,
                    placeholder='Ex: Évolution de carrière, nouveau défi, meilleur équilibre...',
                    help_text='Cette information aide à mieux comprendre votre profil'
                ),
                Question(
                    id='competences_transferables',
                    type=QuestionType.TEXTAREA,
                    question='Quelles compétences de votre expérience actuelle pensez-vous pouvoir transférer ?',
                    sector_weight=0.9,
                    placeholder='Ex: Management, organisation, communication...'
                ),
                Question(
                    id='formation_complementaire',
                    type=QuestionType.BOOLEAN,
                    question='Seriez-vous prêt(e) à suivre une formation complémentaire si nécessaire ?',
                    sector_weight=0.7
                ),
                Question(
                    id='adaptabilite_score',
                    type=QuestionType.SCALE,
                    question='Comment évaluez-vous votre capacité d\\'adaptation à un nouveau secteur ?',
                    min_value=1,
                    max_value=10,
                    sector_weight=0.6,
                    help_text='1 = Très difficile, 10 = Très facile'
                )
            ],
            
            # Questions spécifiques au secteur commercial
            'commercial': [
                Question(
                    id='ca_realise',
                    type=QuestionType.NUMBER,
                    question='Quel chiffre d\\'affaires avez-vous réalisé dans votre dernier poste ?',
                    unit='€',
                    sector_weight=0.9,
                    experience_dependent=True,
                    help_text='Montant annuel en euros'
                ),
                Question(
                    id='portefeuille_clients',
                    type=QuestionType.NUMBER,
                    question='Combien de clients aviez-vous en portefeuille ?',
                    min_value=0,
                    sector_weight=0.8,
                    experience_dependent=True
                ),
                Question(
                    id='techniques_vente',
                    type=QuestionType.MULTISELECT,
                    question='Quelles techniques de vente maîtrisez-vous ?',
                    options=[
                        'Prospection téléphonique',
                        'Négociation commerciale',
                        'Présentation produit',
                        'Closing de vente',
                        'Fidélisation client',
                        'Vente consultative',
                        'Account management'
                    ],
                    sector_weight=0.9
                ),
                Question(
                    id='secteurs_cibles',
                    type=QuestionType.MULTISELECT,
                    question='Dans quels secteurs avez-vous vendu ?',
                    options=[
                        'B2B Services',
                        'B2B Industrie',
                        'B2C Retail',
                        'Immobilier',
                        'Assurance',
                        'Technologie',
                        'Santé',
                        'Autre'
                    ],
                    sector_weight=0.7
                )
            ],
            
            # Questions spécifiques au secteur juridique
            'juridique': [
                Question(
                    id='domaines_juridiques',
                    type=QuestionType.MULTISELECT,
                    question='Dans quels domaines juridiques avez-vous de l\\'expérience ?',
                    options=[
                        'Droit civil',
                        'Droit commercial',
                        'Droit social',
                        'Droit pénal',
                        'Contentieux',
                        'Contrats',
                        'Propriété intellectuelle',
                        'Droit immobilier',
                        'Aucune expérience juridique'
                    ],
                    sector_weight=0.95,
                    required=True
                ),
                Question(
                    id='redaction_juridique',
                    type=QuestionType.SCALE,
                    question='Évaluez votre niveau en rédaction juridique',
                    min_value=1,
                    max_value=10,
                    sector_weight=0.9,
                    help_text='1 = Débutant, 10 = Expert'
                ),
                Question(
                    id='veille_juridique',
                    type=QuestionType.BOOLEAN,
                    question='Avez-vous de l\\'expérience en veille juridique/réglementaire ?',
                    sector_weight=0.8
                ),
                Question(
                    id='formation_juridique',
                    type=QuestionType.SELECT,
                    question='Quelle est votre formation juridique la plus élevée ?',
                    options=[
                        'Aucune formation juridique',
                        'Initiation au droit',
                        'Licence de droit',
                        'Master 1 droit',
                        'Master 2 droit',
                        'Doctorat en droit',
                        'Formation professionnelle juridique'
                    ],
                    sector_weight=0.85,
                    required=True
                )
            ],
            
            # Questions spécifiques à la comptabilité
            'comptabilité': [
                Question(
                    id='logiciels_comptables',
                    type=QuestionType.MULTISELECT,
                    question='Quels logiciels comptables maîtrisez-vous ?',
                    options=[
                        'Sage',
                        'SAP',
                        'QuickBooks',
                        'Ciel',
                        'EBP',
                        'Oracle',
                        'Excel avancé',
                        'Aucun'
                    ],
                    sector_weight=0.9,
                    required=True
                ),
                Question(
                    id='operations_comptables',
                    type=QuestionType.MULTISELECT,
                    question='Quelles opérations comptables savez-vous effectuer ?',
                    options=[
                        'Saisie comptable',
                        'Rapprochements bancaires',
                        'Déclarations TVA',
                        'Bilan comptable',
                        'Compte de résultat',
                        'Paie',
                        'Immobilisations',
                        'Aucune'
                    ],
                    sector_weight=0.95
                ),
                Question(
                    id='formation_comptable',
                    type=QuestionType.SELECT,
                    question='Quelle est votre formation comptable ?',
                    options=[
                        'Aucune formation comptable',
                        'Initiation comptabilité',
                        'BTS Comptabilité',
                        'DCG',
                        'DSCG',
                        'DEC',
                        'Formation professionnelle comptable'
                    ],
                    sector_weight=0.9
                )
            ],
            
            # Questions pour les transitions sectorielles
            'transition': [
                Question(
                    id='raison_reconversion',
                    type=QuestionType.TEXTAREA,
                    question='Pourquoi souhaitez-vous changer de secteur d\\'activité ?',
                    sector_weight=0.8,
                    required=True,
                    placeholder='Ex: Passion, opportunités, évolution...'
                ),
                Question(
                    id='preparation_reconversion',
                    type=QuestionType.MULTISELECT,
                    question='Comment vous préparez-vous à cette transition ?',
                    options=[
                        'Formation en cours',
                        'Auto-formation',
                        'Stages/missions courtes',
                        'Réseau professionnel',
                        'Mentoring',
                        'Lectures spécialisées',
                        'Pas de préparation spécifique'
                    ],
                    sector_weight=0.9
                ),
                Question(
                    id='temps_transition',
                    type=QuestionType.SELECT,
                    question='Sur quelle période envisagez-vous cette transition ?',
                    options=[
                        'Immédiate (0-3 mois)',
                        'Court terme (3-6 mois)',
                        'Moyen terme (6-12 mois)',
                        'Long terme (1-2 ans)',
                        'Très long terme (2+ ans)'
                    ],
                    sector_weight=0.7
                )
            ]
        }
    
    def generate_candidate_questionnaire(self, cv_data: Dict[str, Any], 
                                       target_sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Génère un questionnaire adaptatif pour un candidat
        
        Args:
            cv_data: Données parsées du CV
            target_sector: Secteur cible si connu
            
        Returns:
            Questionnaire structuré avec métadonnées
        """
        
        # 1. Analyse du CV pour détecter le secteur actuel
        cv_text = self._extract_cv_text(cv_data)
        cv_sector_analysis = self.sector_analyzer.detect_sector(cv_text, 'cv')
        
        # 2. Identification des données manquantes
        missing_data = self._identify_missing_data(cv_data)
        
        # 3. Détermination du type de questionnaire
        is_sector_transition = (
            target_sector and 
            target_sector != cv_sector_analysis.primary_sector and
            cv_sector_analysis.confidence > 0.6
        )
        
        # 4. Sélection des questions
        questions = []
        
        # Questions communes (toujours incluses)
        questions.extend(self.question_bank['common'])
        
        # Questions sectorielles selon le CV
        if cv_sector_analysis.primary_sector in self.question_bank:
            sector_questions = self.question_bank[cv_sector_analysis.primary_sector]
            # Filtrer selon l'expérience
            experience_years = cv_data.get('annees_experience', 0)
            for q in sector_questions:
                if not q.experience_dependent or experience_years > 0:
                    questions.append(q)
        
        # Questions de transition si applicable
        if is_sector_transition:
            questions.extend(self.question_bank['transition'])
            
            # Questions spécifiques au secteur cible
            if target_sector in self.question_bank:
                target_questions = self.question_bank[target_sector]
                # Ajouter quelques questions clés du secteur cible
                key_questions = [q for q in target_questions if q.sector_weight >= 0.8][:3]
                questions.extend(key_questions)
        
        # 5. Questions de compensation selon données manquantes
        compensation_questions = self._generate_compensation_questions(missing_data)
        questions.extend(compensation_questions)
        
        # 6. Métadonnées du questionnaire
        questionnaire_id = self._generate_questionnaire_id(cv_data, target_sector)
        
        return {
            'questionnaire_id': questionnaire_id,
            'analysis': {
                'detected_cv_sector': cv_sector_analysis.primary_sector,
                'sector_confidence': cv_sector_analysis.confidence,
                'target_sector': target_sector,
                'is_sector_transition': is_sector_transition,
                'missing_data_identified': list(missing_data.keys())
            },
            'questions': [asdict(q) for q in questions],
            'metadata': {
                'total_questions': len(questions),
                'estimated_time_minutes': len(questions) * 1.5,
                'sectors_covered': list(set([
                    cv_sector_analysis.primary_sector,
                    target_sector
                ]) - {None}),
                'difficulty_level': self._calculate_difficulty_level(questions),
                'adaptation_factors': {
                    'experience_level': cv_data.get('annees_experience', 0),
                    'sector_confidence': cv_sector_analysis.confidence,
                    'missing_data_count': len(missing_data)
                }
            }
        }
    
    def _identify_missing_data(self, cv_data: Dict[str, Any]) -> Dict[str, str]:
        """Identifie les données manquantes dans le CV parsé"""
        missing = {}
        
        # Vérifications essentielles
        if not cv_data.get('competences') or len(cv_data.get('competences', [])) < 3:
            missing['competences'] = 'Compétences insuffisamment détaillées'
        
        if not cv_data.get('missions') or len(cv_data.get('missions', [])) < 2:
            missing['missions'] = 'Missions/expériences peu détaillées'
        
        if not cv_data.get('annees_experience') or cv_data.get('annees_experience') == 0:
            missing['experience_details'] = 'Années d\\'expérience non précisées'
        
        if not cv_data.get('formations'):
            missing['formations'] = 'Formations non mentionnées'
        
        if not cv_data.get('langues'):
            missing['langues'] = 'Compétences linguistiques non précisées'
        
        # Données qualitatives toujours manquantes du parsing
        missing['soft_skills'] = 'Compétences comportementales non extraites'
        missing['career_goals'] = 'Objectifs de carrière non précisés'
        missing['work_preferences'] = 'Préférences de travail non connues'
        
        return missing
    
    def _generate_compensation_questions(self, missing_data: Dict[str, str]) -> List[Question]:
        """Génère des questions pour compenser les données manquantes"""
        compensation_questions = []
        
        if 'competences' in missing_data:
            compensation_questions.append(Question(
                id='competences_detaillees',
                type=QuestionType.TEXTAREA,
                question='Listez vos principales compétences techniques et fonctionnelles',
                sector_weight=0.9,
                placeholder='Ex: Excel avancé, gestion de projet, négociation...',
                help_text='Soyez le plus précis possible'
            ))
        
        if 'soft_skills' in missing_data:
            compensation_questions.append(Question(
                id='soft_skills',
                type=QuestionType.MULTISELECT,
                question='Quelles sont vos principales qualités professionnelles ?',
                options=[
                    'Leadership',
                    'Travail en équipe',
                    'Communication',
                    'Autonomie',
                    'Créativité',
                    'Rigueur',
                    'Adaptabilité',
                    'Persévérance',
                    'Empathie',
                    'Organisation'
                ],
                sector_weight=0.6
            ))
        
        if 'career_goals' in missing_data:
            compensation_questions.append(Question(
                id='objectifs_carriere',
                type=QuestionType.TEXTAREA,
                question='Quels sont vos objectifs de carrière à 3-5 ans ?',
                sector_weight=0.7,
                placeholder='Ex: Évoluer vers un poste de management, me spécialiser...'
            ))
        
        return compensation_questions
    
    def integrate_questionnaire_responses(self, cv_data: Dict[str, Any], 
                                        questionnaire_response: QuestionnaireResponse) -> Dict[str, Any]:
        """
        Intègre les réponses du questionnaire dans le profil candidat
        
        Args:
            cv_data: Données originales du CV
            questionnaire_response: Réponses du questionnaire
            
        Returns:
            Profil candidat enrichi
        """
        
        enhanced_profile = cv_data.copy()
        
        # Ajout des données du questionnaire
        enhanced_profile['questionnaire_data'] = {
            'questionnaire_id': questionnaire_response.questionnaire_id,
            'responses': questionnaire_response.responses,
            'completion_rate': questionnaire_response.completion_rate,
            'sector_confidence_boost': questionnaire_response.sector_confidence_boost
        }
        
        # Enrichissement des compétences
        if 'competences_detaillees' in questionnaire_response.responses:
            additional_skills = self._parse_skills_text(
                questionnaire_response.responses['competences_detaillees']
            )
            existing_skills = enhanced_profile.get('competences', [])
            enhanced_profile['competences'] = list(set(existing_skills + additional_skills))
        
        # Ajout des soft skills
        if 'soft_skills' in questionnaire_response.responses:
            enhanced_profile['soft_skills'] = questionnaire_response.responses['soft_skills']
        
        # Enrichissement du profil sectoriel
        enhanced_profile['sector_analysis_enhanced'] = {
            'questionnaire_confirmed': True,
            'transition_readiness': self._calculate_transition_readiness(questionnaire_response),
            'adaptation_score': self._calculate_adaptation_score(questionnaire_response)
        }
        
        return enhanced_profile
    
    def _extract_cv_text(self, cv_data: Dict[str, Any]) -> str:
        """Extrait le texte pertinent du CV"""
        text_parts = []
        
        for field in ['competences', 'missions', 'titre_poste', 'formations']:
            values = cv_data.get(field, [])
            if isinstance(values, list):
                text_parts.extend(values)
            elif values:
                text_parts.append(str(values))
        
        return ' '.join(text_parts)
    
    def _generate_questionnaire_id(self, cv_data: Dict[str, Any], 
                                  target_sector: Optional[str]) -> str:
        """Génère un ID unique pour le questionnaire"""
        content = f"{cv_data}_{target_sector}_{hash(str(cv_data))}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_difficulty_level(self, questions: List[Question]) -> str:
        """Calcule le niveau de difficulté du questionnaire"""
        if len(questions) <= 8:
            return 'facile'
        elif len(questions) <= 15:
            return 'modéré'
        else:
            return 'difficile'
    
    def _parse_skills_text(self, text: str) -> List[str]:
        """Parse un texte de compétences en liste"""
        # Séparateurs communs
        separators = [',', ';', '\n', '-', '•']
        
        skills = [text]
        for sep in separators:
            new_skills = []
            for skill in skills:
                new_skills.extend(skill.split(sep))
            skills = new_skills
        
        # Nettoyage
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if len(skill) > 2:  # Ignore les compétences trop courtes
                cleaned_skills.append(skill)
        
        return cleaned_skills[:10]  # Maximum 10 compétences supplémentaires
    
    def _calculate_transition_readiness(self, response: QuestionnaireResponse) -> float:
        """Calcule le score de préparation à la transition"""
        readiness_factors = []
        
        if 'formation_complementaire' in response.responses:
            readiness_factors.append(0.3 if response.responses['formation_complementaire'] else 0.0)
        
        if 'preparation_reconversion' in response.responses:
            prep_actions = response.responses['preparation_reconversion']
            if isinstance(prep_actions, list):
                readiness_factors.append(min(0.4, len(prep_actions) * 0.1))
        
        if 'adaptabilite_score' in response.responses:
            adaptability = response.responses['adaptabilite_score']
            if isinstance(adaptability, (int, float)):
                readiness_factors.append((adaptability / 10) * 0.3)
        
        return sum(readiness_factors) if readiness_factors else 0.5
    
    def _calculate_adaptation_score(self, response: QuestionnaireResponse) -> float:
        """Calcule un score d'adaptation basé sur les réponses"""
        base_score = 0.5
        
        # Bonus pour les réponses complètes
        completion_bonus = response.completion_rate * 0.2
        
        # Bonus pour les compétences transférables mentionnées
        if 'competences_transferables' in response.responses:
            text = response.responses['competences_transferables']
            if isinstance(text, str) and len(text) > 50:
                base_score += 0.2
        
        return min(1.0, base_score + completion_bonus)

# Fonction utilitaire pour utilisation simple
def create_questionnaire_for_candidate(cv_data: Dict[str, Any], 
                                     target_sector: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour créer un questionnaire adaptatif
    
    Usage:
        questionnaire = create_questionnaire_for_candidate(zachary_cv, 'juridique')
    """
    engine = AdaptiveQuestionnaireEngine()
    return engine.generate_candidate_questionnaire(cv_data, target_sector)

if __name__ == '__main__':
    """Test du module avec le cas Zachary"""
    
    # Données de test Zachary
    zachary_cv = {
        "competences": ["Prospection commerciale", "Relation client", "CRM"],
        "missions": ["Développement du portefeuille client"],
        "titre_poste": "Assistant commercial",
        "annees_experience": 1,
        "adresse": "Paris"
    }
    
    # Test de génération de questionnaire
    questionnaire = create_questionnaire_for_candidate(zachary_cv, 'juridique')
    
    print("🧪 TEST QUESTIONNAIRE ADAPTATIF")
    print("=" * 50)
    print(f"CV Secteur détecté: {questionnaire['analysis']['detected_cv_sector']}")
    print(f"Secteur cible: {questionnaire['analysis']['target_sector']}")
    print(f"Transition sectorielle: {questionnaire['analysis']['is_sector_transition']}")
    print(f"Nombre de questions: {questionnaire['metadata']['total_questions']}")
    print(f"Temps estimé: {questionnaire['metadata']['estimated_time_minutes']:.1f} minutes")
    
    print("\n📋 Questions générées:")
    for i, q in enumerate(questionnaire['questions'][:5], 1):
        print(f"{i}. [{q['type']}] {q['question']}")
    
    if len(questionnaire['questions']) > 5:
        print(f"... et {len(questionnaire['questions']) - 5} autres questions")
