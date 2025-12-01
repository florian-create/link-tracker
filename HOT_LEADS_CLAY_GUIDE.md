# 🔥 Guide: Envoyer automatiquement les Hot Leads (5+ clics) vers Clay

## 🎯 Vue d'ensemble

Ce système envoie automatiquement les leads qui ont cliqué **5 fois ou plus** sur leur lien vers une table Clay, **toutes les heures**.

### Fonctionnalités :
- ✅ Détecte automatiquement les leads avec 5+ clics
- ✅ Envoie toutes les infos (nom, email, company, LinkedIn, clics, etc.) vers Clay
- ✅ **Ne renvoie jamais les mêmes leads** (évite les doublons)
- ✅ Exécution automatique toutes les heures via cron
- ✅ Peut être déclenché manuellement à tout moment

---

## 📋 Étape 1 : Créer un Webhook dans Clay

### 1.1 Dans Clay, crée une nouvelle table "Hot Leads"

### 1.2 Ajoute un webhook :
1. Clique sur "Add via Webhook" ou "Import via HTTP API"
2. Clay va te donner une URL de webhook comme :
   ```
   https://webhook.clay.com/webhook/abc123def456...
   ```
3. **Copie cette URL** (tu en auras besoin)

### 1.3 Structure de données que Clay recevra :

Chaque lead envoyé aura ces champs :

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "company_name": "Google",
  "company_url": "https://google.com",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "icp": "Enterprise",
  "campaign": "outbound-q1",
  "click_count": 7,
  "first_clicked": "2025-01-15T10:30:00",
  "last_clicked": "2025-01-20T15:45:00",
  "link_id": "AbC123Xy",
  "tracking_url": "https://link-tracker.onrender.com/c/AbC123Xy"
}
```

Clay va automatiquement créer les colonnes correspondantes.

---

## ⚙️ Étape 2 : Configuration sur Render

### 2.1 Ajouter la variable d'environnement

1. Va sur **Render Dashboard** → Ton app link-tracker
2. Onglet **"Environment"**
3. Ajoute une nouvelle variable :
   - **Key:** `CLAY_WEBHOOK_URL`
   - **Value:** `https://webhook.clay.com/webhook/abc123def456...` (ton URL Clay)
4. Clique **"Save Changes"**

L'app va redémarrer automatiquement.

### 2.2 Lancer la migration de la base de données

Dans le **Shell** de Render :
```bash
python migrate_add_clay_tracking.py
```

Tu devrais voir :
```
✅ Added column: sent_to_clay
✅ Added column: sent_to_clay_at
✅ Migration completed successfully!
```

---

## 🚀 Étape 3 : Configuration du Cron Job (Automatique toutes les heures)

### Option A : Cron Job sur Render (Recommandé)

1. Dans Render, va dans ton service
2. Clique sur **"Cron Jobs"** dans le menu
3. Ajoute un nouveau Cron Job :
   - **Command:** `python cron_hot_leads.py`
   - **Schedule:** `0 * * * *` (toutes les heures)
   - Ou utilise l'interface visuelle : "Every 1 hour"
4. Sauvegarde

**Note :** Le cron job utilisera automatiquement la variable `CLAY_WEBHOOK_URL` que tu as configurée.

### Option B : Service externe (cron-job.org)

Si Render ne supporte pas les cron jobs sur ton plan :

1. Va sur https://cron-job.org/
2. Crée un compte gratuit
3. Crée un nouveau cron job :
   - **URL:** `https://link-tracker-r68v.onrender.com/api/webhook/hot-leads`
   - **Method:** POST
   - **Headers:** `Content-Type: application/json`
   - **Body:**
     ```json
     {
       "clay_webhook_url": "https://webhook.clay.com/webhook/abc123...",
       "min_clicks": 5
     }
     ```
   - **Schedule:** Every hour (0 * * * *)
4. Active le cron job

---

## 🧪 Étape 4 : Test manuel

### 4.1 Test complet

```bash
curl -X POST https://link-tracker-r68v.onrender.com/api/webhook/hot-leads \
  -H "Content-Type: application/json" \
  -d '{
    "clay_webhook_url": "https://webhook.clay.com/webhook/TON-WEBHOOK",
    "min_clicks": 5
  }'
```

**Réponse attendue :**
```json
{
  "success": true,
  "message": "Sent 3 hot leads to Clay",
  "sent_count": 3,
  "total_found": 3,
  "min_clicks": 5
}
```

### 4.2 Vérifier dans Clay

Va dans ta table Clay, tu devrais voir les nouveaux leads apparaître ! 🎉

---

## 🔧 Options avancées

### Changer le nombre minimum de clics

Par défaut : **5 clics**. Pour changer (ex: 3 clics) :

```bash
curl -X POST https://link-tracker-r68v.onrender.com/api/webhook/hot-leads \
  -H "Content-Type: application/json" \
  -d '{
    "clay_webhook_url": "https://webhook.clay.com/webhook/...",
    "min_clicks": 3
  }'
```

