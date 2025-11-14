# 🎯 Feature ICP - Ideal Customer Profile

Guide complet pour utiliser le champ ICP (Ideal Customer Profile) et analyser la répartition de vos prospects par profil.

---

## 📊 Vue d'ensemble

Le champ ICP vous permet de :
- Catégoriser vos prospects par profil type (CEO, CTO, Sales Director, etc.)
- Voir dans le dashboard quels ICPs cliquent le plus
- Analyser la performance par type de profil
- Exporter les données avec l'ICP pour analyse

---

## 🚀 Migration (si base existante)

Si vous avez déjà des données dans votre link tracker, lancez la migration :

```bash
cd /Users/florian/Desktop/link-tracker
python3 migrate_add_icp.py
```

**Sécurité :**
- ✅ Aucune donnée n'est supprimée
- ✅ Toutes les données existantes sont conservées
- ✅ La colonne ICP accepte les valeurs NULL (optionnel)

---

## 🎨 Configuration Clay

### Pour Wesser avec ICP

**Body JSON complet :**

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "ICP": "{{ICP}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "{{Full URL}}"
}
```

### Exemples de valeurs ICP

Adaptez selon votre segmentation :

**B2B SaaS :**
- `CEO`
- `CTO`
- `VP Sales`
- `Head of Marketing`
- `Product Manager`

**Recrutement (Wesser) :**
- `Commercial Senior`
- `Manager Commercial`
- `Directeur Regional`
- `Chef d'Équipe`
- `Responsable Développement`

**E-commerce :**
- `E-commerce Director`
- `CMO`
- `Growth Manager`
- `Performance Marketing Lead`

**Industrie :**
- `Directeur Général`
- `Directeur Technique`
- `Responsable Production`
- `Directeur Qualité`

---

## 📊 Visualisation Dashboard

### Graphique Camembert ICP

**Position :** À droite du graphique Sankey (Conversion Funnel)

**Données affichées :** Répartition des ICPs **qui ont cliqué uniquement**

**Filtres applicables :**
- Par période (24h, 7d, 30d, All)
- Par campagne (aura.camp, wesser-recrutement.fr, etc.)

**Exemple de visualisation :**
```
CEO: 45 clics (35%)
CTO: 30 clics (23%)
VP Sales: 28 clics (22%)
Head of Marketing: 25 clics (20%)
```

**Couleurs :** Palette Rose → Bordeaux (cohérente avec heatmap et top clickers)

---

## 📋 Tableau Dashboard

### Colonne ICP ajoutée

Le tableau affiche maintenant :

| Name | Email | **ICP** | Campaign | Clicks | First Click | Last Click | Status | Actions |
|------|-------|---------|----------|--------|-------------|------------|--------|---------|
| John Doe | john@co.com | **CEO** | wesser | 3 | 11/14 10:30 | 11/14 14:20 | Clicked | Delete |
| Jane Smith | jane@co.com | **CTO** | aura | 1 | 11/14 15:45 | 11/14 15:45 | Clicked | Delete |

---

## 📥 Export CSV

Le CSV exporté inclut désormais la colonne ICP :

```csv
First Name,Last Name,Email,ICP,Campaign,Clicks,First Click,Last Click,Status
John,Doe,john@company.com,CEO,wesser-recrutement.fr,3,11/14/2025 10:30,11/14/2025 14:20,Clicked
Jane,Smith,jane@startup.io,CTO,aura.camp,1,11/14/2025 15:45,11/14/2025 15:45,Clicked
```

---

## 🔌 API

### Endpoint : `/api/icp-stats`

Récupère la répartition des ICPs qui ont cliqué.

**Paramètres :**
- `range` (optional) : `24h`, `7d`, `30d`, `all` (default: `all`)
- `campaign` (optional) : Filtrer par campagne

**Exemples :**

```bash
# Tous les ICPs (toutes périodes, toutes campagnes)
GET /api/icp-stats

# ICPs des 7 derniers jours
GET /api/icp-stats?range=7d

# ICPs pour la campagne Wesser uniquement
GET /api/icp-stats?campaign=wesser-recrutement.fr

# ICPs Wesser des 30 derniers jours
GET /api/icp-stats?range=30d&campaign=wesser-recrutement.fr
```

**Réponse :**

```json
[
  {
    "icp": "CEO",
    "click_count": 45
  },
  {
    "icp": "CTO",
    "click_count": 30
  },
  {
    "icp": "VP Sales",
    "click_count": 28
  },
  {
    "icp": "Non défini",
    "click_count": 5
  }
]
```

**Note :** Les liens sans ICP sont regroupés sous `"Non défini"`

---

## 💡 Cas d'usage

### 1. Identifier les ICPs les plus engagés

**Objectif :** Savoir quels profils cliquent le plus

**Action :**
1. Ouvrir le dashboard
2. Regarder le camembert ICP
3. Identifier les 3 ICPs avec le plus de clics
4. Adapter votre messaging pour ces profils

**Exemple :**
Si "Commercial Senior" représente 40% des clics, concentrez vos efforts sur ce profil.

---

### 2. Comparer les ICPs entre campagnes

**Objectif :** Voir si aura.camp et wesser.fr attirent les mêmes profils

**Action :**
1. Filtrer par "aura.camp" → Noter les top 3 ICPs
2. Filtrer par "wesser-recrutement.fr" → Noter les top 3 ICPs
3. Comparer les résultats

