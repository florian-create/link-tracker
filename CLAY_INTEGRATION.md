# 🎨 Guide d'intégration Clay

## Vue d'ensemble

Ce guide vous montre comment intégrer le link tracker avec Clay pour générer automatiquement des liens trackés personnalisés pour chaque personne de votre campagne.

## Prérequis

- Avoir déployé l'application sur Render (voir `DEPLOYMENT.md`)
- Avoir une table Clay avec vos prospects
- L'URL de votre application Render (ex: `https://link-tracker-xxxx.onrender.com`)

## Étape 1 : Préparer votre table Clay

Votre table Clay doit contenir au minimum:

| Colonne | Type | Description |
|---------|------|-------------|
| `first_name` | Texte | Prénom du prospect |
| `last_name` | Texte | Nom du prospect |
| `email` | Email | Email du prospect |
| `destination_url` | URL | Vers où le lien doit rediriger |

Colonnes optionnelles:
- `campaign` : Nom de la campagne (ex: "outbound-q1-2024")
- `company` : Nom de l'entreprise
- Toute autre donnée que vous voulez tracker

## Étape 2 : Ajouter l'enrichissement HTTP dans Clay

### 2.1 Créer une nouvelle colonne

1. Dans votre table Clay, cliquer sur "+ Add enrichment"
2. Chercher "HTTP API" ou "Webhook"
3. Sélectionner "HTTP API"

### 2.2 Configurer la requête HTTP

**Configuration de base:**

- **URL**: `https://VOTRE-APP.onrender.com/api/create-link`
- **Method**: `POST`
- **Headers**:
  ```
  Content-Type: application/json
  ```

**Body (JSON):**

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "{{campaign}}",
  "destination_url": "{{destination_url}}"
}
```

### 2.3 Mapper les champs Clay

Dans Clay, utiliser les variables dynamiques pour mapper vos colonnes:

| Variable JSON | Colonne Clay |
|---------------|--------------|
| `{{first_name}}` | Prénom ou First Name |
| `{{last_name}}` | Nom ou Last Name |
| `{{email}}` | Email |
| `{{campaign}}` | Campaign (ou mettre une valeur fixe) |
| `{{destination_url}}` | URL de destination |

**Exemple concret:**

Si vous voulez que tous vos prospects aillent vers votre landing page:

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "outbound-janvier-2025",
  "destination_url": "https://votresite.com/landing-page"
}
```

### 2.4 Extraire l'URL courte

L'API retourne une réponse JSON:

```json
{
  "success": true,
  "short_url": "https://link-tracker-xxxx.onrender.com/c/AbC123",
  "link_id": "AbC123"
}
```

Dans Clay:
1. Après avoir configuré la requête HTTP
2. Aller dans "Output Settings"
3. Sélectionner le champ à extraire: `short_url`
4. Nommer la colonne: "Lien tracké" ou "Tracked Link"

## Étape 3 : Utiliser le lien dans vos messages

Une fois le lien généré, vous pouvez l'utiliser dans:

### LinkedIn (via Unipile ou autre)

```
Salut {{first_name}},

J'ai vu ton profil et je pense que [notre solution] pourrait t'intéresser.

J'ai préparé quelque chose pour toi : {{tracked_link}}

Dis-moi ce que tu en penses !
```

### Email

```
Bonjour {{first_name}},

Je t'envoie ce lien personnalisé : {{tracked_link}}

Belle journée,
```

### SMS / WhatsApp

```
Bonjour {{first_name}}, voici le lien dont je te parlais : {{tracked_link}}
```

## Étape 4 : Exemples de cas d'usage

### Cas 1 : Landing page personnalisée

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "demo-request",
  "destination_url": "https://calendly.com/votrecompte/demo"
}
```

### Cas 2 : Article de blog

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "content-marketing-q1",
  "destination_url": "https://votreblog.com/article-xyz"
}
```

### Cas 3 : Offre spéciale

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "promo-janvier",
  "destination_url": "https://votresite.com/promo?code=JAN2025"
}
```

### Cas 4 : Lien LinkedIn personnalisé

```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "linkedin-outreach",
  "destination_url": "https://linkedin.com/in/votre-profil"
}
```

## Étape 5 : Workflow complet dans Clay

Voici un exemple de workflow typique:

```
[Table Clay avec prospects]
    ↓