### Filtrer par campagne

Envoyer seulement les leads d'une campagne spécifique :

```bash
curl -X POST https://link-tracker-r68v.onrender.com/api/webhook/hot-leads \
  -H "Content-Type: application/json" \
  -d '{
    "clay_webhook_url": "https://webhook.clay.com/webhook/...",
    "min_clicks": 5,
    "campaign": "outbound-q1"
  }'
```

### Réinitialiser le statut d'envoi (pour tester)

Si tu veux renvoyer des leads déjà envoyés :

```bash
# Réinitialiser un lead spécifique
curl -X POST https://link-tracker-r68v.onrender.com/api/webhook/reset-clay-status \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com"}'

# Réinitialiser TOUS les leads (attention!)
curl -X POST https://link-tracker-r68v.onrender.com/api/webhook/reset-clay-status \
  -H "Content-Type: application/json"
```

---

## 📊 Comment ça marche ?

### Flux de données :

1. **Toutes les heures**, le cron job s'exécute
2. Il cherche dans la base tous les leads avec :
   - `click_count >= 5`
   - `sent_to_clay = FALSE` (pas encore envoyés)
3. Pour chaque lead trouvé :
   - Envoie les données au webhook Clay
   - Marque le lead comme `sent_to_clay = TRUE`
   - Enregistre la date d'envoi dans `sent_to_clay_at`
4. Les leads déjà envoyés ne seront **jamais renvoyés**

### Colonnes ajoutées à la table `links` :

- `sent_to_clay` (BOOLEAN) : Si le lead a été envoyé à Clay
- `sent_to_clay_at` (TIMESTAMP) : Date et heure de l'envoi

---

## 🔍 Monitoring

### Vérifier les logs sur Render

1. Va sur ton app Render
2. Onglet **"Logs"**
3. Recherche : `hot leads`

Tu verras les logs des exécutions du cron :
```
[2025-01-20 10:00:00] Checking for hot leads (min 5 clicks)...
[2025-01-20 10:00:02] ✅ SUCCESS: Sent 3 hot leads to Clay
   - Sent: 3 leads
   - Total found: 3 leads
```

### Dashboard Analytics

Dans ton dashboard `https://link-tracker-r68v.onrender.com/`, tu peux voir :
- Les leads avec 5+ clics dans le tableau "Click Details"
- Le nombre total de clics par personne

---

## 🚨 Dépannage

### Problème : "No hot leads found"
- Vérifie qu'il y a des leads avec 5+ clics dans ta base
- Vérifie qu'ils n'ont pas déjà été envoyés (`sent_to_clay = TRUE`)
- Réinitialise le statut pour tester : `/api/webhook/reset-clay-status`

### Problème : "Clay webhook returned 4XX/5XX"
- Vérifie que ton URL de webhook Clay est correcte
- Vérifie que la table Clay est bien configurée pour recevoir des webhooks
- Teste le webhook manuellement dans Clay

### Problème : Le cron ne s'exécute pas
- Vérifie que le cron job est bien activé sur Render
- Vérifie que la variable `CLAY_WEBHOOK_URL` est bien configurée
- Regarde les logs Render pour voir les erreurs

### Problème : Doublons dans Clay
- Normalement impossible grâce à `sent_to_clay`
- Si ça arrive, vérifie que la migration a bien été lancée
- Utilise `/api/webhook/reset-clay-status` pour tester

---

## 📈 Cas d'usage

### Use Case 1 : Lead Scoring
Les leads avec 5+ clics sont **très engagés**. Envoie-les automatiquement à ton équipe Sales via Clay pour qu'ils les rappellent immédiatement.

### Use Case 2 : Nurturing personnalisé
Dans Clay, crée un workflow qui :
1. Reçoit les hot leads
2. Les enrichit avec des données supplémentaires
3. Lance une séquence email personnalisée ultra-chaude

### Use Case 3 : Alertes Slack
Configure Clay pour envoyer une notification Slack quand un hot lead arrive :
*"🔥 John Doe (Google) a cliqué 7 fois sur ton lien !"*

---

## 📝 Résumé de la configuration

1. ✅ Créer un webhook Clay et copier l'URL
2. ✅ Ajouter `CLAY_WEBHOOK_URL` dans les variables d'environnement Render
3. ✅ Lancer `python migrate_add_clay_tracking.py` dans le Shell Render
4. ✅ Configurer le cron job (toutes les heures)
5. ✅ Tester manuellement avec curl
6. ✅ Vérifier les données dans Clay

**C'est tout ! Tes hot leads seront maintenant envoyés automatiquement à Clay toutes les heures ! 🚀**

---

## 🆘 Support

Si tu as des questions :
1. Vérifie les logs Render
2. Teste manuellement l'endpoint
3. Vérifie que le webhook Clay fonctionne