**Exemple :**
```
Aura.camp : CEO (50%), CTO (30%), CMO (20%)
Wesser    : Manager (45%), Directeur (35%), Chef d'équipe (20%)
```

---

### 3. Optimiser le ciblage Clay

**Objectif :** Enrichir plus de prospects du bon ICP

**Action :**
1. Identifier les ICPs avec le meilleur taux de clic
2. Dans Clay, augmenter le volume de prospects avec ces ICPs
3. Réduire les ICPs moins performants

**Exemple :**
Si "CEO" a un taux de clic de 60% vs "Manager" à 15%, priorisez les CEOs.

---

### 4. Segmentation des relances

**Objectif :** Relancer différemment selon l'ICP

**Action :**
1. Exporter le CSV avec filtre par campagne
2. Trier par ICP dans Excel/Google Sheets
3. Créer des messages de relance adaptés par ICP

**Exemple :**
- CEO : Focus ROI et vision stratégique
- CTO : Focus tech et intégration
- VP Sales : Focus performance et résultats

---

## 🧪 Exemple Clay complet

### Table Wesser avec ICP

**Colonnes Clay nécessaires :**

| Colonne Clay | Type | Source |
|--------------|------|--------|
| `first_name` | Texte | LinkedIn/Import |
| `last_name` | Texte | LinkedIn/Import |
| `email` | Texte | Email enrichment |
| `ICP` | Texte | **Formule ou colonne manuelle** |
| `Full URL` | Texte | URL de destination |

**Exemple de formule ICP dans Clay :**

```javascript
IF(
  CONTAINS({{job_title}}, "CEO") OR CONTAINS({{job_title}}, "Directeur Général"),
  "CEO",
  IF(
    CONTAINS({{job_title}}, "CTO") OR CONTAINS({{job_title}}, "Directeur Technique"),
    "CTO",
    IF(
      CONTAINS({{job_title}}, "Sales") OR CONTAINS({{job_title}}, "Commercial"),
      "Sales Director",
      "Other"
    )
  )
)
```

**Configuration HTTP API :**

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "ICP": "{{ICP}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "{{Full URL}}"
}
```

---

## 📈 Métriques à suivre

### Par ICP

Pour chaque profil ICP, suivez :

1. **Click Rate** : `(Clics / Liens envoyés) * 100`
2. **Engagement** : Nombre moyen de clics par personne
3. **Time to Click** : Délai moyen avant le premier clic
4. **Conversion** : Si intégré CRM, taux de conversion en opportunité

**Exemple d'analyse :**

| ICP | Liens envoyés | Clics uniques | Click Rate | Avg Clicks/Person |
|-----|---------------|---------------|------------|-------------------|
| CEO | 100 | 45 | 45% | 2.1 |
| CTO | 80 | 30 | 37.5% | 1.8 |
| VP Sales | 70 | 28 | 40% | 2.5 |

**Insights :**
- CEO : Meilleur click rate → Prioriser
- VP Sales : Meilleur engagement (2.5 clics/personne) → Très intéressés
- CTO : À améliorer → Revoir le messaging

---

## 🚨 Troubleshooting

### ICP n'apparaît pas dans le dashboard

**Cause :** Champ ICP non renseigné lors de la création du lien

**Solution :**
1. Vérifier que le body Clay contient `"ICP": "{{ICP}}"`
2. Vérifier que la colonne `{{ICP}}` existe et est remplie dans Clay
3. Créer un lien de test avec ICP renseigné

### Graphique ICP vide

**Cause :** Aucun lien avec ICP n'a été cliqué

**Solution :**
1. Vérifier que des liens avec ICP ont été créés
2. Cliquer sur un lien de test pour vérifier
3. Attendre que des prospects cliquent

### ICP affiché comme "Non défini"

**Cause :** Champ ICP vide ou non fourni lors de la création

**Solution :**
- C'est normal pour les liens créés sans ICP
- Pour les nouveaux liens, renseigner le champ ICP dans Clay
- Les anciens liens sans ICP resteront "Non défini"

---

## ✅ Checklist de démarrage

- [ ] Migration exécutée (si base existante)
- [ ] Colonne ICP créée dans Clay
- [ ] Formule ICP configurée (ou valeurs manuelles)
- [ ] HTTP API updated with `"ICP": "{{ICP}}"`
- [ ] Test de création de lien avec ICP
- [ ] Vérification : ICP apparaît dans le tableau dashboard
- [ ] Test de clic : ICP apparaît dans le camembert
- [ ] Export CSV : ICP présent dans les colonnes

---

## 📞 Support

**Fichiers modifiés pour cette feature :**
- `app.py` : Ajout colonne ICP, endpoint `/api/icp-stats`
- `dashboard_corporate.html` : Graphique camembert + colonne tableau
- `migrate_add_icp.py` : Script de migration

**Documentation :**
- Ce fichier (`ICP_FEATURE.md`)
- Guide Clay mis à jour dans `CLAY_WESSER_CONFIG.md`

---

**🎉 Vous êtes prêt à analyser vos ICPs !**

Commencez par :
1. Lancer la migration
2. Ajouter le champ ICP dans Clay
3. Créer quelques liens de test
4. Visualiser les résultats dans le dashboard

---

**Dernière mise à jour :** 14 novembre 2025
**Version :** 1.0 - Feature ICP
