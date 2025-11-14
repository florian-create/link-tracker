# 🔗 URLs et Configuration - Aide-mémoire

Document à garder sous la main pour configurer Clay et accéder aux dashboards.

---

## 🏠 Link Tracker - URLs principales

### Dashboard Analytics
```
https://VOTRE-APP.onrender.com/
```

### API - Créer un lien
```
https://VOTRE-APP.onrender.com/api/create-link
```

### API - Analytics globales
```
https://VOTRE-APP.onrender.com/api/analytics
```

### API - Analytics filtrées Aura
```
https://VOTRE-APP.onrender.com/api/analytics?campaign=aura.camp
```

### API - Analytics filtrées Wesser
```
https://VOTRE-APP.onrender.com/api/analytics?campaign=wesser-recrutement.fr
```

### API - Liste des campagnes
```
https://VOTRE-APP.onrender.com/api/campaigns
```

---

## 🎨 Configuration Clay - Copy/Paste

### Pour AURA.CAMP

**URL API:**
```
https://VOTRE-APP.onrender.com/api/create-link
```

**Body JSON:**
```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "aura.camp",
  "destination_url": "https://aura.camp/demo"
}
```

### Pour WESSER-RECRUTEMENT.FR

**URL API:**
```
https://VOTRE-APP.onrender.com/api/create-link
```

**Body JSON:**
```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
```

---

## 📊 Render - Accès

### Dashboard Render
```
https://dashboard.render.com
```

### Logs de l'application
```
https://dashboard.render.com/web/VOTRE-SERVICE-ID
→ Onglet "Logs"
```

### Base de données PostgreSQL
```
https://dashboard.render.com/d/VOTRE-DB-ID
→ Onglet "Info" pour voir la connection string
```

---

## 🧪 Tests rapides

### Test 1 : API en ligne ?
```bash
curl https://VOTRE-APP.onrender.com/api/campaigns
```

Réponse attendue : `["aura.camp","wesser-recrutement.fr"]` (ou vide si aucune campagne)

### Test 2 : Créer un lien de test
```bash
curl -X POST https://VOTRE-APP.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "campaign": "test",
    "destination_url": "https://google.com"
  }'
```

Réponse attendue :
```json
{
  "success": true,
  "short_url": "https://VOTRE-APP.onrender.com/c/AbC123",
  "link_id": "AbC123"
}
```

### Test 3 : Script complet
```bash
cd /Users/florian/Desktop/link-tracker
python3 test_multi_campaign.py
```

---

## 🔑 GitHub

### Repository
```
https://github.com/florian-create/link-tracker
```

### Cloner
```bash
git clone https://github.com/florian-create/link-tracker.git
```

### Pousser les modifications
```bash
cd /Users/florian/Desktop/link-tracker
git add .
git commit -m "Description des modifications"
git push
```

---

## 📖 Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation générale du projet |
| `DEPLOYMENT.md` | Guide de déploiement sur Render |
| `CLAY_INTEGRATION.md` | Intégration Clay originale |
| `WESSER_SETUP.md` | Guide complet Wesser |
| `CLAY_WESSER_CONFIG.md` | Configuration Clay détaillée Wesser |
| `QUICK_START_WESSER.md` | Quick start 5 minutes Wesser |
| `CLAY_VISUAL_GUIDE.txt` | Guide visuel ASCII |
| `API.md` | Documentation API complète |

---

## 🎯 Workflow typique

### 1. Créer campagne dans Clay

1. Nouvelle table Clay
2. Importer prospects
3. Ajouter enrichissement HTTP API
4. Configurer avec body JSON (voir ci-dessus)
5. Extraire `short_url` avec formule

### 2. Envoyer messages

1. LinkedIn / Email avec lien `{{Wesser Tracking Link}}`
2. Les clics sont trackés automatiquement

### 3. Analyser résultats

1. Ouvrir dashboard
2. Filtrer par campagne
3. Identifier hot leads (2+ clics)
4. Exporter CSV
5. Relancer non-cliqueurs

---

## ⚡ Commandes utiles

### Vérifier les fichiers locaux
```bash
ls -la /Users/florian/Desktop/link-tracker/
```

### Voir les commits récents
```bash
cd /Users/florian/Desktop/link-tracker
git log --oneline -5
```

### Voir le statut Git
```bash
cd /Users/florian/Desktop/link-tracker
git status
```

### Redéployer sur Render
Render redéploie automatiquement à chaque push GitHub.

Pour forcer un redéploiement manuel :
1. Aller sur dashboard.render.com
2. Sélectionner le service "link-tracker"
3. Cliquer "Manual Deploy" → "Deploy latest commit"

---

## 🚨 Troubleshooting rapide

### App en sleep (erreur timeout)
**Solution :** Ouvrir `https://VOTRE-APP.onrender.com/` dans un navigateur et attendre 30 secondes

### Base de données vide
**Solution :** Vérifier que PostgreSQL est bien connecté dans Render → Environment Variables → `DATABASE_URL`

### Liens non créés dans Clay
**Solution :** Vérifier l'URL API (doit finir par `/api/create-link`)

### Dashboard ne charge pas
**Solution :** Vérifier les logs Render pour voir les erreurs

### Campagne n'apparaît pas dans le filtre
**Solution :** Créer au moins 1 lien avec cette campagne, puis rafraîchir le dashboard

---

## 📞 Ressources

- **Render Docs:** https://render.com/docs
- **Clay Docs:** https://clay.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

## ✅ Checklist de vérification

Avant de lancer une nouvelle campagne :

- [ ] Link tracker déployé et accessible
- [ ] Dashboard affiche correctement les stats
- [ ] Test de création de lien réussi (curl ou Clay)
- [ ] Test de clic et redirection réussi
- [ ] Filtre de campagne fonctionne dans le dashboard
- [ ] Export CSV testé
- [ ] Messages LinkedIn/Email prêts avec liens trackés
- [ ] Test sur 5-10 prospects avant envoi massif

---

**Dernière mise à jour :** 14 novembre 2025
