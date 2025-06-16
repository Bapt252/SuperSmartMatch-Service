# 🚀 SuperSmartMatch V2.1 - Test Massif

Script automatisé pour tester SuperSmartMatch V2.1 sur de gros volumes de données réelles.

## 🎯 Objectif

Valider l'algorithme Enhanced V2.1 avec intelligence sectorielle sur tous vos CVs et fiches de poste automatiquement.

## ✨ Fonctionnalités

### 🔍 **Traitement 100% automatique**
- Scanne automatiquement les dossiers CVs et fiches de poste
- Extrait le texte de tous les PDFs (pdfplumber + PyPDF2 fallback)
- Détecte automatiquement : secteurs, compétences, années d'expérience
- Effectue tous les matchings possibles (CV × Fiche de poste)

### 🧠 **Intelligence de parsing**
- **9 secteurs français** : commercial, juridique, comptabilité, informatique, marketing, RH, finance, production, management
- **Extraction d'expérience** : Patterns regex avancés pour détecter les années
- **Détection de compétences** : Analyse sémantique + mots-clés sectoriels
- **Secteur automatique** : Classification intelligente basée sur le contenu

### 📊 **Rapports complets**
- **CSV détaillé** : Tous les résultats de matching exportés
- **Dashboard HTML** : Statistiques visuelles, top matches, analyse sectorielle
- **Métriques avancées** : Scores min/max/moyen, distribution par secteur, recommandations

## 🚀 Installation

```bash
# Installation des dépendances
pip install -r requirements.txt

# Ou installation manuelle
pip install pandas requests pdfplumber PyPDF2
```

## ⚙️ Configuration

### Prérequis
1. **SuperSmartMatch V2.1 démarré** :
```bash
cd /Users/baptistecomas/Commitment-/Commitment-/SuperSmartMatch-Service
PORT=5061 python app.py
```

2. **Dossiers de test** :
- CVs : `/Users/baptistecomas/Desktop/CV TEST/`
- Fiches de poste : `/Users/baptistecomas/Desktop/FDP TEST/`

### Personnalisation
Modifiez les chemins dans `test_massif.py` si nécessaire :
```python
self.cv_folder = "/votre/chemin/CVs/"
self.job_folder = "/votre/chemin/Jobs/"
```

## 🎯 Utilisation

### Lancement simple
```bash
python test_massif.py
```

### Exemple de sortie
```bash
🚀 SuperSmartMatch V2.1 - Mass Testing Tool
==================================================
✅ pdfplumber disponible (recommandé)
✅ API SuperSmartMatch V2.1 disponible

🔍 Scanning /Users/baptistecomas/Desktop/CV TEST/...
✅ 25 fichiers CV trouvés

🔍 Scanning /Users/baptistecomas/Desktop/FDP TEST/...
✅ 15 fichiers fiche de poste trouvés

🧠 Traitement prévu: 25 CVs × 15 postes = 375 matchings

📄 Traitement des CVs...
📋 Traitement des fiches de poste...
🎯 Exécution des matchings...
📊 Génération des rapports...

✅ TEST MASSIF TERMINÉ!
⏱️  Durée totale: 42.3 secondes
📄 CVs traités: 25
📋 Jobs traités: 15
🎯 Matchings réalisés: 375
```

## 📈 Résultats

### Fichiers générés
- `resultats_matching_YYYY-MM-DD_HH-MM-SS.csv` : Données brutes
- `rapport_matching_YYYY-MM-DD_HH-MM-SS.html` : Dashboard visuel

### Métriques incluses
- **Scores de matching** : Min/Max/Moyen par secteur
- **Top 10 matches** : Meilleurs et pires résultats
- **Analyse sectorielle** : Distribution et performance par secteur
- **Recommandations** : Suggestions d'amélioration automatiques

## 🔧 Algorithmes testés

Le script utilise **Enhanced V2.1** par défaut, l'algorithme le plus avancé :

- ✅ **enhanced-v2** : Intelligence sectorielle française (recommandé)
- semantic : Analyse sémantique des compétences  
- hybrid : Combinaison des algorithmes
- auto : Sélection automatique

## 📊 Secteurs supportés

| Secteur | Mots-clés détectés |
|---------|-------------------|
| **Commercial** | vente, commercial, CRM, prospection |
| **Juridique** | droit, avocat, contrat, contentieux |
| **Comptabilité** | comptable, bilan, fiscalité, audit |
| **Informatique** | développeur, Python, SQL, software |
| **Marketing** | marketing, digital, SEO, campagne |
| **RH** | recrutement, paie, formation, talent |
| **Finance** | finance, trésorerie, budget, analyste |
| **Production** | production, qualité, lean, process |
| **Management** | manager, équipe, leadership, gestion |

## 🚨 Résolution des problèmes

### API non disponible
```bash
# Vérifiez que le service tourne
curl http://localhost:5061/api/v1/health

# Redémarrez si nécessaire
PORT=5061 python app.py
```

### Dossiers non trouvés
- Vérifiez les chemins dans le script
- Assurez-vous que les dossiers contiennent des fichiers `.pdf`

### Erreurs PDF
- Le script utilise automatiquement pdfplumber puis PyPDF2 en fallback
- Les erreurs sont loggées mais n'arrêtent pas le traitement

## 📝 Structure des données

### Format CV détecté
```json
{
    "filename": "cv_candidat.pdf",
    "competences": ["Python", "Marketing", "CRM"],
    "secteur": "informatique",
    "annees_experience": 5,
    "titre_poste": "Développeur Senior"
}
```

### Format Fiche de Poste
```json
{
    "id": "poste_dev",
    "titre": "Développeur Full Stack",
    "competences": ["React", "Node.js", "SQL"],
    "secteur": "informatique",
    "experience": "3-5 ans"
}
```

## 🎯 Cas d'usage

### Validation de l'algorithme
- Tester Enhanced V2.1 sur un gros volume
- Identifier les patterns de réussite/échec
- Valider la cohérence des scores sectoriels

### Analyse de portefeuille
- Évaluer la qualité d'un pool de candidats
- Identifier les secteurs sous-représentés
- Optimiser les stratégies de recrutement

### Benchmark de performance
- Comparer les algorithmes sur données réelles
- Mesurer l'amélioration des versions
- Générer des métriques de référence

## 🔄 Évolutions

Le script est conçu pour être facilement extensible :

- **Nouveaux secteurs** : Ajout dans `secteur_keywords`
- **Patterns d'extraction** : Amélioration des regex
- **Formats de rapport** : Nouvelles visualisations
- **APIs externes** : Intégration d'autres services

## 📞 Support

Pour toute question ou amélioration, consultez :
- Issues GitHub du projet
- Documentation SuperSmartMatch V2.1
- Logs détaillés du script

---

**Développé pour SuperSmartMatch V2.1 Enhanced Algorithm** 🚀
