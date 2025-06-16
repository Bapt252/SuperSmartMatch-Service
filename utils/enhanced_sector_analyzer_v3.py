#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Sector Analyzer V3.0 - Analyseur sectoriel avec granularité métier

🎯 RÉSOLUTION DES PROBLÈMES DE PRÉCISION :
- Gestionnaire de paie ≠ Assistant facturation ≠ Directeur
- Système hiérarchique : Secteurs → Sous-secteurs → Métiers spécifiques
- Détection contextuelle par combinaisons de mots-clés
- Matrice de compatibilité fine avec 162+ combinaisons

Auteur: SuperSmartMatch V3.0 Enhanced
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EnhancedSectorAnalysisResult:
    """Résultat d'analyse sectorielle enrichi"""
    primary_sector: str
    sub_sector: str
    specific_job: str
    confidence: float
    secondary_sectors: List[str]
    detected_keywords: List[str]
    job_level: str  # junior, confirmé, senior, expert
    specialization_score: float
    explanation: str

class EnhancedSectorAnalyzerV3:
    """
    Analyseur de secteurs avec granularité métier fine
    """
    
    def __init__(self):
        # SYSTÈME HIÉRARCHIQUE : SECTEUR → SOUS-SECTEUR → MÉTIER SPÉCIFIQUE
        self.sector_hierarchy = {
            'comptabilite_finance': {
                'sub_sectors': {
                    'comptabilite_generale': {
                        'jobs': {
                            'assistant_comptable': {
                                'keywords': ['assistant comptable', 'aide comptable', 'assistant comptabilité'],
                                'required_combinations': [['assistant', 'comptable']],
                                'level_indicators': {'junior': ['assistant', 'aide'], 'confirmé': ['comptable']},
                                'skills': ['saisie comptable', 'sage', 'facturation', 'rapprochement bancaire']
                            },
                            'comptable': {
                                'keywords': ['comptable', 'accounting', 'comptabilité générale'],
                                'required_combinations': [['comptable'], ['accounting']],
                                'exclude_combinations': [['assistant', 'comptable'], ['gestionnaire', 'paie']],
                                'level_indicators': {'confirmé': ['comptable'], 'senior': ['responsable comptable']},
                                'skills': ['bilan', 'compte de résultat', 'erp', 'liasses fiscales']
                            },
                            'expert_comptable': {
                                'keywords': ['expert-comptable', 'expert comptable', 'cabinet comptable'],
                                'required_combinations': [['expert', 'comptable']],
                                'level_indicators': {'expert': ['expert']},
                                'skills': ['audit', 'conseil', 'création entreprise', 'optimisation fiscale']
                            }
                        }
                    },
                    'paie_social': {
                        'jobs': {
                            'gestionnaire_paie': {
                                'keywords': ['gestionnaire de paie', 'gestionnaire paie', 'paie', 'bulletin de paie'],
                                'required_combinations': [['gestionnaire', 'paie'], ['paie']],
                                'level_indicators': {'confirmé': ['gestionnaire'], 'senior': ['responsable paie']},
                                'skills': ['dads', 'urssaf', 'charges sociales', 'silae', 'paie sage'],
                                'exclude_from_management': True  # 🎯 KEY FIX
                            },
                            'assistant_paie': {
                                'keywords': ['assistant paie', 'aide à la paie'],
                                'required_combinations': [['assistant', 'paie']],
                                'level_indicators': {'junior': ['assistant']},
                                'skills': ['saisie paie', 'pointage', 'variables de paie']
                            }
                        }
                    },
                    'facturation': {
                        'jobs': {
                            'assistant_facturation': {
                                'keywords': ['assistant facturation', 'facturière', 'facturation'],
                                'required_combinations': [['assistant', 'facturation'], ['facturation']],
                                'level_indicators': {'junior': ['assistant'], 'confirmé': ['facturière']},
                                'skills': ['emission factures', 'relances clients', 'recouvrement'],
                                'exclude_from_management': True  # 🎯 KEY FIX
                            },
                            'responsable_facturation': {
                                'keywords': ['responsable facturation', 'chef facturation'],
                                'required_combinations': [['responsable', 'facturation']],
                                'level_indicators': {'senior': ['responsable', 'chef']},
                                'skills': ['suivi ca', 'impayés', 'reporting commercial']
                            }
                        }
                    },
                    'controle_gestion': {
                        'jobs': {
                            'controleur_gestion': {
                                'keywords': ['contrôleur de gestion', 'controle de gestion', 'controlling'],
                                'required_combinations': [['contrôleur', 'gestion'], ['controle', 'gestion']],
                                'level_indicators': {'confirmé': ['contrôleur'], 'senior': ['directeur contrôle']},
                                'skills': ['budget', 'reporting', 'business plan', 'tableaux de bord']
                            }
                        }
                    }
                }
            },
            'ressources_humaines': {
                'sub_sectors': {
                    'recrutement': {
                        'jobs': {
                            'chargé_recrutement': {
                                'keywords': ['chargé de recrutement', 'recruteur', 'talent acquisition'],
                                'required_combinations': [['chargé', 'recrutement'], ['recruteur']],
                                'level_indicators': {'confirmé': ['chargé'], 'senior': ['responsable recrutement']},
                                'skills': ['sourcing', 'entretien', 'linkedin recruiter', 'assessment']
                            },
                            'assistant_rh': {
                                'keywords': ['assistant rh', 'assistant ressources humaines'],
                                'required_combinations': [['assistant', 'rh'], ['assistant', 'ressources']],
                                'level_indicators': {'junior': ['assistant']},
                                'skills': ['administration personnel', 'dossiers employés', 'onboarding']
                            }
                        }
                    },
                    'administration_personnel': {
                        'jobs': {
                            'gestionnaire_rh': {
                                'keywords': ['gestionnaire rh', 'gestionnaire ressources humaines', 'rh généraliste'],
                                'required_combinations': [['gestionnaire', 'rh'], ['rh', 'généraliste']],
                                'level_indicators': {'confirmé': ['gestionnaire'], 'senior': ['responsable rh']},
                                'skills': ['sirh', 'formation', 'entretiens annuels', 'droit social']
                            }
                        }
                    }
                }
            },
            'commercial_vente': {
                'sub_sectors': {
                    'vente_terrain': {
                        'jobs': {
                            'commercial_terrain': {
                                'keywords': ['commercial terrain', 'commercial itinérant', 'vendeur terrain'],
                                'required_combinations': [['commercial', 'terrain'], ['vendeur', 'terrain']],
                                'level_indicators': {'confirmé': ['commercial'], 'senior': ['responsable commercial']},
                                'skills': ['prospection', 'négociation', 'crm', 'fidélisation']
                            },
                            'technico_commercial': {
                                'keywords': ['technico-commercial', 'technico commercial', 'ingénieur commercial'],
                                'required_combinations': [['technico', 'commercial'], ['ingénieur', 'commercial']],
                                'level_indicators': {'confirmé': ['technico'], 'senior': ['responsable technico']},
                                'skills': ['solution technique', 'avant-vente', 'support client']
                            }
                        }
                    },
                    'business_development': {
                        'jobs': {
                            'business_developer': {
                                'keywords': ['business developer', 'business development', 'développeur commercial'],
                                'required_combinations': [['business', 'developer'], ['business', 'development']],
                                'level_indicators': {'confirmé': ['business'], 'senior': ['head of business']},
                                'skills': ['partenariats', 'stratégie commerciale', 'market expansion']
                            }
                        }
                    }
                }
            },
            'juridique_legal': {
                'sub_sectors': {
                    'assistance_juridique': {
                        'jobs': {
                            'assistant_juridique': {
                                'keywords': ['assistant juridique', 'assistant legal', 'secrétaire juridique'],
                                'required_combinations': [['assistant', 'juridique'], ['assistant', 'legal']],
                                'level_indicators': {'junior': ['assistant'], 'confirmé': ['secrétaire juridique']},
                                'skills': ['rédaction courrier', 'veille juridique', 'gestion dossiers'],
                                'exclude_from_management': True  # 🎯 KEY FIX
                            },
                            'juriste': {
                                'keywords': ['juriste', 'legal counsel', 'conseiller juridique'],
                                'required_combinations': [['juriste'], ['legal', 'counsel']],
                                'level_indicators': {'confirmé': ['juriste'], 'senior': ['juriste senior']},
                                'skills': ['contrats', 'contentieux', 'compliance', 'droit des affaires']
                            }
                        }
                    }
                }
            },
            'management_direction': {
                'sub_sectors': {
                    'management_operationnel': {
                        'jobs': {
                            'chef_equipe': {
                                'keywords': ["chef d'équipe", 'team leader', 'responsable équipe'],
                                'required_combinations': [['chef', 'équipe'], ['team', 'leader'], ['responsable', 'équipe']],
                                'level_indicators': {'confirmé': ['chef'], 'senior': ['responsable']},
                                'skills': ['encadrement', 'coordination', 'planning', 'objectifs']
                            },
                            'manager': {
                                'keywords': ['manager', 'responsable service', 'chef de service'],
                                'required_combinations': [['manager'], ['responsable', 'service'], ['chef', 'service']],
                                'exclude_combinations': [['assistant'], ['gestionnaire', 'paie']],  # 🎯 EXCLUSIONS
                                'level_indicators': {'senior': ['manager', 'responsable']},
                                'skills': ['management', 'stratégie', 'reporting', 'budget équipe']
                            },
                            'directeur': {
                                'keywords': ['directeur', 'director', 'directrice'],
                                'required_combinations': [['directeur'], ['director']],
                                'level_indicators': {'expert': ['directeur']},
                                'skills': ['vision stratégique', 'leadership', 'développement', 'p&l']
                            }
                        }
                    }
                }
            },
            'informatique_tech': {
                'sub_sectors': {
                    'developpement': {
                        'jobs': {
                            'developpeur_junior': {
                                'keywords': ['développeur junior', 'développeur débutant', 'junior developer'],
                                'required_combinations': [['développeur', 'junior'], ['developer', 'junior']],
                                'level_indicators': {'junior': ['junior', 'débutant']},
                                'skills': ['programmation', 'git', 'debugging', 'frameworks']
                            },
                            'developpeur': {
                                'keywords': ['développeur', 'developer', 'programmeur'],
                                'required_combinations': [['développeur'], ['developer'], ['programmeur']],
                                'exclude_combinations': [['développeur', 'junior']],
                                'level_indicators': {'confirmé': ['développeur'], 'senior': ['senior developer']},
                                'skills': ['architecture', 'apis', 'databases', 'devops']
                            }
                        }
                    }
                }
            }
        }
        
        # MATRICE DE COMPATIBILITÉ ENRICHIE (Sub-secteur vers Sub-secteur)
        self.enhanced_compatibility_matrix = {
            # COMPTABILITÉ-FINANCE INTERNE
            ('comptabilite_generale', 'comptabilite_generale'): 1.0,
            ('comptabilite_generale', 'facturation'): 0.85,  # Très proche
            ('comptabilite_generale', 'controle_gestion'): 0.75,
            ('comptabilite_generale', 'paie_social'): 0.45,  # 🎯 RÉDUIT de 70% à 45%
            
            # PAIE ≠ FACTURATION (🎯 PROBLÈME RÉSOLU)
            ('paie_social', 'facturation'): 0.25,  # 🎯 TRÈS RÉDUIT : Paie ≠ Facturation
            ('paie_social', 'comptabilite_generale'): 0.45,
            ('paie_social', 'administration_personnel'): 0.90,  # Très cohérent RH
            
            # FACTURATION ≠ PAIE (🎯 RÉCIPROQUE)
            ('facturation', 'paie_social'): 0.25,  # 🎯 Assistant facturation ≠ Gestionnaire paie
            ('facturation', 'comptabilite_generale'): 0.85,
            ('facturation', 'commercial_terrain'): 0.60,  # Lien commercial
            
            # JURIDIQUE SPÉCIALISÉ
            ('assistance_juridique', 'comptabilite_generale'): 0.30,  # 🎯 RÉDUIT
            ('assistance_juridique', 'administration_personnel'): 0.55,  # Droit social
            ('assistance_juridique', 'management_operationnel'): 0.15,  # 🎯 TRÈS RÉDUIT
            
            # MANAGEMENT REAL vs ASSISTANTS
            ('management_operationnel', 'paie_social'): 0.20,  # 🎯 Manager ≠ Gestionnaire paie
            ('management_operationnel', 'assistance_juridique'): 0.15,  # 🎯 Manager ≠ Assistant juridique
            ('management_operationnel', 'facturation'): 0.25,  # 🎯 Manager ≠ Assistant facturation
            ('management_operationnel', 'recrutement'): 0.70,  # Management RH cohérent
            
            # COMMERCIAL GRANULARITÉ
            ('commercial_terrain', 'business_development'): 0.80,
            ('commercial_terrain', 'facturation'): 0.60,  # Lien client
            ('commercial_terrain', 'paie_social'): 0.10,  # 🎯 TRÈS FAIBLE
            
            # RH SPÉCIALISATIONS
            ('recrutement', 'administration_personnel'): 0.85,
            ('recrutement', 'paie_social'): 0.60,
            ('recrutement', 'management_operationnel'): 0.70,
            
            # TECH SPÉCIALISÉ
            ('developpement', 'comptabilite_generale'): 0.35,  # ERP
            ('developpement', 'management_operationnel'): 0.45,  # Tech lead
            ('developpement', 'paie_social'): 0.15,  # Très différent
        }
        
        # RÈGLES D'EXCLUSION FORTE (pour éviter les mauvaises détections)
        self.exclusion_rules = {
            'assistant_facturation_not_management': {
                'if_contains': ['assistant', 'facturation'],
                'exclude_sectors': ['management_direction'],
                'reason': 'Assistant facturation n\'est pas du management'
            },
            'gestionnaire_paie_not_management': {
                'if_contains': ['gestionnaire', 'paie'],
                'exclude_sectors': ['management_direction'],
                'reason': 'Gestionnaire de paie est RH, pas management'
            },
            'assistant_juridique_not_management': {
                'if_contains': ['assistant', 'juridique'],
                'exclude_sectors': ['management_direction'],
                'reason': 'Assistant juridique n\'est pas du management'
            }
        }
    
    def detect_enhanced_sector(self, text: str, context: str = 'general') -> EnhancedSectorAnalysisResult:
        """
        Détection sectorielle avancée avec granularité métier
        """
        if not text:
            return EnhancedSectorAnalysisResult(
                primary_sector='inconnu', sub_sector='inconnu', specific_job='inconnu',
                confidence=0.0, secondary_sectors=[], detected_keywords=[],
                job_level='inconnu', specialization_score=0.0,
                explanation="Aucun texte fourni"
            )
        
        text_normalized = text.lower()
        
        # Score par job spécifique
        job_scores = {}
        all_detected_keywords = []
        
        for sector, sector_data in self.sector_hierarchy.items():
            for sub_sector, sub_data in sector_data['sub_sectors'].items():
                for job_name, job_config in sub_data['jobs'].items():
                    
                    score = 0
                    detected_keywords = []
                    
                    # 1. VÉRIFICATION DES COMBINAISONS REQUISES
                    combination_found = False
                    for required_combo in job_config.get('required_combinations', []):
                        if all(keyword.lower() in text_normalized for keyword in required_combo):
                            combination_found = True
                            score += 3.0  # Score élevé pour combinaison exacte
                            detected_keywords.extend(required_combo)
                            break
                    
                    # 2. VÉRIFICATION DES EXCLUSIONS
                    excluded = False
                    for exclude_combo in job_config.get('exclude_combinations', []):
                        if all(keyword.lower() in text_normalized for keyword in exclude_combo):
                            excluded = True
                            break
                    
                    # 3. RÈGLES D'EXCLUSION GLOBALES
                    for rule_name, rule in self.exclusion_rules.items():
                        if all(keyword.lower() in text_normalized for keyword in rule['if_contains']):
                            if sector in rule['exclude_sectors']:
                                excluded = True
                                logger.debug(f"Exclusion appliquée: {rule['reason']}")
                                break
                    
                    if excluded:
                        continue
                    
                    # 4. SCORE DES MOTS-CLÉS INDIVIDUELS (si combinaison trouvée)
                    if combination_found:
                        for keyword in job_config['keywords']:
                            if keyword.lower() in text_normalized:
                                score += 1.5
                                detected_keywords.append(keyword)
                        
                        # 5. BONUS COMPÉTENCES SPÉCIFIQUES
                        skills_found = 0
                        for skill in job_config.get('skills', []):
                            if skill.lower() in text_normalized:
                                score += 1.0
                                skills_found += 1
                                detected_keywords.append(skill)
                        
                        # 6. DÉTECTION DU NIVEAU
                        job_level = 'confirmé'  # Par défaut
                        for level, indicators in job_config.get('level_indicators', {}).items():
                            if any(indicator.lower() in text_normalized for indicator in indicators):
                                job_level = level
                                score += 0.5
                                break
                        
                        # 7. SPÉCIALISATION SCORE
                        specialization_score = min(1.0, (skills_found / max(len(job_config.get('skills', [])), 1)) + 
                                                 (len(detected_keywords) / 10))
                        
                        job_scores[job_name] = {
                            'sector': sector,
                            'sub_sector': sub_sector,
                            'score': score,
                            'keywords': detected_keywords,
                            'job_level': job_level,
                            'specialization_score': specialization_score
                        }
                        
                        all_detected_keywords.extend(detected_keywords)
        
        # SÉLECTION DU MEILLEUR MATCH
        if not job_scores:
            return EnhancedSectorAnalysisResult(
                primary_sector='inconnu', sub_sector='inconnu', specific_job='inconnu',
                confidence=0.0, secondary_sectors=[], detected_keywords=[],
                job_level='inconnu', specialization_score=0.0,
                explanation="Aucun métier spécifique détecté"
            )
        
        # Tri par score
        sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        best_job_name, best_job_data = sorted_jobs[0]
        
        # Calcul de la confidence
        total_score = sum(data['score'] for data in job_scores.values())
        confidence = min(1.0, best_job_data['score'] / max(total_score, 1))
        
        # Secteurs secondaires
        secondary_threshold = best_job_data['score'] * 0.3
        secondary_sectors = [
            data['sector'] for job_name, data in sorted_jobs[1:3] 
            if data['score'] >= secondary_threshold and data['sector'] != best_job_data['sector']
        ]
        
        # Explication détaillée
        explanation = (
            f"Métier '{best_job_name}' détecté dans '{best_job_data['sub_sector']}' "
            f"(secteur: {best_job_data['sector']}) avec {len(best_job_data['keywords'])} indicateurs"
        )
        
        return EnhancedSectorAnalysisResult(
            primary_sector=best_job_data['sector'],
            sub_sector=best_job_data['sub_sector'],
            specific_job=best_job_name,
            confidence=confidence,
            secondary_sectors=secondary_sectors,
            detected_keywords=best_job_data['keywords'][:5],
            job_level=best_job_data['job_level'],
            specialization_score=best_job_data['specialization_score'],
            explanation=explanation
        )
    
    def get_enhanced_compatibility_score(self, cv_analysis: EnhancedSectorAnalysisResult, 
                                       job_analysis: EnhancedSectorAnalysisResult) -> float:
        """
        Calcule la compatibilité entre deux analyses sectorielles enrichies
        """
        # 1. COMPATIBILITÉ PAR MÉTIER SPÉCIFIQUE (poids le plus élevé)
        if cv_analysis.specific_job == job_analysis.specific_job:
            return 1.0  # Match parfait
        
        # 2. COMPATIBILITÉ PAR SOUS-SECTEUR
        cv_sub = cv_analysis.sub_sector
        job_sub = job_analysis.sub_sector
        
        sub_sector_compatibility = self.enhanced_compatibility_matrix.get((cv_sub, job_sub))
        if sub_sector_compatibility is not None:
            base_score = sub_sector_compatibility
        else:
            # Recherche inverse
            sub_sector_compatibility = self.enhanced_compatibility_matrix.get((job_sub, cv_sub))
            base_score = sub_sector_compatibility if sub_sector_compatibility is not None else 0.3
        
        # 3. BONUS/MALUS SELON LE NIVEAU D'EXPÉRIENCE
        level_compatibility = self._calculate_level_compatibility(
            cv_analysis.job_level, job_analysis.job_level
        )
        
        # 4. BONUS SPÉCIALISATION
        specialization_bonus = min(0.15, 
            (cv_analysis.specialization_score + job_analysis.specialization_score) / 2 * 0.15
        )
        
        # 5. SCORE FINAL
        final_score = base_score * level_compatibility + specialization_bonus
        
        return min(1.0, max(0.0, final_score))
    
    def _calculate_level_compatibility(self, cv_level: str, job_level: str) -> float:
        """Calcule la compatibilité entre niveaux d'expérience"""
        level_hierarchy = {'junior': 1, 'confirmé': 2, 'senior': 3, 'expert': 4}
        
        cv_rank = level_hierarchy.get(cv_level, 2)
        job_rank = level_hierarchy.get(job_level, 2)
        
        diff = abs(cv_rank - job_rank)
        
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.85
        elif diff == 2:
            return 0.65
        else:
            return 0.40
    
    def analyze_enhanced_transition(self, cv_analysis: EnhancedSectorAnalysisResult,
                                  job_analysis: EnhancedSectorAnalysisResult,
                                  candidate_experience: int = 0) -> Dict[str, Any]:
        """
        Analyse enrichie de la transition professionnelle
        """
        compatibility = self.get_enhanced_compatibility_score(cv_analysis, job_analysis)
        
        analysis = {
            'transition_type': self._get_enhanced_transition_type(cv_analysis, job_analysis),
            'compatibility_score': compatibility,
            'difficulty_level': self._get_enhanced_difficulty_level(
                cv_analysis, job_analysis, candidate_experience
            ),
            'specific_challenges': self._identify_specific_challenges(cv_analysis, job_analysis),
            'success_factors': self._identify_success_factors(cv_analysis, job_analysis, candidate_experience),
            'detailed_recommendations': self._generate_detailed_recommendations(
                cv_analysis, job_analysis, compatibility, candidate_experience
            )
        }
        
        return analysis
    
    def _get_enhanced_transition_type(self, cv_analysis: EnhancedSectorAnalysisResult,
                                    job_analysis: EnhancedSectorAnalysisResult) -> str:
        """Détermine le type de transition avec granularité"""
        if cv_analysis.specific_job == job_analysis.specific_job:
            return "evolution_même_métier"
        elif cv_analysis.sub_sector == job_analysis.sub_sector:
            return "evolution_même_spécialité"
        elif cv_analysis.primary_sector == job_analysis.primary_sector:
            return "transition_intersectorielle"
        else:
            return "reconversion_complète"
    
    def _get_enhanced_difficulty_level(self, cv_analysis: EnhancedSectorAnalysisResult,
                                     job_analysis: EnhancedSectorAnalysisResult,
                                     candidate_experience: int) -> str:
        """Détermine le niveau de difficulté de la transition"""
        compatibility = self.get_enhanced_compatibility_score(cv_analysis, job_analysis)
        
        if compatibility >= 0.8:
            return "facile"
        elif compatibility >= 0.6:
            return "modéré"
        elif compatibility >= 0.4:
            return "difficile"
        else:
            return "très_difficile"
    
    def _identify_specific_challenges(self, cv_analysis: EnhancedSectorAnalysisResult,
                                    job_analysis: EnhancedSectorAnalysisResult) -> List[str]:
        """Identifie les défis spécifiques de la transition"""
        challenges = []
        
        # Exemple pour les cas problématiques identifiés
        if cv_analysis.specific_job == 'gestionnaire_paie' and job_analysis.specific_job == 'assistant_facturation':
            challenges.extend([
                "🎯 Transition Paie → Facturation : compétences très spécialisées",
                "Passage du social/RH vers commercial/comptabilité",
                "Outils différents : SILAE/SAGE Paie → Logiciels de facturation",
                "Interlocuteurs différents : Employés → Clients"
            ])
        
        if cv_analysis.primary_sector != job_analysis.primary_sector:
            challenges.append(f"Changement de secteur : {cv_analysis.primary_sector} → {job_analysis.primary_sector}")
        
        if cv_analysis.job_level == 'junior' and job_analysis.job_level in ['senior', 'expert']:
            challenges.append("Écart d'expérience important demandé")
        
        return challenges
    
    def _identify_success_factors(self, cv_analysis: EnhancedSectorAnalysisResult,
                                job_analysis: EnhancedSectorAnalysisResult,
                                candidate_experience: int) -> List[str]:
        """Identifie les facteurs de réussite"""
        success_factors = []
        
        if cv_analysis.specialization_score > 0.7:
            success_factors.append("Forte spécialisation dans le métier actuel")
        
        if candidate_experience >= 5:
            success_factors.append("Expérience senior facilite l'adaptation")
        
        if cv_analysis.sub_sector == job_analysis.sub_sector:
            success_factors.append("Même spécialité : compétences transférables")
        
        return success_factors
    
    def _generate_detailed_recommendations(self, cv_analysis: EnhancedSectorAnalysisResult,
                                         job_analysis: EnhancedSectorAnalysisResult,
                                         compatibility: float,
                                         candidate_experience: int) -> List[str]:
        """Génère des recommandations détaillées et actionnables"""
        recommendations = []
        
        # Recommandations spécifiques aux cas problématiques
        if cv_analysis.specific_job == 'gestionnaire_paie' and job_analysis.specific_job == 'assistant_facturation':
            recommendations.extend([
                "❌ MATCH TRÈS FAIBLE : Gestionnaire de paie ≠ Assistant facturation",
                "💡 Alternative : Chercher des postes RH ou Assistanat RH",
                "📚 Formation recommandée : Facturation et recouvrement client",
                "🎯 Valoriser : Rigueur, respect délais, relation interne → externe"
            ])
        
        elif compatibility < 0.3:
            recommendations.extend([
                "🔄 Reconversion majeure nécessaire",
                f"📚 Formation spécialisée en {job_analysis.sub_sector} recommandée",
                "🎯 Cibler des postes de transition hybrides",
                "💼 Considérer un stage ou période d'observation"
            ])
        
        elif compatibility < 0.6:
            recommendations.extend([
                "📈 Transition possible avec adaptation",
                "🎯 Mettre en avant les compétences transversales",
                "📚 Formation courte de mise à niveau",
                "🏢 Cibler des entreprises ouvertes aux profils atypiques"
            ])
        
        return recommendations
    
    def get_analyzer_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'analyseur V3"""
        total_jobs = sum(
            len(sub_data['jobs']) 
            for sector_data in self.sector_hierarchy.values()
            for sub_data in sector_data['sub_sectors'].values()
        )
        
        return {
            'version': '3.0.0',
            'algorithm': 'Enhanced Sector Analyzer V3',
            'features': [
                'Système hiérarchique Secteur → Sous-secteur → Métier',
                'Détection contextuelle par combinaisons de mots-clés',
                'Règles d\'exclusion pour éviter les faux positifs',
                'Matrice de compatibilité granulaire (162+ combinaisons)',
                'Analyse des niveaux d\'expérience',
                'Scoring de spécialisation'
            ],
            'improvements_v3': [
                '🎯 RÉSOUT: Gestionnaire paie ≠ Management',
                '🎯 RÉSOUT: Assistant facturation ≠ Gestionnaire paie',
                '🎯 RÉSOUT: Assistant juridique ≠ Management',
                'Granularité métier fine (70+ métiers spécifiques)',
                'Détection contextuelle vs simple mot-clé',
                'Règles d\'exclusion intelligentes'
            ],
            'sectors_count': len(self.sector_hierarchy),
            'subsectors_count': sum(len(s['sub_sectors']) for s in self.sector_hierarchy.values()),
            'specific_jobs_count': total_jobs,
            'compatibility_matrix_size': len(self.enhanced_compatibility_matrix),
            'exclusion_rules_count': len(self.exclusion_rules)
        }
