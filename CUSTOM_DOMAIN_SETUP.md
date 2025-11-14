# 🌐 Configuration des Domaines Personnalisés

Guide complet pour configurer `wesser-recrutement.fr` et `agence.aura.camp` pour vos liens trackés.

---

## 🎯 Fonctionnement

Le système supporte maintenant **plusieurs domaines personnalisés par campagne** :

- **Campagne Wesser** → Liens avec `wesser-recrutement.fr`
- **Campagne Aura** → Liens avec `agence.aura.camp`
- **Autres campagnes** → Domaine par défaut

**Exemple :**
```json
{
  "campaign": "wesser-recrutement.fr"
}
```
→ Génère un lien : `https://wesser-recrutement.fr/c/AbC123`

---

## 📋 Étape 1 : Configuration DNS

### Pour wesser-recrutement.fr

Aller sur votre registrar de domaine (OVH, Gandi, Cloudflare, etc.) et ajouter ces enregistrements DNS :

**Type A (ou CNAME selon Render) :**

Si Render vous donne une IP :
```
Type: A
Name: @
Value: XXX.XXX.XXX.XXX (IP fournie par Render)
TTL: 3600
```

Si Render vous donne un CNAME :
```
Type: CNAME
Name: @
Value: votre-app.onrender.com
TTL: 3600
```

**Pour le sous-domaine www (optionnel) :**
```
Type: CNAME
Name: www
Value: wesser-recrutement.fr
TTL: 3600
```

### Pour agence.aura.camp (si pas déjà fait)

Même principe sur le domaine `aura.camp` :

```
Type: CNAME
Name: agence
Value: votre-app.onrender.com
TTL: 3600
```

---

## 📋 Étape 2 : Configuration Render

### 1. Ajouter le domaine personnalisé dans Render

