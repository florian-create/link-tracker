# 📋 Changelog - Feature ICP

## Version 2.0 - Feature ICP (14 novembre 2025)

### ✨ Nouvelles fonctionnalités

#### 🎯 Support ICP (Ideal Customer Profile)

**Qu'est-ce que l'ICP ?**
- Permet de catégoriser vos prospects par profil type (CEO, CTO, Commercial, etc.)
- Analyse la répartition des profils qui cliquent sur vos liens
- Optimisation du ciblage basée sur les performances par ICP

**Fonctionnalités ajoutées :**

1. **Champ ICP dans la base de données**
   - Nouvelle colonne `icp` dans la table `links`
   - Support des valeurs NULL (optionnel)
   - Migration sécurisée sans perte de données

2. **API étendue**
   - Endpoint `/api/create-link` accepte maintenant `ICP` ou `icp`
   - Nouvel endpoint `/api/icp-stats` pour récupérer la distribution des ICPs
   - Filtrage par campagne et période (24h, 7d, 30d, all)

3. **Dashboard amélioré**
   - **Graphique camembert ICP** : Visualisation de la répartition des ICPs qui ont cliqué
     - Position : À droite du graphique Sankey
     - Couleurs : Palette rose → bordeaux (cohérent avec heatmap)
     - Interactif : Affiche nombre et pourcentage au survol
   - **Colonne ICP** ajoutée au tableau des clics
   - **Export CSV** inclut maintenant la colonne ICP

4. **Migration automatique**
   - Script `migrate_add_icp.py` pour ajouter la colonne aux bases existantes
   - Sécurisé : Aucune perte de données
   - Vérification automatique du nombre de lignes

5. **Documentation complète**
   - `ICP_FEATURE.md` : Guide complet avec cas d'usage
   - `ICP_QUICK_START.md` : Activation en 3 étapes
   - Exemples Clay avec formules ICP
   - Troubleshooting et best practices

---

### 🔧 Modifications techniques

#### Backend (`app.py`)

**init_db() :**
```python
# Ajout colonne ICP
icp VARCHAR(255)
```

**create_link() :**
```python
# Support ICP et icp (case insensitive)
icp = data.get('ICP', data.get('icp', ''))

# Insertion avec ICP
INSERT INTO links (..., icp, ...) VALUES (..., %s, ...)
```

**Nouvel endpoint /api/icp-stats :**
```python
@app.route('/api/icp-stats')
def get_icp_stats():
    # Retourne la distribution des ICPs qui ont cliqué
    # Filtrable par range et campaign
```

**get_clicks() modifié :**
```python
# Ajout de l.icp dans le SELECT
# GROUP BY inclut maintenant l.icp
```

#### Frontend (`dashboard_corporate.html`)

**Structure HTML :**
```html
<!-- Nouveau graphique camembert ICP -->
<div class="chart-card">
    <canvas id="icpChart"></canvas>
</div>

<!-- Nouvelle colonne ICP dans le tableau -->
<th>ICP</th>
```

**JavaScript :**
```javascript
// Variable globale
let icpChart = null;

// Nouvelle fonction
async function loadICPStats()

// Nouveau renderer
function renderICPChart(icpData)

// Modification de loadAllData()
loadICPStats() // Ajouté

// Modification de renderClicksTable()
click.icp || 'Non défini' // Affiché

// Modification de exportCSV()
'ICP' header + click.icp data // Exporté
```

---

### 📦 Fichiers ajoutés

1. **migrate_add_icp.py** (105 lignes)
   - Script de migration PostgreSQL
   - Vérification de l'existence de la colonne
   - Comptage avant/après pour sécurité
   - Messages d'information détaillés

2. **ICP_FEATURE.md** (450+ lignes)
   - Documentation complète de la feature
   - Cas d'usage détaillés
   - Exemples Clay avec formules
   - Guide d'analyse des métriques
   - Troubleshooting

3. **ICP_QUICK_START.md** (135 lignes)
   - Guide d'activation rapide (3 étapes)
   - Test rapide avec curl
   - Exemples de valeurs ICP
   - Support et liens

4. **CHANGELOG_ICP.md** (ce fichier)
   - Récapitulatif des changements
   - Notes de migration
   - Breaking changes (aucun)

---

### 📊 Fichiers modifiés

1. **app.py**
   - Ajout colonne `icp` dans `init_db()`
   - Modification `create_link()` pour accepter ICP
   - Modification `get_clicks()` pour retourner ICP
   - Nouvel endpoint `/api/icp-stats`
   - +50 lignes

2. **dashboard_corporate.html**
   - Nouveau graphique camembert ICP (Chart.js)
   - Colonne ICP dans le tableau
   - Fonction `loadICPStats()`
   - Fonction `renderICPChart()`
   - Modification `loadAllData()`, `renderClicksTable()`, `exportCSV()`
   - +120 lignes

3. **README.md**
   - Ajout ICP dans la liste des fonctionnalités
   - +3 lignes

4. **INDEX.md**
   - Ajout liens vers documentation ICP
   - Ajout script de migration
   - +5 lignes

---

