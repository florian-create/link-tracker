# 📡 Documentation API - Link Tracker

API REST complète pour créer et tracker des liens personnalisés.

## Base URL

```
https://votre-app.onrender.com
```

## Endpoints

### 1. Créer un lien tracké

Crée un nouveau lien court personnalisé et retourne l'URL.

**Endpoint:**
```
POST /api/create-link
```

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "campaign": "outbound-q1-2025",
  "destination_url": "https://example.com/landing-page"
}
```

**Paramètres:**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `first_name` | string | Non | Prénom de la personne |
| `last_name` | string | Non | Nom de la personne |
| `email` | string | Non | Email de la personne |
| `campaign` | string | Non | Nom de la campagne (défaut: "default") |
| `destination_url` | string | **Oui** | URL de destination pour la redirection |

**Réponse (201 Created):**
```json
{
  "success": true,
  "short_url": "https://votre-app.onrender.com/c/AbC123Xy",
  "link_id": "AbC123Xy"
}
```

**Erreur (400 Bad Request):**
```json
{
  "error": "destination_url is required"
}
```

**Exemple cURL:**
```bash
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "campaign": "test-campaign",
    "destination_url": "https://google.com"
  }'
```

**Exemple Python:**
```python
import requests

response = requests.post(
    'https://votre-app.onrender.com/api/create-link',
    json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'campaign': 'test-campaign',
        'destination_url': 'https://google.com'
    }
)

data = response.json()
print(data['short_url'])  # https://votre-app.onrender.com/c/AbC123Xy
```

---

### 2. Rediriger et tracker

Redirige vers l'URL de destination et enregistre le clic avec toutes les métadonnées.

**Endpoint:**
```
GET /c/{link_id}
```

**Paramètres:**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `link_id` | string | ID unique du lien (généré automatiquement) |

**Comportement:**
1. Recherche le lien dans la base de données
2. Enregistre le clic avec :
   - IP address
   - User agent (navigateur, appareil)
   - Timestamp
   - Referer (d'où vient le visiteur)
   - Géolocalisation (pays, ville via IP)
3. Redirige (HTTP 302) vers la destination

**Réponse (302 Found):**
```
Location: https://destination-url.com
```

**Erreur (404 Not Found):**
```
Link not found
```

**Exemple:**
```
https://votre-app.onrender.com/c/AbC123Xy
→ Track click
→ Redirect to https://google.com
```

**Données trackées:**
```json
{
  "link_id": "AbC123Xy",
  "clicked_at": "2025-01-12T14:32:15Z",
  "ip_address": "195.154.123.45",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
  "country": "France",
  "city": "Paris",
  "referer": "https://linkedin.com"
}
```

---

### 3. Analytics globales

Récupère les statistiques globales de toutes les campagnes.

**Endpoint:**
```
GET /api/analytics
```

**Paramètres:** Aucun

**Réponse (200 OK):**
```json
{
  "total_links": 1247,
  "total_clicks": 892,
  "unique_clicks": 534,
  "click_rate": 42.8,
  "campaigns": [
    {
      "campaign": "outbound-q1-2025",
      "clicks": 456
    },
    {
      "campaign": "email-cold-founders",
      "clicks": 321
    }
  ],
  "recent_clicks": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "campaign": "outbound-q1-2025",
      "clicked_at": "2025-01-12T14:32:15Z",
      "country": "France",
      "city": "Paris"
    }
  ]
}
```

**Description des champs:**

| Champ | Description |
|-------|-------------|
| `total_links` | Nombre total de liens créés |
| `total_clicks` | Nombre total de clics enregistrés |
| `unique_clicks` | Nombre de liens ayant au moins 1 clic |
| `click_rate` | Taux d'ouverture en % (unique_clicks / total_links * 100) |
| `campaigns` | Liste des campagnes avec nombre de clics |
| `recent_clicks` | 10 derniers clics enregistrés |

**Exemple cURL:**
```bash
curl https://votre-app.onrender.com/api/analytics
```

**Exemple Python:**
```python
import requests

response = requests.get('https://votre-app.onrender.com/api/analytics')
data = response.json()

print(f"Taux d'ouverture: {data['click_rate']}%")
print(f"Total clics: {data['total_clicks']}")
```

---

### 4. Liste détaillée des clics

Récupère la liste complète de tous les liens avec leurs statistiques de clics, groupés par personne.

**Endpoint:**
```
GET /api/clicks
```

**Paramètres (query string):**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `campaign` | string | Non | Filtrer par nom de campagne |

**Réponse (200 OK):**
```json
[
  {
    "link_id": "AbC123Xy",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "campaign": "outbound-q1-2025",
    "created_at": "2025-01-10T10:00:00Z",
    "click_count": 3,
    "first_clicked": "2025-01-10T14:32:15Z",
    "last_clicked": "2025-01-12T09:15:22Z"
  },
  {
    "link_id": "DeF456Gh",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@startup.io",
    "campaign": "outbound-q1-2025",
    "created_at": "2025-01-10T10:05:00Z",
    "click_count": 0,
    "first_clicked": null,
    "last_clicked": null
  }
]
```

**Description des champs:**

| Champ | Type | Description |
|-------|------|-------------|
| `link_id` | string | ID unique du lien |
| `first_name` | string | Prénom de la personne |
| `last_name` | string | Nom de la personne |
| `email` | string | Email de la personne |
| `campaign` | string | Nom de la campagne |
| `created_at` | datetime | Date de création du lien |
| `click_count` | integer | Nombre de clics sur ce lien |
| `first_clicked` | datetime | Date du premier clic (null si aucun) |
| `last_clicked` | datetime | Date du dernier clic (null si aucun) |

**Exemple sans filtre:**
```bash
curl https://votre-app.onrender.com/api/clicks
```

**Exemple avec filtre campagne:**
```bash
curl "https://votre-app.onrender.com/api/clicks?campaign=outbound-q1-2025"
```

**Exemple Python avec filtre:**
```python
import requests

