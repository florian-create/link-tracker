# Guide: Mettre à jour les liens existants

## 🎯 Endpoint: `/api/update-link`

Cet endpoint permet de mettre à jour les informations company/LinkedIn sur des liens déjà créés.

---

## 📡 Configuration de l'API

**Method:** `POST` ou `PUT`

**URL:** `https://TON-APP.onrender.com/api/update-link`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

---

## 📝 Body de la requête

### Champs requis (au moins un des deux):
- `email` : Email de la personne pour identifier le lien
- `link_id` : ID du lien court (ex: "AbC123Xy")

### Champs optionnels à mettre à jour:
- `company_name` : Nom de l'entreprise
- `company_url` : URL du site de l'entreprise
- `linkedin_url` : URL du profil LinkedIn

**⚠️ Important:** Au moins un champ à mettre à jour doit être fourni.

---

## 🧪 Exemples d'utilisation

### Exemple 1: Update par email
```bash
curl -X POST https://link-tracker-r68v.onrender.com/api/update-link \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "company_name": "Google",
    "company_url": "https://google.com",
    "linkedin_url": "https://linkedin.com/in/johndoe"
  }'
```

### Exemple 2: Update par link_id
```bash
curl -X POST https://link-tracker-r68v.onrender.com/api/update-link \
  -H "Content-Type: application/json" \
  -d '{
    "link_id": "AbC123Xy",
    "company_name": "Microsoft",
    "company_url": "https://microsoft.com"
  }'
```

### Exemple 3: Update seulement LinkedIn
```bash
curl -X POST https://link-tracker-r68v.onrender.com/api/update-link \
  -H "Content-Type: application/json" \
  -d '{
    "email": "marie@example.com",
    "linkedin_url": "https://linkedin.com/in/marie-dupont"
  }'
```

---

## 📊 Réponses de l'API

### ✅ Succès (200)
```json
{
  "success": true,
  "message": "Updated 1 link(s)",
  "link": {
    "link_id": "AbC123Xy",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "company_name": "Google",
    "company_url": "https://google.com",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "campaign": "test",
    "created_at": "2025-01-15T10:30:00"
  }
}
```

### ❌ Erreur: Link non trouvé (404)
```json
{
  "error": "Link not found",
  "searched_by": "email",
  "value": "john@example.com"
}
```

### ❌ Erreur: Identifiant manquant (400)
```json
{
  "error": "email or link_id is required to identify the link"
}
```

### ❌ Erreur: Aucun champ à mettre à jour (400)
```json
{
  "error": "No fields to update. Provide company_name, company_url, or linkedin_url"
}
```

---

## 🏗️ Configuration dans Clay

### Étape 1: Créer un enrichissement "HTTP API"

**Method:** POST

**URL:** `https://link-tracker-r68v.onrender.com/api/update-link`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "{{Email}}",
  "company_name": "{{Company Name}}",
  "company_url": "{{Company Website}}",
  "linkedin_url": "{{LinkedIn URL}}"
}
```

### Étape 2: Mapper les colonnes Clay

Remplace les valeurs entre `{{}}` par les noms exacts de tes colonnes Clay:
- `{{Email}}` → Colonne email
- `{{Company Name}}` → Colonne du nom de l'entreprise
- `{{Company Website}}` → Colonne URL du site
- `{{LinkedIn URL}}` → Colonne URL LinkedIn

### Étape 3: Extraire la réponse

Dans Clay, tu peux extraire:
- `{{HTTP API Response.success}}` → true/false
- `{{HTTP API Response.message}}` → Message de confirmation
- `{{HTTP API Response.link.company_name}}` → Nom vérifié

---

## 🔄 Workflow complet dans Clay

### Option A: Update en masse de tous les liens existants

1. **Table 1:** Ta liste de prospects existants (avec emails)
2. **Enrichir:** Ajouter les colonnes company et LinkedIn (via enrichissement LinkedIn/Clearbit/etc)
3. **HTTP API:** Appeler `/api/update-link` pour chaque ligne
4. **Résultat:** Tous tes liens existants sont mis à jour

### Option B: Update sélectif

1. Filtre les lignes où `company_name` est vide dans ta base
2. Lance l'update seulement sur ces lignes
3. Les autres restent intactes

---

## ⚠️ Notes importantes

1. **Email comme identifiant:** L'email doit correspondre exactement à celui utilisé lors de la création du lien
2. **Majuscules/minuscules:** L'email n'est PAS sensible à la casse
3. **Plusieurs liens par email:** Si plusieurs liens existent pour le même email, seul le premier sera mis à jour
4. **Champs vides:** Pour vider un champ, envoie une chaîne vide `""`
5. **Champs non fournis:** Les champs non inclus dans la requête ne seront pas modifiés

---

## 🧪 Test rapide

```bash
# 1. Créer un lien
curl -X POST https://link-tracker-r68v.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "campaign": "test",
    "destination_url": "https://example.com"
  }'

# 2. Mettre à jour avec les infos company/LinkedIn
curl -X POST https://link-tracker-r68v.onrender.com/api/update-link \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "company_name": "Test Company",
    "company_url": "https://testcompany.com",
    "linkedin_url": "https://linkedin.com/in/testuser"
  }'

# 3. Vérifier dans le dashboard
# Ouvre: https://link-tracker-r68v.onrender.com/
```

---

## 📞 Support

Si tu as des questions ou problèmes:
1. Vérifie que l'email correspond exactement
2. Regarde les logs dans Render
3. Teste d'abord avec curl/Postman avant Clay
