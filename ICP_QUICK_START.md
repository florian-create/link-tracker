# ⚡ ICP Feature - Quick Start

Guide ultra-rapide pour activer et utiliser la feature ICP.

---

## 🚀 Activation (3 étapes)

### 1. Migrer la base de données

```bash
cd /Users/florian/Desktop/link-tracker
python3 migrate_add_icp.py
# Répondre 'yes' quand demandé
```

**Durée :** 10 secondes
**Sécurité :** ✅ Aucune donnée supprimée

---

### 2. Redéployer sur Render

**Option A - Auto (si push GitHub détecté par Render) :**
→ Render redéploie automatiquement ✅

**Option B - Manuel :**
1. Aller sur [dashboard.render.com](https://dashboard.render.com)
2. Cliquer sur votre service "link-tracker"
3. Cliquer **"Manual Deploy"** → **"Deploy latest commit"**

**Durée :** 2-3 minutes

---

### 3. Configurer Clay

**Ajouter le champ ICP au body JSON :**

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

**Créer une colonne ICP dans Clay :**

Option 1 - Manuelle : Taper directement le profil (CEO, CTO, etc.)

Option 2 - Formule : Déduire du job_title
```javascript
IF(CONTAINS({{job_title}}, "CEO"), "CEO",
IF(CONTAINS({{job_title}}, "CTO"), "CTO",
IF(CONTAINS({{job_title}}, "Commercial"), "Commercial",
"Other")))
```

---

## 📊 Résultat dans le Dashboard

**Vous verrez :**

1. **Graphique camembert** (à droite du Sankey)
   - Distribution des ICPs qui ont cliqué
   - Couleurs rose → bordeaux
   - Filtrable par campagne et période

2. **Colonne ICP** dans le tableau
   - Affiche l'ICP de chaque prospect
   - "Non défini" si pas renseigné

3. **Export CSV** avec ICP
   - Colonne ICP incluse

---

## 🧪 Test rapide

```bash
# Créer un lien de test avec ICP
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "ICP": "CEO",
    "campaign": "test",
    "destination_url": "https://google.com"
  }'

# Cliquer sur le lien retourné

# Vérifier le graphique ICP dans le dashboard
# → Vous devriez voir "CEO: 1 (100%)"
```

---

## 💡 Exemples de valeurs ICP

**Wesser :**
- Commercial Senior
- Manager Commercial
- Directeur Regional
- Chef d'Équipe

**Aura (B2B SaaS) :**
- CEO
- CTO
- VP Sales
- Head of Marketing

**Adaptez selon votre segmentation !**

---

## 📞 Support

**Problème ?**
- Lire la doc complète : [ICP_FEATURE.md](./ICP_FEATURE.md)
- Vérifier les logs Render
- Tester l'endpoint : `GET /api/icp-stats`

---

**🎉 C'est prêt ! Vos ICPs sont maintenant trackés.**

**Documentation complète :** [ICP_FEATURE.md](./ICP_FEATURE.md)