response = requests.get(
    'https://votre-app.onrender.com/api/clicks',
    params={'campaign': 'outbound-q1-2025'}
)

clicks = response.json()

# Voir qui a cliqué
clicked = [c for c in clicks if c['click_count'] > 0]
print(f"{len(clicked)} personnes ont cliqué")

# Voir qui n'a pas cliqué
not_clicked = [c for c in clicks if c['click_count'] == 0]
print(f"{len(not_clicked)} personnes n'ont pas cliqué")
```

---

### 5. Liste des campagnes

Récupère la liste de toutes les campagnes existantes.

**Endpoint:**
```
GET /api/campaigns
```

**Paramètres:** Aucun

**Réponse (200 OK):**
```json
[
  "outbound-q1-2025",
  "email-cold-founders",
  "linkedin-tech-leads",
  "demo-requests"
]
```

**Exemple cURL:**
```bash
curl https://votre-app.onrender.com/api/campaigns
```

**Exemple Python:**
```python
import requests

response = requests.get('https://votre-app.onrender.com/api/campaigns')
campaigns = response.json()

for campaign in campaigns:
    print(f"Campagne: {campaign}")
```

---

### 6. Dashboard web

Interface web pour visualiser les analytics en temps réel.

**Endpoint:**
```
GET /
```

**Accès:** Ouvrir dans un navigateur

```
https://votre-app.onrender.com/
```

**Fonctionnalités:**
- Statistiques globales (cartes)
- Tableau détaillé de tous les clics
- Filtrage par campagne
- Export CSV
- Rafraîchissement automatique (30s)

---

## Codes de réponse HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 201 | Ressource créée avec succès |
| 302 | Redirection (pour /c/{link_id}) |
| 400 | Requête invalide (paramètres manquants ou incorrects) |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |

---

## Limites et quotas

**Render Free Tier:**
- Pas de limite sur le nombre de liens
- Pas de limite sur le nombre de clics
- Sleep après 15 min d'inactivité
- Premier chargement après sleep : ~30-60s

**Recommandations:**
- Pour production intensive : passer au plan payant ($7/mois)
- Utiliser UptimeRobot pour éviter le sleep mode
- Backup régulier de la base de données

---

## Géolocalisation

L'API utilise [ip-api.com](http://ip-api.com) (gratuit) pour la géolocalisation.

**Données récupérées:**
- Pays (ex: "France")
- Ville (ex: "Paris")

**Limites ip-api.com:**
- 45 requêtes/minute en gratuit
- Pour plus : passer à leur plan pro

**Alternative:** Remplacer par MaxMind GeoIP2 ou ipinfo.io si besoin.

---

## Exemples d'intégration

### JavaScript (fetch)

```javascript
// Créer un lien
const createLink = async (userData) => {
  const response = await fetch('https://votre-app.onrender.com/api/create-link', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      first_name: userData.firstName,
      last_name: userData.lastName,
      email: userData.email,
      campaign: 'my-campaign',
      destination_url: 'https://example.com'
    })
  });

  const data = await response.json();
  return data.short_url;
};

// Utiliser
const shortUrl = await createLink({
  firstName: 'John',
  lastName: 'Doe',
  email: 'john@example.com'
});

console.log(shortUrl); // https://votre-app.onrender.com/c/AbC123
```

### Node.js (axios)

```javascript
const axios = require('axios');

const createLink = async (person) => {
  const response = await axios.post(
    'https://votre-app.onrender.com/api/create-link',
    {
      first_name: person.firstName,
      last_name: person.lastName,
      email: person.email,
      campaign: 'nodejs-campaign',
      destination_url: 'https://example.com'
    }
  );

  return response.data.short_url;
};

// Batch création
const people = [
  { firstName: 'John', lastName: 'Doe', email: 'john@example.com' },
  { firstName: 'Jane', lastName: 'Smith', email: 'jane@example.com' }
];

Promise.all(people.map(createLink)).then(urls => {
  console.log('All URLs:', urls);
});
```

### Google Apps Script (Google Sheets)

```javascript
function createTrackedLinks() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    const [firstName, lastName, email, campaign, destUrl] = data[i];

    const payload = {
      first_name: firstName,
      last_name: lastName,
      email: email,
      campaign: campaign,
      destination_url: destUrl
    };

    const options = {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload)
    };

    const response = UrlFetchApp.fetch(
      'https://votre-app.onrender.com/api/create-link',
      options
    );

    const result = JSON.parse(response.getContentText());
    sheet.getRange(i + 1, 7).setValue(result.short_url);
  }
}
```

---

## Webhook pour notifications (futur)

Fonctionnalité à implémenter : recevoir une notification à chaque clic.

**Configuration souhaitée:**
```json
POST /api/webhooks
{
  "url": "https://votre-webhook.com/on-click",
  "events": ["click"]
}
```

**Payload envoyé:**
```json
{
  "event": "click",
  "link_id": "AbC123Xy",
  "person": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "click_data": {
    "timestamp": "2025-01-12T14:32:15Z",
    "country": "France",
    "city": "Paris"
  }
}
```

---

## Rate Limiting

Actuellement **aucune limite** n'est implémentée.

Pour production, recommandations :
- Implémenter rate limiting (ex: Flask-Limiter)
- Limite suggérée : 100 requêtes/minute par IP
- Authentification via API key pour clients privilégiés

---

## Support

Questions ou bugs :
1. Vérifier les logs Render
2. Tester avec curl/Postman
3. Consulter les guides DEPLOYMENT.md et CLAY_INTEGRATION.md
