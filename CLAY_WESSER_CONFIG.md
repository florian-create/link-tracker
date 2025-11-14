# 🎨 Configuration Clay pour Wesser - Guide Visuel

Guide pas à pas pour configurer l'enrichissement HTTP dans Clay pour générer des liens trackés pour **wesser-recrutement.fr**.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

✅ Votre link-tracker déployé sur Render
✅ L'URL de votre app (format : `https://link-tracker-xxxx.onrender.com`)
✅ Un compte Clay actif
✅ Une liste de prospects à contacter pour Wesser

---

## 🚀 Étape par Étape

### Étape 1 : Créer une nouvelle table Clay

1. Aller sur [clay.com](https://clay.com)
2. Cliquer sur **"+ New Table"**
3. Nommer la table : **"Wesser - Prospects Recrutement"**
4. Cliquer sur **"Create"**

---

### Étape 2 : Importer vos prospects

Vous avez plusieurs options :

**Option A : Import CSV**
- Préparer un CSV avec les colonnes : `first_name`, `last_name`, `email`, `job_title`, `company`
- Cliquer sur **"Import"** → **"CSV"**
- Mapper les colonnes

**Option B : Recherche LinkedIn**
- Utiliser l'enrichissement **"Find People"**
- Filtrer par critères (titre, localisation, etc.)

**Option C : Import depuis liste**
- Copier-coller une liste de LinkedIn URLs
- Clay va enrichir automatiquement

---

### Étape 3 : Ajouter l'enrichissement HTTP API

1. Dans votre table Clay, cliquer sur **"Add Enrichment"** (en haut à droite)
2. Dans la barre de recherche, taper **"HTTP API"**
3. Sélectionner **"HTTP API"**
4. Cliquer sur **"Use Enrichment"**

---

### Étape 4 : Configurer la requête HTTP

Voici la configuration exacte à entrer :

#### 📍 Section "Request" (Requête)

**Method (Méthode):**
```
POST
```

**URL:**
```
https://VOTRE-APP.onrender.com/api/create-link
```

⚠️ **IMPORTANT** : Remplacer `VOTRE-APP` par le nom exact de votre app Render.

**Exemple :**
```
https://link-tracker-abc123.onrender.com/api/create-link
```

Pour trouver votre URL Render :
1. Aller sur [dashboard.render.com](https://dashboard.render.com)
2. Cliquer sur votre service "link-tracker"
3. Copier l'URL en haut (format : `https://xxx.onrender.com`)

---

#### 📍 Section "Headers" (En-têtes)

Cliquer sur **"+ Add Header"** et ajouter :

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |

---

#### 📍 Section "Body" (Corps de la requête)

**Type de body :** Sélectionner **"raw"** et **"JSON"**

**Contenu du body :**

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
```

#### 🔧 Explication des champs :

| Champ | Description | À modifier ? |
|-------|-------------|--------------|
| `{{first_name}}` | Prénom du prospect (automatique depuis Clay) | ✅ Remplacer par le nom de votre colonne Clay si différent |
| `{{last_name}}` | Nom du prospect (automatique depuis Clay) | ✅ Remplacer par le nom de votre colonne Clay si différent |
| `{{email}}` | Email du prospect (automatique depuis Clay) | ✅ Remplacer par le nom de votre colonne Clay si différent |
| `campaign` | Nom de la campagne (fixe) | ⛔ **NE PAS MODIFIER** - doit rester `"wesser-recrutement.fr"` |
| `destination_url` | Page de destination après clic | ✅ Remplacer par votre vraie landing page Wesser |

#### 📝 Exemples de `destination_url` :

```json
"destination_url": "https://wesser-recrutement.fr/rejoindre"
"destination_url": "https://wesser-recrutement.fr/offres/commercial"
"destination_url": "https://wesser-recrutement.fr/candidature?ref=linkedin"
```

---

#### 📍 Section "Mapping Colonnes Clay"

Si vos colonnes Clay ont des noms différents, adaptez les `{{ }}` :

**Exemples de mapping :**

| Nom colonne Clay | À utiliser dans le body |
|------------------|------------------------|
| `First Name` | `{{First Name}}` |
| `Last Name` | `{{Last Name}}` |
| `Email Address` | `{{Email Address}}` |
| `/in/linkedin-profile` | `{{/in/linkedin-profile}}` |

**Body adapté si colonnes différentes :**
```json
{
  "first_name": "{{First Name}}",
  "last_name": "{{Last Name}}",
  "email": "{{Email Address}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
```

---

### Étape 5 : Tester la configuration

1. Cliquer sur **"Test"** en bas de la configuration
2. Clay va faire un appel de test
3. Vous devriez voir une réponse comme :

```json
{
  "success": true,
  "short_url": "https://link-tracker-abc123.onrender.com/c/AbC123Xy",
  "link_id": "AbC123Xy"
}
```

✅ **Si vous voyez ça = Configuration réussie !**

❌ **Si erreur :**
- Vérifier que l'URL Render est correcte
- Vérifier que le body JSON est valide (pas de virgule en trop)
- Vérifier que les noms de colonnes `{{ }}` correspondent à Clay

---

### Étape 6 : Extraire le lien généré

Une fois le test réussi :

1. Clay va créer une nouvelle colonne avec le résultat de l'API
2. Renommer cette colonne en : **"HTTP API Response"** (ou laisser le nom par défaut)

Pour extraire juste le lien court :

1. Cliquer sur **"+ Add Column"** → **"Formula"**
2. Entrer cette formule :

```javascript
{{HTTP API Response.short_url}}
```

3. Renommer la colonne en : **"Wesser Tracking Link"**

---

### Étape 7 : Utiliser le lien dans vos messages

Le lien est maintenant disponible dans la colonne **"Wesser Tracking Link"**.

#### Exemple dans un message LinkedIn :

```
Bonjour {{first_name}},

J'ai vu votre profil et je pense que vous pourriez être intéressé(e)
par une opportunité chez Wesser.

Découvrez notre proposition ici : {{Wesser Tracking Link}}

Au plaisir d'échanger,
L'équipe Wesser
```

#### Exemple dans un email :

```html
<p>Bonjour {{first_name}},</p>

<p>Nous recherchons des talents comme vous pour rejoindre Wesser.</p>

<p><a href="{{Wesser Tracking Link}}">Cliquez ici pour en savoir plus</a></p>

<p>Cordialement,<br>
L'équipe Wesser</p>
```

---

## 🧪 Vérification complète

### Test 1 : Vérifier qu'un lien a été créé

1. Dans Clay, sélectionner une ligne de prospect
2. Vérifier que la colonne "Wesser Tracking Link" contient une URL
3. Format attendu : `https://votre-app.onrender.com/c/XXXXXXXX`

### Test 2 : Tester le clic

1. Copier un lien depuis Clay
2. Ouvrir dans un nouvel onglet
3. Vérifier que vous êtes redirigé vers votre landing page Wesser

### Test 3 : Vérifier dans le dashboard

1. Ouvrir `https://votre-app.onrender.com/`
2. Dans le filtre "Campagne", sélectionner **"wesser-recrutement.fr"**
3. Vérifier que votre test apparaît dans le tableau
4. Vérifier que le clic est comptabilisé

---

## 📊 Configuration Clay complète - Récapitulatif

### Configuration HTTP API finale :

```
Method: POST
URL: https://VOTRE-APP.onrender.com/api/create-link

Headers:
  Content-Type: application/json

Body (JSON):
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
```

### Colonnes Clay après configuration :

| Colonne | Type | Contenu |
|---------|------|---------|
| `first_name` | Import | Prénom du prospect |
| `last_name` | Import | Nom du prospect |
| `email` | Import/Enrichissement | Email du prospect |
| `HTTP API Response` | Enrichissement | Réponse complète de l'API |
| `Wesser Tracking Link` | Formule | Le lien court extrait |

---

## 🎯 Cas d'usage avancés

### Cas 1 : Plusieurs landing pages Wesser

Si vous avez différentes offres :

**Commercial :**
```json
{
  "campaign": "wesser-commercial",
  "destination_url": "https://wesser-recrutement.fr/commercial"
}
```

**Manager :**
```json
{
  "campaign": "wesser-manager",
  "destination_url": "https://wesser-recrutement.fr/manager"
}
```

Créez des enrichissements HTTP séparés pour chaque offre.

### Cas 2 : Liens avec paramètres UTM

Pour tracker la source du clic :

```json
{
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre?utm_source=linkedin&utm_medium=outreach&utm_campaign=q1-2025"
}
```

### Cas 3 : Destination dynamique par profil

Utiliser une colonne Clay pour déterminer la destination :

```json
{
  "campaign": "wesser-recrutement.fr",
  "destination_url": "{{landing_page_url}}"
}
```

Puis créer une colonne `landing_page_url` avec une formule :
```javascript
IF({{job_title}} CONTAINS "commercial",
   "https://wesser-recrutement.fr/commercial",
   "https://wesser-recrutement.fr/rejoindre"
)
```

---

## 🚨 Troubleshooting

### Erreur : "Failed to fetch"

**Cause :** L'app Render est en "sleep" (inactivité 15 min)

**Solution :**
1. Ouvrir `https://votre-app.onrender.com/` dans un navigateur
2. Attendre 30 secondes que l'app se réveille
3. Retester dans Clay

### Erreur : "400 Bad Request"

**Cause :** Body JSON mal formaté

**Solution :**
1. Vérifier qu'il n'y a pas de virgule en trop dans le JSON
2. Vérifier que les `{{ }}` correspondent aux colonnes Clay
3. Copier-coller exactement le body de ce guide

### Erreur : "404 Not Found"

**Cause :** URL incorrecte

**Solution :**
1. Vérifier l'URL : doit finir par `/api/create-link`
2. Vérifier que l'app Render est bien déployée
3. Tester l'URL dans un navigateur (vous devriez avoir une erreur 405, c'est normal)

### Pas de réponse / Timeout

**Cause :** App Render éteinte ou problème de connexion

**Solution :**
1. Vérifier les logs Render : [dashboard.render.com](https://dashboard.render.com)
2. Vérifier que la base de données PostgreSQL est active
3. Redéployer si nécessaire

---

## ✅ Checklist finale

Avant de lancer votre campagne Wesser :

- [ ] HTTP API configuré dans Clay avec `campaign: "wesser-recrutement.fr"`
- [ ] Test réussi avec un prospect
- [ ] Lien extrait dans colonne "Wesser Tracking Link"
- [ ] Clic sur le lien redirige vers la bonne landing page
- [ ] Dashboard affiche le prospect dans la campagne "wesser-recrutement.fr"
- [ ] Message LinkedIn/Email prêt avec le lien `{{Wesser Tracking Link}}`
- [ ] First batch de 5-10 prospects testé avant envoi massif

---

## 🎉 Vous êtes prêt !

Vous pouvez maintenant :

1. ✅ Générer des liens trackés pour chaque prospect Wesser
2. ✅ Envoyer vos messages avec liens personnalisés
3. ✅ Suivre qui clique en temps réel dans le dashboard
4. ✅ Séparer les stats Wesser des stats Aura
5. ✅ Exporter les données en CSV par campagne

**Prochaines étapes :**
- Lancer votre première campagne Wesser
- Consulter le dashboard quotidiennement
- Relancer les prospects qui ont cliqué (hot leads)
- Analyser le taux d'ouverture et optimiser votre message

---

**Besoin d'aide ?** Consultez [WESSER_SETUP.md](./WESSER_SETUP.md) pour plus de détails.
