# 🎯 Configuration Wesser-Recrutement.fr - Link Tracker

Guide complet pour configurer le tracking de liens pour la campagne **wesser-recrutement.fr** en parallèle de **aura.camp**.

## ✅ Prérequis

Votre link-tracker est déjà configuré pour supporter plusieurs campagnes ! Il suffit de :
1. Utiliser le bon nom de campagne dans Clay
2. Filtrer les résultats dans le dashboard

---

## 📋 Configuration Clay pour Wesser

### Étape 1 : Créer une nouvelle table Clay

1. Aller sur [clay.com](https://clay.com)
2. Créer une nouvelle table : **"Wesser - Prospects Recrutement"**
3. Importer vos prospects avec les colonnes :
   - `first_name`
   - `last_name`
   - `email`
   - `job_title` (optionnel)
   - `company` (optionnel)

### Étape 2 : Ajouter l'enrichissement HTTP (Génération du lien)

1. Dans Clay, cliquer sur **"Add Enrichment"** → **"HTTP API"**
2. Configurer comme suit :

**Configuration de la requête :**

```
Method: POST
URL: https://votre-app.onrender.com/api/create-link
Headers:
  Content-Type: application/json
```

**Body (JSON) :**

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
```

**⚠️ IMPORTANT** :
- `campaign`: Doit être **exactement** `"wesser-recrutement.fr"` pour séparer des stats aura.camp
- `destination_url`: Remplacer par votre vraie landing page Wesser

### Étape 3 : Extraire le lien court généré

Dans Clay, après l'enrichissement HTTP :

1. Ajouter une colonne **"Formule"**
2. Utiliser cette formule pour extraire le `short_url` :

```javascript
{{http_enrichment.short_url}}
```

3. Renommer la colonne en : `tracking_link_wesser`

---

## 🎯 Utilisation dans vos campagnes

### Dans LinkedIn (via Unipile ou autre)

Dans votre message personnalisé :

```
Bonjour {{first_name}},

J'ai remarqué votre profil et je pense que vous pourriez être intéressé
par une opportunité chez Wesser.

Découvrez notre offre ici : {{tracking_link_wesser}}

Cordialement,
L'équipe Wesser
```

### Dans vos emails

```html
<a href="{{tracking_link_wesser}}">Découvrir l'opportunité Wesser</a>
```

---

## 📊 Visualiser les statistiques Wesser

### Dashboard Link Tracker

1. Ouvrir : `https://votre-app.onrender.com/`
2. En haut à droite, sélectionner dans le filtre **"Campagne"** :
   - **"All Campaigns"** → Voir aura.camp + wesser-recrutement.fr
   - **"aura.camp"** → Voir uniquement Aura
   - **"wesser-recrutement.fr"** → Voir uniquement Wesser

### Métriques disponibles (par campagne)

- **Total Liens** : Nombre de liens générés pour Wesser
- **Total Clics** : Nombre total d'ouvertures
- **Unique Visitors** : Nombre de personnes ayant cliqué au moins une fois
- **Click Rate** : Taux d'ouverture (%)

### Tableau détaillé

Le tableau affiche pour chaque prospect :
- Nom complet
- Email
- Campagne (badge bleu : "wesser-recrutement.fr")
- Nombre de clics
- Date du premier clic
- Date du dernier clic
- Statut (Clicked / Not clicked)

---

## 🧪 Test de la configuration

### Test 1 : Créer un lien de test pour Wesser

```bash
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Wesser",
    "email": "test@wesser.fr",
    "campaign": "wesser-recrutement.fr",
    "destination_url": "https://wesser-recrutement.fr"
  }'
```

**Réponse attendue :**

```json
{
  "success": true,
  "short_url": "https://votre-app.onrender.com/c/AbC123",
  "link_id": "AbC123"
}
```

### Test 2 : Cliquer sur le lien

1. Copier le `short_url` reçu
2. Ouvrir dans un navigateur
3. Vérifier que vous êtes redirigé vers wesser-recrutement.fr

### Test 3 : Vérifier dans le dashboard

1. Ouvrir `https://votre-app.onrender.com/`
2. Sélectionner **"wesser-recrutement.fr"** dans le filtre
3. Vérifier que le test "Test Wesser" apparaît avec 1 clic

---

## 📈 Exemple de résultats

### Dashboard avec filtre Wesser

```
📊 Statistiques (wesser-recrutement.fr uniquement)
├─ Total Liens : 324
├─ Total Clics : 187
├─ Unique Visitors : 142
└─ Click Rate : 43.8%

📋 Top Clickers
├─ 1. Jean Dupont - 5 clics
├─ 2. Marie Martin - 3 clics
└─ 3. Pierre Durand - 2 clics
```

---

## 🔄 Workflow complet

### Pour chaque nouvelle campagne Wesser

1. **Clay** : Importer prospects → Enrichir avec HTTP API → Récupérer `short_url`
2. **Outreach** : Envoyer messages LinkedIn/Email avec liens personnalisés
3. **Dashboard** : Filtrer par "wesser-recrutement.fr"
4. **Export CSV** : Télécharger les résultats pour analyse
5. **Relance** : Identifier les non-cliqueurs, relancer avec nouvelle approche

---

## 🎨 Personnalisation avancée (optionnel)

### Utiliser plusieurs landing pages Wesser

Vous pouvez créer plusieurs campagnes pour différentes offres Wesser :

```json
{
  "campaign": "wesser-recrutement-commercial",
  "destination_url": "https://wesser-recrutement.fr/commercial"
}
```

```json
{
  "campaign": "wesser-recrutement-manager",
  "destination_url": "https://wesser-recrutement.fr/manager"
}
```

Le dashboard affichera alors 3 campagnes :
- aura.camp
- wesser-recrutement-commercial
- wesser-recrutement-manager

---

## 🚨 Troubleshooting

### Problème : Liens non créés dans Clay

**Cause** : URL de l'API incorrecte

**Solution** :
1. Vérifier que votre app Render est bien déployée
2. Tester l'URL avec curl (voir Test 1)
3. Vérifier que l'URL dans Clay est exacte (pas de trailing slash)

### Problème : Campagne Wesser n'apparaît pas dans le filtre

**Cause** : Aucun lien créé avec `campaign: "wesser-recrutement.fr"`

**Solution** :
1. Créer au moins 1 lien avec la campagne Wesser
2. Rafraîchir le dashboard (F5)
3. Le filtre se remplira automatiquement

### Problème : Les stats sont mélangées aura + wesser

**Cause** : Filtre "All Campaigns" sélectionné

**Solution** :
1. Cliquer sur le dropdown "All Campaigns"
2. Sélectionner "wesser-recrutement.fr"
3. Les stats se mettront à jour automatiquement

---

## 📊 Export des données Wesser

### Export CSV filtré

1. Dans le dashboard, filtrer par "wesser-recrutement.fr"
2. Cliquer sur **"EXPORT CSV"**
3. Le fichier contiendra uniquement les prospects Wesser

**Colonnes du CSV :**
```csv
First Name,Last Name,Email,Campaign,Clicks,First Click,Last Click,Status
Jean,Dupont,jean@example.com,wesser-recrutement.fr,3,11/14/2025 10:30,11/14/2025 14:20,Clicked
```

---

## 🎯 Objectifs de tracking

### KPIs à suivre pour Wesser

- **Click Rate** : Objectif > 30%
- **Unique Visitors** : Mesurer l'engagement réel
- **Time to Click** : Analyser le premier clic (rapidité d'intérêt)
- **Multiple Clicks** : Identifier les prospects très intéressés (2+ clics)

### Segments d'analyse

1. **Hot prospects** : 2+ clics → Relance prioritaire
2. **Warm prospects** : 1 clic → Nurturer avec contenu
3. **Cold prospects** : 0 clics → Revoir le messaging ou abandonner

---

## ✅ Checklist de démarrage Wesser

- [ ] Link tracker déployé sur Render
- [ ] Table Clay créée avec prospects Wesser
- [ ] Enrichissement HTTP configuré avec `campaign: "wesser-recrutement.fr"`
- [ ] Test de création de lien réussi
- [ ] Test de clic et redirection réussi
- [ ] Dashboard affiche correctement la campagne Wesser
- [ ] Premier batch de messages envoyé avec liens trackés
- [ ] Suivi quotidien des stats dans le dashboard

---

## 📞 Support

En cas de problème :
1. Vérifier les logs Render : Dashboard Render → Logs
2. Tester l'API avec curl (voir section Tests)
3. Vérifier la configuration Clay (body JSON exact)

---

**🚀 Vous êtes prêt à tracker vos campagnes Wesser !**

Commencez par créer votre première table Clay et configurer l'enrichissement HTTP.
