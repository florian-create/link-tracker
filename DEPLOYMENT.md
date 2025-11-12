# 🚀 Guide de déploiement sur Render

## Étape 1 : Préparer le projet

1. Créer un repository Git
```bash
cd ~/Desktop/link-tracker
git init
git add .
git commit -m "Initial commit - Link tracker system"
```

2. Créer un repository sur GitHub
   - Aller sur https://github.com/new
   - Nommer le repo : `link-tracker`
   - Ne pas initialiser avec README

3. Pousser le code
```bash
git remote add origin https://github.com/VOTRE-USERNAME/link-tracker.git
git branch -M main
git push -u origin main
```

## Étape 2 : Déployer sur Render

### Option A : Déploiement automatique avec render.yaml

1. Aller sur https://render.com
2. Se connecter / Créer un compte (gratuit)
3. Cliquer sur "New +" → "Blueprint"
4. Connecter votre repository GitHub `link-tracker`
5. Render détectera automatiquement le fichier `render.yaml`
6. Cliquer sur "Apply"
7. Attendre 3-5 minutes que le déploiement se termine

### Option B : Déploiement manuel

1. **Créer la base de données PostgreSQL**
   - Dashboard Render → "New +" → "PostgreSQL"
   - Name: `link-tracker-db`
   - Plan: Free
   - Cliquer sur "Create Database"
   - Noter l'URL de connexion (Internal Database URL)

2. **Créer le Web Service**
   - Dashboard → "New +" → "Web Service"
   - Connecter votre repo GitHub
   - Settings:
     - **Name**: `link-tracker`
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Plan**: Free

3. **Ajouter les variables d'environnement**
   - Dans le Web Service → "Environment"
   - Ajouter:
     - `DATABASE_URL` = [Internal Database URL de votre PostgreSQL]
     - `PYTHON_VERSION` = `3.11.0`

4. **Déployer**
   - Cliquer sur "Create Web Service"
   - Attendre le déploiement (3-5 min)

## Étape 3 : Vérifier le déploiement

1. Une fois déployé, vous aurez une URL type:
   ```
   https://link-tracker-xxxx.onrender.com
   ```

2. Ouvrir l'URL dans le navigateur
   - Vous devriez voir le dashboard analytics

3. Tester l'API:
   ```bash
   curl -X POST https://link-tracker-xxxx.onrender.com/api/create-link \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "John",
       "last_name": "Doe",
       "email": "john@example.com",
       "campaign": "test",
       "destination_url": "https://google.com"
     }'
   ```

## Étape 4 : Configuration du domaine personnalisé (Optionnel)

Si vous voulez un domaine personnalisé (ex: `track.votresite.com`):

1. **Dans Render**
   - Web Service → Settings → Custom Domain
   - Ajouter votre domaine: `track.votresite.com`

2. **Dans votre DNS** (Cloudflare, OVH, etc.)
   - Ajouter un CNAME:
     - Type: `CNAME`
     - Name: `track`
     - Value: `link-tracker-xxxx.onrender.com`

3. Attendre la propagation DNS (5-30 minutes)

## 🎯 URLs importantes après déploiement

- **Dashboard**: `https://votre-app.onrender.com/`
- **API Create Link**: `https://votre-app.onrender.com/api/create-link`
- **API Analytics**: `https://votre-app.onrender.com/api/analytics`
- **API Clicks**: `https://votre-app.onrender.com/api/clicks`
- **Redirect**: `https://votre-app.onrender.com/c/{link_id}`

## ⚠️ Important : Free Tier Render

Le plan gratuit Render a quelques limitations:

- **Sleep après inactivité**: L'app se met en veille après 15 min d'inactivité
- **Premier chargement lent**: Peut prendre 30-60 secondes au réveil
- **750h/mois gratuit**: Largement suffisant pour usage normal
- **Base de données**: 90 jours de rétention, puis suppression si inactif

**Pour éviter le sleep mode** (optionnel):
- Utiliser un service comme UptimeRobot (gratuit) pour ping toutes les 5 min
- Ou passer au plan payant ($7/mois pour instance toujours active)

## 🔧 Maintenance

### Voir les logs
```
Render Dashboard → Votre service → Logs
```

### Redéployer manuellement
```
Render Dashboard → Votre service → Manual Deploy → Deploy latest commit
```

### Variables d'environnement
```
Render Dashboard → Votre service → Environment
```

## 🆘 Problèmes courants

**Erreur "Application failed to respond"**
- Vérifier que `DATABASE_URL` est bien configuré
- Regarder les logs pour voir l'erreur exacte

**Database connection failed**
- Vérifier que la base PostgreSQL est bien créée
- Vérifier que l'URL de connexion est correcte

**502 Bad Gateway**
- L'app est probablement en train de se réveiller du sleep mode
- Attendre 30-60 secondes et rafraîchir

## ✅ Checklist de déploiement

- [ ] Code poussé sur GitHub
- [ ] Base de données PostgreSQL créée sur Render
- [ ] Web Service créé et déployé
- [ ] Variable `DATABASE_URL` configurée
- [ ] Dashboard accessible via l'URL Render
- [ ] Test API `/api/create-link` réussi
- [ ] Lien court testé et redirection fonctionnelle
- [ ] Dashboard affiche les statistiques

🎉 Votre système de tracking de liens est maintenant déployé !