[Enrichissement 1: Trouver email]
    ↓
[Enrichissement 2: Générer lien tracké] ← HTTP API
    ↓
[Enrichissement 3: Envoyer message LinkedIn/Email]
    ↓
[Vérifier dashboard pour voir qui a cliqué]
```

## 📊 Consulter les résultats

Une fois vos liens envoyés:

1. **Dashboard en temps réel**
   - Aller sur: `https://votre-app.onrender.com/`
   - Voir les statistiques globales
   - Voir qui a cliqué et quand

2. **Export CSV**
   - Sur le dashboard, cliquer sur "Export CSV"
   - Obtenir toutes les données (nom, email, clics, dates)

3. **API pour automatisation**
   ```bash
   # Récupérer toutes les données
   curl https://votre-app.onrender.com/api/clicks

   # Filtrer par campagne
   curl https://votre-app.onrender.com/api/clicks?campaign=outbound-janvier
   ```

## 🎯 Bonnes pratiques

### 1. Nommage des campagnes
Utilisez des noms explicites:
- ✅ `linkedin-outbound-q1-2025`
- ✅ `email-cold-saas-founders`
- ❌ `campagne1`
- ❌ `test`

### 2. Segmentation
Créez différentes campagnes pour:
- Canaux différents (LinkedIn, Email, SMS)
- Audiences différentes (Founders, Sales, Marketing)
- Périodes différentes (Q1, Q2...)

### 3. A/B Testing
Créez 2 campagnes avec 2 destinations différentes:
```
campagne-variant-a → landing-page-v1
campagne-variant-b → landing-page-v2
```

### 4. Suivi dans Clay
Ajoutez une colonne "A cliqué" qui check via l'API si la personne a cliqué:
- Vous pouvez créer un enrichissement qui appelle `/api/clicks`
- Filtrer les résultats pour voir qui a engagé
- Déclencher des actions de suivi automatiques

## 🔧 Troubleshooting

**Le lien ne se génère pas dans Clay**
- Vérifier que l'URL de l'API est correcte
- Vérifier que le format JSON est valide
- Regarder les logs d'erreur dans Clay

**Le lien redirige vers 404**
- Vérifier que l'app Render est bien déployée
- Vérifier que la base de données est connectée
- Tester manuellement avec curl

**Les statistiques ne s'affichent pas**
- Vérifier que quelqu'un a bien cliqué sur les liens
- Rafraîchir le dashboard (auto-refresh toutes les 30s)
- Regarder les logs Render

## 📞 Support

Si vous avez des questions:
1. Vérifier les logs Render: `Dashboard → Service → Logs`
2. Tester l'API manuellement avec curl ou Postman
3. Vérifier la console développeur du navigateur (F12)

## 🎉 Exemple complet

Voici à quoi ressemble une configuration complète dans Clay:

**Table Clay:**
| Prénom | Nom | Email | Campaign | URL Destination | Lien Tracké (généré) |
|--------|-----|-------|----------|-----------------|----------------------|
| John | Doe | john@company.com | outbound-q1 | https://monsite.com/demo | https://app.onrender.com/c/Xy7z2 |
| Jane | Smith | jane@startup.io | outbound-q1 | https://monsite.com/demo | https://app.onrender.com/c/Bk3m9 |

**Message envoyé:**
```
Salut John,

J'ai vu que tu es [titre] chez [company].

Je pense que notre solution pourrait t'intéresser, j'ai préparé une démo personnalisée pour toi :

https://app.onrender.com/c/Xy7z2

Qu'en penses-tu ?
```

**Résultat dans le dashboard:**
```
John Doe | john@company.com | 2 clics | Premier: 10/01 14:32 | Dernier: 11/01 09:15 | ✅ Cliqué
Jane Smith | jane@startup.io | 0 clic | - | - | ⚪ Non cliqué
```

🚀 Vous êtes maintenant prêt à tracker vos campagnes !
