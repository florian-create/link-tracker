# ⚡ Migration ICP - Ultra Simple (2 minutes)

## Option 1 : Render Shell (Le plus simple)

### Étape 1 : Ouvrir le Shell
1. Aller sur https://dashboard.render.com
2. Cliquer sur **"link-tracker"** (votre service)
3. Cliquer sur **"Shell"** (bouton en haut à droite)

### Étape 2 : Copier-coller cette commande

```bash
python3 migrate_add_icp.py
```

### Étape 3 : Répondre "yes"

```
Continue? (yes/no): yes
```

### ✅ C'est tout !

Le service va redémarrer automatiquement et l'erreur sera résolue.

---

## Option 2 : SQL Direct (Si Shell ne marche pas)

### Étape 1 : Copier le SQL

Ouvrir le fichier `MIGRATION_SQL.sql` et copier tout le contenu.

### Étape 2 : Aller dans Render Database

1. Dashboard Render → Cliquer sur **"link-tracker-db"** (votre database)
2. Scroller en bas jusqu'à **"Connect"**
3. Cliquer sur **"Postgres.app"** ou copier l'**External Database URL**

### Étape 3 : Ouvrir psql

Dans votre terminal Mac :

```bash
# Remplacer par votre External Database URL
psql "postgres://unipile_auth_db_user:VOTRE_PASSWORD@dpg-xxx.oregon-postgres.render.com/unipile_auth_db"
```

### Étape 4 : Coller le SQL

Copier tout le contenu de `MIGRATION_SQL.sql` et le coller dans psql.

Appuyer sur Entrée.

### Étape 5 : Vérifier

Vous devriez voir :

```
NOTICE:  Colonne ICP ajoutée avec succès
 total_rows_before
-------------------
              1234
(1 row)

 total_rows_after
------------------
             1234
(1 row)

 column_name | data_type
-------------+-----------
 icp         | character varying
(1 row)

       status          | total_links | links_with_icp | links_without_icp
-----------------------+-------------+----------------+-------------------
 Migration terminée ✅ |        1234 |              0 |              1234
(1 row)
```

### Étape 6 : Quitter

```bash
\q
```

### Étape 7 : Redémarrer l'app Render

1. Retour sur dashboard.render.com
2. Cliquer sur "link-tracker"
3. Cliquer **"Manual Deploy"** → **"Deploy latest commit"**

---

## ✅ Vérification

Une fois la migration faite :

1. Ouvrir `https://votre-app.onrender.com/`
2. Le dashboard doit charger sans erreur
3. Le graphique camembert ICP apparaît (vide pour l'instant)
4. La colonne ICP apparaît dans le tableau (avec "Non défini" pour les anciens liens)

---

## 🧪 Test rapide

```bash
# Créer un lien de test avec ICP
curl -X POST https://votre-app.onrender.com/api/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "ICP",
    "email": "test@icp.com",
    "ICP": "CEO",
    "campaign": "test",
    "destination_url": "https://google.com"
  }'
```

Résultat attendu : `{"success":true,"short_url":"...","link_id":"..."}`

---

## 🚨 Si ça ne marche toujours pas

Envoyez-moi les logs Render (dernières 50 lignes) et je vous aide à débugger.

---

**Temps estimé :** 2 minutes avec Option 1, 5 minutes avec Option 2
