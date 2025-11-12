# 🔗 Link Tracker - Système de tracking de liens personnalisés

Un système complet de création et tracking de liens raccourcis personnalisés avec analytics détaillés, conçu pour s'intégrer parfaitement avec Clay.

## 🎯 Fonctionnalités

- ✅ **Génération de liens uniques** pour chaque prospect
- ✅ **Tracking détaillé** : qui a cliqué, quand, combien de fois
- ✅ **Dashboard analytics en temps réel** avec visualisations
- ✅ **Intégration Clay native** via webhook HTTP
- ✅ **API REST complète** pour automatisation
- ✅ **Géolocalisation** des clics (pays, ville)
- ✅ **Export CSV** de toutes les données
- ✅ **Multi-campagnes** pour segmenter vos actions
- ✅ **Gratuit** à déployer sur Render

## 📊 Cas d'usage

- Campagnes d'outreach LinkedIn (voir qui ouvre vos liens)
- Email marketing avec tracking personnalisé
- A/B testing de landing pages
- Suivi de conversion par personne
- Analytics détaillés de vos campagnes

## 🚀 Démarrage rapide

### 1. Cloner le projet

```bash
cd ~/Desktop/link-tracker
```

### 2. Déployer sur Render

Suivre le guide complet : **[DEPLOYMENT.md](./DEPLOYMENT.md)**

En résumé :
1. Créer un repo GitHub
2. Pousser le code
3. Connecter à Render
4. Déployer automatiquement avec `render.yaml`

### 3. Intégrer avec Clay

Suivre le guide complet : **[CLAY_INTEGRATION.md](./CLAY_INTEGRATION.md)**

Configuration rapide dans Clay :
```json
POST https://votre-app.onrender.com/api/create-link

{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "ma-campagne",
  "destination_url": "https://monsite.com/landing"
}
```

Réponse :
```json
{
  "short_url": "https://votre-app.onrender.com/c/AbC123",
  "link_id": "AbC123"
}
```

## 📖 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Guide complet de déploiement sur Render
- **[CLAY_INTEGRATION.md](./CLAY_INTEGRATION.md)** - Intégration avec Clay pas à pas
- **[API.md](./API.md)** - Documentation complète de l'API

## 🏗️ Architecture

```
Clay (prospects)
    ↓
HTTP Request → API Flask (Render)
    ↓
PostgreSQL Database
    ↓
Dashboard Analytics
```

**Stack technique :**
- Backend : Python + Flask
- Base de données : PostgreSQL
- Frontend : HTML/CSS/JS (dashboard intégré)
- Déploiement : Render (free tier)
- Intégration : Clay HTTP API

## 📡 API Endpoints

### Créer un lien
```bash
POST /api/create-link
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "campaign": "outbound-q1",
  "destination_url": "https://example.com"
}
```

### Rediriger et tracker
```bash
GET /c/{link_id}
```

### Analytics globales
```bash
GET /api/analytics
```

### Liste des clics détaillés
```bash
GET /api/clicks?campaign=outbound-q1
```

### Liste des campagnes
```bash
GET /api/campaigns
```

## 📊 Dashboard

Accès : `https://votre-app.onrender.com/`

**Métriques affichées :**
- Nombre total de liens créés
- Nombre total de clics
- Nombre de personnes uniques ayant cliqué
- Taux d'ouverture (%)
- Tableau détaillé : nom, email, campagne, nombre de clics, dates
- Export CSV

**Fonctionnalités :**
- ✅ Rafraîchissement auto toutes les 30 secondes
- ✅ Filtrage par campagne
- ✅ Export CSV complet
- ✅ Vue en temps réel

## 🔧 Installation locale (développement)

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données locale
export DATABASE_URL="postgresql://localhost/link_tracker_dev"

# Créer la base de données
createdb link_tracker_dev

# Lancer l'application
python app.py
```

Ouvrir : `http://localhost:5000`

## 🌍 Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@host/db` |
| `PORT` | Port du serveur (auto sur Render) | `5000` |

## 💰 Coûts

**Free tier Render :**
- ✅ Web Service : 750h/mois gratuit
- ✅ PostgreSQL : Gratuit (90 jours de rétention)
- ✅ Liens illimités
- ⚠️ Sleep après 15 min d'inactivité (réveil en ~30s)

**Pour upgrade :**
- Instance toujours active : $7/mois
- PostgreSQL persistant : $7/mois

## 📈 Exemples de résultats

**Dashboard :**
```
📊 Statistiques
├─ Total Liens : 1,247
├─ Total Clics : 892
├─ Personnes Uniques : 534
└─ Taux d'ouverture : 42.8%

📋 Détails des clics
├─ John Doe | john@company.com | 3 clics | 10/01 14:32
├─ Jane Smith | jane@startup.io | 1 clic | 10/01 15:45
└─ ...
```

**Export CSV :**
```csv
Prénom,Nom,Email,Campagne,Clics,Premier clic,Dernier clic,Statut
John,Doe,john@company.com,outbound-q1,3,10/01/2025 14:32,11/01/2025 09:15,Cliqué
Jane,Smith,jane@startup.io,outbound-q1,1,10/01/2025 15:45,10/01/2025 15:45,Cliqué
```

## 🤝 Workflow typique

1. **Créer table Clay** avec vos prospects (nom, prénom, email)
2. **Ajouter enrichissement HTTP** pour générer les liens
3. **Envoyer vos messages** avec les liens personnalisés
4. **Consulter le dashboard** pour voir qui a cliqué
5. **Exporter en CSV** pour analyse ou CRM
6. **Relancer les non-cliqueurs** avec une nouvelle campagne

## 🔒 Sécurité

- Pas de données sensibles stockées
- HTTPS par défaut sur Render
- CORS configuré
- Pas d'authentification nécessaire pour MVP (ajouter si besoin)

## 🛠️ Technologies utilisées

- **Python 3.11**
- **Flask** - Framework web
- **PostgreSQL** - Base de données
- **psycopg2** - Driver PostgreSQL
- **Gunicorn** - Serveur WSGI production
- **Requests** - Géolocalisation IP

## 📝 Structure du projet

```
link-tracker/
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances Python
├── render.yaml              # Configuration Render
├── .gitignore               # Fichiers à ignorer
├── README.md                # Ce fichier
├── DEPLOYMENT.md            # Guide de déploiement
├── CLAY_INTEGRATION.md      # Guide Clay
└── API.md                   # Documentation API
```

## 🎯 Roadmap

Fonctionnalités potentielles futures :
- [ ] Authentification multi-utilisateurs
- [ ] QR codes générés automatiquement
- [ ] Webhooks pour notifier les clics
- [ ] Intégration native CRM (HubSpot, Salesforce)
- [ ] Domaine personnalisé facilité
- [ ] Analytics avancés (heatmap, parcours utilisateur)

## 📞 Support

En cas de problème :
1. Consulter [DEPLOYMENT.md](./DEPLOYMENT.md) - section Troubleshooting
2. Consulter [CLAY_INTEGRATION.md](./CLAY_INTEGRATION.md) - section Troubleshooting
3. Vérifier les logs Render
4. Tester l'API avec curl/Postman

## 📄 Licence

Projet personnel - Libre d'utilisation

---

🚀 **Prêt à tracker vos campagnes !**

Commencez par déployer sur Render : [DEPLOYMENT.md](./DEPLOYMENT.md)