1. Aller sur [dashboard.render.com](https://dashboard.render.com)
2. Cliquer sur votre service **"link-tracker"**
3. Aller dans l'onglet **"Settings"**
4. Scroller jusqu'à **"Custom Domains"**
5. Cliquer sur **"Add Custom Domain"**

**Ajouter wesser-recrutement.fr :**
```
Domain: wesser-recrutement.fr
```
Cliquer sur **"Save"**

**Ajouter www.wesser-recrutement.fr (optionnel) :**
```
Domain: www.wesser-recrutement.fr
```
Cliquer sur **"Save"**

### 2. Vérifier le certificat SSL

Render va automatiquement provisionner un certificat SSL Let's Encrypt.

**Statut attendu :**
- ✅ `wesser-recrutement.fr` → Verified (peut prendre 5-10 minutes)
- ✅ SSL Certificate → Issued

Si erreur "Verification failed" :
- Vérifier que les DNS pointent bien vers Render
- Attendre 24-48h pour propagation DNS
- Retenter la vérification

---

## 📋 Étape 3 : Variables d'environnement Render

### Ajouter les variables d'environnement

1. Dashboard Render → Service "link-tracker" → **"Environment"**
2. Cliquer sur **"Add Environment Variable"**

**Variable 1 : WESSER_DOMAIN**
```
Key: WESSER_DOMAIN
Value: wesser-recrutement.fr
```

**Variable 2 : AURA_DOMAIN**
```
Key: AURA_DOMAIN
Value: agence.aura.camp
```

**Variable 3 : CUSTOM_DOMAIN (fallback par défaut)**
```
Key: CUSTOM_DOMAIN
Value: link-tracker.onrender.com
```
(Ou votre domaine Render actuel)

3. Cliquer sur **"Save Changes"**

**⚠️ Important :** Le service va redémarrer automatiquement après sauvegarde.

---

## 📋 Étape 4 : Redéploiement

Après avoir ajouté les variables d'environnement :

1. Render redémarre automatiquement ✅
2. Attendre 1-2 minutes
3. Vérifier les logs (onglet "Logs")

**Logs attendus :**
```
Starting service...
Server running on port 10000
```

Pas d'erreur → ✅ Configuration réussie

---

## 🧪 Tests

### Test 1 : Créer un lien Wesser

```bash
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Wesser",
    "email": "test@wesser.fr",
    "campaign": "wesser-recrutement.fr",
    "destination_url": "https://google.com"
  }'
```

**Résultat attendu :**
```json
{
  "success": true,
  "short_url": "https://wesser-recrutement.fr/c/AbC123",
  "link_id": "AbC123"
}
```

✅ Le domaine doit être `wesser-recrutement.fr`

### Test 2 : Créer un lien Aura

```bash
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Aura",
    "email": "test@aura.camp",
    "campaign": "aura.camp",
    "destination_url": "https://aura.camp"
  }'
```

**Résultat attendu :**
```json
{
  "success": true,
  "short_url": "https://agence.aura.camp/c/DeF456",
  "link_id": "DeF456"
}
```

✅ Le domaine doit être `agence.aura.camp`

### Test 3 : Tester la redirection

**Tester Wesser :**
```bash
# Ouvrir dans un navigateur
https://wesser-recrutement.fr/c/AbC123
```

→ Doit rediriger vers votre `destination_url` ✅

**Tester Aura :**
```bash
https://agence.aura.camp/c/DeF456
```

→ Doit rediriger vers votre `destination_url` ✅

### Test 4 : Vérifier le tracking

1. Cliquer sur les liens de test
2. Ouvrir le dashboard : `https://votre-app.onrender.com/`
3. Vérifier que les clics sont enregistrés

---

## 🔧 Configuration Clay mise à jour

### Pour Wesser

**Body HTTP API :**
```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "ICP": "{{ICP}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "{{Full URL}}"
}
```

**Résultat :**
- Lien généré : `https://wesser-recrutement.fr/c/XXXXXXXX`
- Professionnel et branded ✅

### Pour Aura

**Body HTTP API :**
```json
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "ICP": "{{ICP}}",
  "campaign": "aura.camp",
  "destination_url": "{{Full URL}}"
}
```

**Résultat :**
- Lien généré : `https://agence.aura.camp/c/XXXXXXXX`

---

## 📊 Logique de sélection du domaine

Le système utilise cette logique :

```python
if 'wesser' in campaign.lower():
    # Utilise WESSER_DOMAIN (wesser-recrutement.fr)
elif 'aura' in campaign.lower():
    # Utilise AURA_DOMAIN (agence.aura.camp)
else:
    # Utilise CUSTOM_DOMAIN (défaut)
```

**Exemples :**

| Campaign | Domaine utilisé |
|----------|----------------|
| `wesser-recrutement.fr` | `wesser-recrutement.fr` |
| `wesser-commercial` | `wesser-recrutement.fr` |
| `aura.camp` | `agence.aura.camp` |
| `aura-b2b` | `agence.aura.camp` |
| `test` | `link-tracker.onrender.com` (défaut) |

---

## 🚨 Troubleshooting

### Erreur : "SSL Certificate not verified"

**Cause :** DNS pas encore propagé ou mal configuré

**Solution :**
1. Vérifier les enregistrements DNS avec `dig wesser-recrutement.fr`
2. Attendre 24h pour propagation DNS
3. Render → Custom Domains → Cliquer "Verify" à nouveau

### Erreur : "Domain not reachable"

**Cause :** DNS ne pointe pas vers Render

**Solution :**
1. Vérifier que le CNAME ou A record pointe vers Render
2. Utiliser `nslookup wesser-recrutement.fr` pour vérifier
3. Corriger les DNS si nécessaire

### Les liens utilisent encore l'ancien domaine

**Cause :** Variables d'environnement pas prises en compte

**Solution :**
1. Vérifier dans Render → Environment que `WESSER_DOMAIN` existe
2. Redémarrer manuellement le service
3. Vérifier les logs pour confirmer le démarrage

### La redirection ne fonctionne pas

**Cause :** Render ne route pas vers votre app pour ce domaine

**Solution :**
1. Vérifier que le domaine est bien ajouté dans "Custom Domains"
2. Vérifier que le statut est "Verified"
3. Tester avec curl : `curl -I https://wesser-recrutement.fr/c/test`

---

## ✅ Checklist de configuration

### DNS
- [ ] A ou CNAME ajouté pour wesser-recrutement.fr
- [ ] DNS propagé (vérifier avec `dig` ou `nslookup`)

### Render - Custom Domains
- [ ] wesser-recrutement.fr ajouté
- [ ] Statut : Verified
- [ ] SSL Certificate : Issued

### Render - Environment Variables
- [ ] WESSER_DOMAIN = wesser-recrutement.fr
- [ ] AURA_DOMAIN = agence.aura.camp
- [ ] CUSTOM_DOMAIN = link-tracker.onrender.com (ou autre)

### Code déployé
- [ ] Dernière version avec support multi-domains
- [ ] Service redémarré
- [ ] Pas d'erreur dans les logs

### Tests
- [ ] Lien Wesser généré avec wesser-recrutement.fr
- [ ] Lien Aura généré avec agence.aura.camp
- [ ] Redirections fonctionnent
- [ ] Tracking enregistre les clics

---

## 🎯 Avantages

**Avant :**
```
https://link-tracker-abc123.onrender.com/c/XyZ789
```
❌ Pas professionnel
❌ Pas de branding

**Après :**
```
https://wesser-recrutement.fr/c/XyZ789
https://agence.aura.camp/c/XyZ789
```
✅ Professionnel
✅ Branded
✅ Confiance augmentée
✅ Meilleur taux de clic

---

## 📞 Support

**Documentation Render :**
https://render.com/docs/custom-domains

**Vérifier la propagation DNS :**
- https://dnschecker.org/
- https://www.whatsmydns.net/

**En cas de problème :**
1. Vérifier les logs Render
2. Tester avec curl
3. Vérifier les variables d'environnement
4. Contacter le support Render si nécessaire

---

**Date :** 14 novembre 2025
**Version :** 2.1 - Multi-domain support
