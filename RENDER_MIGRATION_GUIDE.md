# 🚀 Migration ICP sur Render - Guide

Votre base de données sur Render n'a pas encore la colonne `icp`. Voici comment la migrer.

---

## Option 1 : Migration via Render Shell (Recommandé)

### Étape 1 : Ouvrir le Shell Render

1. Aller sur [dashboard.render.com](https://dashboard.render.com)
2. Cliquer sur votre service **"link-tracker"**
3. En haut à droite, cliquer sur **"Shell"**

### Étape 2 : Lancer la migration

Dans le shell Render, taper :

```bash
python3 migrate_add_icp.py
```

Quand demandé, répondre : `yes`

**Résultat attendu :**
```
🔧 Migration: Add ICP column to links table
📅 Date: 2025-11-14 21:05:00
============================================================

⚠️  This script will add the 'icp' column to the links table
   Existing data will NOT be affected
   The column will allow NULL values by default

Continue? (yes/no): yes

📋 Checking if ICP column exists...
🔄 Adding ICP column to links table...
   Rows before migration: 1234
✅ Migration successful - all 1234 rows preserved

============================================================
✅ Migration completed successfully!
============================================================
```

### Étape 3 : Redémarrer l'application

Le redémarrage se fait automatiquement, mais vous pouvez forcer :
1. Cliquer sur **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## Option 2 : Migration manuelle via SQL

Si le shell ne fonctionne pas, vous pouvez exécuter la migration SQL directement.

### Étape 1 : Ouvrir la console PostgreSQL

1. Dashboard Render → Cliquer sur votre **database "link-tracker-db"**
2. Copier l'**External Database URL** (commence par `postgres://...`)

### Étape 2 : Se connecter avec psql

Dans votre terminal local :

```bash
# Remplacer par votre External Database URL
psql "votre-database-url-ici"
```

### Étape 3 : Vérifier si la colonne existe

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'links' AND column_name = 'icp';
```

Si vide → Continuer

### Étape 4 : Ajouter la colonne

```sql
-- Compter avant
SELECT COUNT(*) FROM links;

-- Ajouter la colonne
ALTER TABLE links ADD COLUMN icp VARCHAR(255);

-- Vérifier après
SELECT COUNT(*) FROM links;

-- Les deux nombres doivent être identiques ✅
```

### Étape 5 : Vérifier

```sql
-- Voir la structure de la table
\d links

-- Devrait afficher :
-- ...
-- icp | character varying(255) |
-- ...
```

### Étape 6 : Quitter

```sql
\q
```

---

## Option 3 : Via l'init_db (Auto)

La colonne `icp` est déjà dans le code `init_db()` dans `app.py`. Mais PostgreSQL ne modifie pas les tables existantes avec `CREATE TABLE IF NOT EXISTS`.

**Solution :** Forcer la recréation (⚠️ PERTE DE DONNÉES) :

```bash
# NE PAS FAIRE si vous avez des données importantes !
# Supprimer et recréer la table
DROP TABLE clicks;
DROP TABLE links;
# Puis redémarrer l'app
```

**❌ Non recommandé** - Utilisez Option 1 ou 2 à la place

---

## ✅ Vérification post-migration

### Test 1 : Dashboard charge sans erreur

1. Ouvrir `https://votre-app.onrender.com/`
2. Pas d'erreur dans la console
3. Camembert ICP visible (peut être vide)

### Test 2 : API fonctionne

```bash
# Tester l'endpoint ICP
curl https://votre-app.onrender.com/api/icp-stats

# Résultat attendu (peut être vide) :
[]
# ou avec données :
[{"icp":"CEO","click_count":5}]
```

### Test 3 : Créer un lien avec ICP

```bash
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Migration",
    "email": "test@migration.com",
    "ICP": "CEO",
    "campaign": "test",
    "destination_url": "https://google.com"
  }'

# Résultat attendu :
{
  "success": true,
  "short_url": "https://...",
  "link_id": "..."
}
```

### Test 4 : Vérifier dans le tableau

1. Dashboard → Tableau des clics
2. Colonne "ICP" doit apparaître
3. Les anciens liens auront "Non défini"
4. Le nouveau lien de test aura "CEO"

---

## 🚨 Troubleshooting

### Erreur : "permission denied"

**Cause :** Vous n'avez pas les droits sur la base

**Solution :** Utiliser l'option 1 (Shell Render) qui utilise les bonnes credentials

### Erreur : "relation links does not exist"

**Cause :** La table n'existe pas encore

**Solution :** L'app doit d'abord créer les tables. Redémarrez l'app, puis relancez la migration

### L'app redémarre en boucle

**Cause :** Erreur dans le code

**Solution :**
1. Vérifier les logs Render
2. Vérifier que `app.py` a bien été déployé avec les modifications ICP
3. Redéployer si nécessaire

### La colonne existe déjà

```
ERROR: column "icp" of relation "links" already exists
```

**Solution :** C'est bon ! La migration a déjà été faite. Ignorez l'erreur.

---

## 📞 Support

Si aucune option ne fonctionne :

1. **Vérifier le code déployé** :
   - Sur Render, regarder les logs de build
   - Vérifier que le dernier commit inclut les modifs ICP

2. **Forcer le redéploiement** :
   - Dashboard Render → Manual Deploy → Clear build cache & deploy

3. **Vérifier la DATABASE_URL** :
   - Render → Environment → DATABASE_URL doit pointer vers la bonne DB

---

**Étapes suivantes après migration :**
1. ✅ Migration réussie
2. Dashboard fonctionne
3. Configurer Clay avec ICP
4. Créer des liens avec ICP
5. Analyser les résultats

---

**Date :** 14 novembre 2025
**Action requise :** Lancer la migration ICP sur Render