### 🔄 Migration

#### Pour bases de données existantes :

```bash
cd /Users/florian/Desktop/link-tracker
python3 migrate_add_icp.py
```

**Impact :**
- ✅ Aucune donnée supprimée
- ✅ Colonne ajoutée avec valeur NULL par défaut
- ✅ Les liens existants fonctionnent normalement
- ✅ Les nouveaux liens peuvent avoir un ICP

#### Après migration :

1. Redéployer sur Render (auto si GitHub connecté)
2. Rafraîchir le dashboard → Camembert ICP apparaît
3. Configurer Clay avec champ ICP
4. Créer des liens avec ICP renseigné

---

### ⚠️ Breaking Changes

**AUCUN** ✅

- Les anciens appels API sans ICP fonctionnent toujours
- Les liens existants sans ICP sont affichés comme "Non défini"
- Rétrocompatibilité totale

---

### 📈 Améliorations de performance

- Index non ajouté sur `icp` (colonne peu utilisée pour les filtres)
- Requête `/api/icp-stats` optimisée avec `INNER JOIN` (uniquement cliqués)
- Utilisation de `COALESCE` et `NULLIF` pour gérer les valeurs vides

---

### 🎨 Design

**Graphique camembert ICP :**
- Palette de couleurs : Rose pâle → Bordeaux foncé
  - `#FAD4C8` (rose très clair)
  - `#F5A48A` (orange clair)
  - `#E35A4A` (rouge orangé)
  - `#CC3A32` (rouge soutenu)
  - `#A41519` (rouge foncé)
  - `#63070A` (bordeaux très foncé)
- Cohérent avec heatmap et top clickers
- Légende en bas avec points circulaires
- Tooltip dark avec pourcentage

**Colonne ICP :**
- Badge gris pour tous les ICPs
- "Non défini" si pas renseigné
- Même style que la colonne Campaign

---

### 🧪 Tests

**Test manuel recommandé :**

```bash
# 1. Créer un lien avec ICP
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "ICP",
    "email": "test@icp.com",
    "ICP": "CEO",
    "campaign": "test",
    "destination_url": "https://google.com"
  }'

# 2. Cliquer sur le lien retourné

# 3. Vérifier /api/icp-stats
curl https://votre-app.onrender.com/api/icp-stats

# Résultat attendu :
# [{"icp":"CEO","click_count":1}]

# 4. Vérifier le dashboard
# → Camembert affiche "CEO: 1 (100%)"
# → Tableau affiche ICP dans la colonne
# → CSV export inclut ICP
```

---

### 📝 Configuration Clay mise à jour

**Ancien body (sans ICP) :**
```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "{{Full URL}}"
}
```

**Nouveau body (avec ICP) :**
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

**Colonne ICP dans Clay :**
- Créer une colonne `ICP`
- Option 1 : Remplir manuellement (CEO, CTO, etc.)
- Option 2 : Formule basée sur `job_title`

**Exemple de formule :**
```javascript
IF(CONTAINS({{job_title}}, "CEO"), "CEO",
IF(CONTAINS({{job_title}}, "CTO"), "CTO",
IF(CONTAINS({{job_title}}, "Commercial"), "Commercial",
"Other")))
```

---

### 🎯 Cas d'usage

1. **Identifier les profils les plus engagés**
   - Regarder le camembert ICP
   - Prioriser les ICPs avec le plus de clics

2. **Comparer les campagnes**
   - Filtrer par aura.camp → Noter top 3 ICPs
   - Filtrer par wesser → Noter top 3 ICPs
   - Adapter le ciblage Clay

3. **Optimiser le ROI**
   - Calculer le taux de clic par ICP
   - Augmenter le volume sur les ICPs performants
   - Réduire les ICPs peu engagés

4. **Segmenter les relances**
   - Exporter CSV avec ICP
   - Messages différents par profil
   - Meilleur taux de conversion

---

### 📞 Support et documentation

**Guides d'activation :**
- [ICP_QUICK_START.md](./ICP_QUICK_START.md) - 3 étapes rapides
- [ICP_FEATURE.md](./ICP_FEATURE.md) - Documentation complète

**API :**
- [API.md](./API.md) - Documentation API (à mettre à jour)

**Migration :**
- `python3 migrate_add_icp.py`

---

### 🚀 Prochaines étapes

1. Lancer la migration
2. Redéployer sur Render
3. Configurer Clay avec ICP
4. Analyser les premiers résultats
5. Optimiser le ciblage

---

### ✅ Checklist de vérification

- [ ] Migration lancée avec succès
- [ ] Render redéployé
- [ ] Dashboard affiche le camembert ICP
- [ ] Colonne ICP visible dans le tableau
- [ ] Clay configuré avec champ ICP
- [ ] Premier lien de test avec ICP créé
- [ ] Clic de test enregistré
- [ ] Camembert affiche le test ICP
- [ ] Export CSV inclut la colonne ICP

---

**Date de release :** 14 novembre 2025
**Version :** 2.0.0
**Type :** Feature majeure (non breaking)
**Commits :** 3 commits (feature + quick start + docs update)
