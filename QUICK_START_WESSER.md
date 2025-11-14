# ⚡ Quick Start Wesser - 5 minutes

Configuration ultra-rapide de Clay pour Wesser.

---

## 🎯 Objectif

Générer des liens trackés personnalisés pour chaque prospect Wesser et suivre qui clique.

---

## 📋 Configuration Clay en 3 étapes

### 1️⃣ Ajouter HTTP API Enrichment

Dans Clay : **Add Enrichment** → **HTTP API**

### 2️⃣ Copier-coller cette config

**Method:** `POST`

**URL:**
```
https://VOTRE-APP.onrender.com/api/create-link
```
🔴 **REMPLACER `VOTRE-APP`** par le nom de votre app Render

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
```

🔴 **ADAPTER** `{{first_name}}` etc. aux noms de vos colonnes Clay
🔴 **REMPLACER** `destination_url` par votre vraie landing page

### 3️⃣ Extraire le lien

Créer une colonne **Formula** :
```javascript
{{HTTP API Response.short_url}}
```

Renommer en : **"Wesser Tracking Link"**

---

## 💬 Utiliser dans vos messages

```
Bonjour {{first_name}},

Découvrez notre offre Wesser : {{Wesser Tracking Link}}

Cordialement
```

---

## 📊 Voir les résultats

Dashboard : `https://votre-app.onrender.com/`

Filtre : **"wesser-recrutement.fr"**

---

## ✅ Test rapide

```bash
cd /Users/florian/Desktop/link-tracker
python3 test_multi_campaign.py
```

---

**Documentation complète :** [CLAY_WESSER_CONFIG.md](./CLAY_WESSER_CONFIG.md)
