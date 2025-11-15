# 🔐 Système de Backup Automatique

Ce guide explique comment configurer et utiliser le système de backup automatique pour sauvegarder les données du Link Tracker vers Google Drive.

## 📋 Vue d'ensemble

Le système de backup exporte quotidiennement :
- ✅ Table `links` (tous les liens créés)
- ✅ Table `clicks` (tous les clics avec informations enrichies)

Les backups sont au format **CSV** et uploadés automatiquement sur **Google Drive**.

## 🚀 Configuration initiale

### Étape 1 : Créer un compte de service Google

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API Google Drive :
   - Menu → "APIs & Services" → "Library"
   - Cherchez "Google Drive API"
   - Cliquez sur "Enable"

4. Créez un compte de service :
   - Menu → "APIs & Services" → "Credentials"
   - Cliquez sur "Create Credentials" → "Service Account"
   - Donnez un nom : `link-tracker-backup`
   - Cliquez sur "Create and Continue"
   - Role : "Editor" (ou créez un rôle personnalisé)
   - Cliquez sur "Done"

5. Créez une clé JSON :
   - Cliquez sur le compte de service créé
   - Onglet "Keys"
   - "Add Key" → "Create new key"
   - Type : **JSON**
   - Téléchargez le fichier JSON

### Étape 2 : Configurer Google Drive

1. Créez un dossier dédié dans Google Drive pour les backups
   - Exemple : `Link Tracker Backups`

2. Partagez ce dossier avec le compte de service :
   - Clic droit sur le dossier → "Partager"
   - Collez l'email du compte de service (format: `xxx@xxx.iam.gserviceaccount.com`)
   - Donnez les droits "Éditeur"
   - Cliquez sur "Partager"

3. Récupérez l'ID du dossier :
   - Ouvrez le dossier dans Google Drive
   - L'URL ressemble à : `https://drive.google.com/drive/folders/XXXXX`
   - L'ID est la partie `XXXXX` après `/folders/`

### Étape 3 : Configuration des variables d'environnement

#### Sur Render.com :

1. Allez dans votre service Render
2. Onglet "Environment"
3. Ajoutez ces variables :

```bash
GOOGLE_SERVICE_ACCOUNT_JSON=/etc/secrets/service-account.json
GOOGLE_DRIVE_FOLDER_ID=votre_folder_id_google_drive
```

4. Ajoutez le fichier JSON comme "Secret File" :
   - Dans "Environment" → "Secret Files"
   - Filename: `/etc/secrets/service-account.json`
   - Contents: Collez le contenu du fichier JSON téléchargé

#### En local (développement) :

Créez un fichier `.env` :

```bash
DATABASE_URL=postgresql://localhost/link_tracker
GOOGLE_SERVICE_ACCOUNT_JSON=./service-account.json
GOOGLE_DRIVE_FOLDER_ID=votre_folder_id_google_drive
```

Placez votre fichier `service-account.json` à la racine du projet.

⚠️ **IMPORTANT** : Ajoutez ces fichiers au `.gitignore` :
```
.env
service-account.json
```

## 📅 Configuration du backup quotidien

### Option 1 : Cron Job (Render.com)

Render supporte les cron jobs natifs. Modifiez `render.yaml` :

```yaml
services:
  # Service web existant
  - type: web
    name: link-tracker
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: link-tracker-db
          property: connectionString

  # Nouveau cron job pour backup
  - type: cron
    name: link-tracker-backup
    env: python
    schedule: "0 2 * * *"  # Tous les jours à 2h du matin (UTC)
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python backup_to_drive.py"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: link-tracker-db
          property: connectionString
      - key: GOOGLE_SERVICE_ACCOUNT_JSON
        sync: false
      - key: GOOGLE_DRIVE_FOLDER_ID
        sync: false
```

### Option 2 : GitHub Actions

Créez `.github/workflows/backup.yml` :

```yaml
name: Daily Database Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Tous les jours à 2h du matin (UTC)
  workflow_dispatch:  # Permet de lancer manuellement

jobs:
  backup:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Create service account file
        run: |
          echo '${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}' > service-account.json

      - name: Run backup
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GOOGLE_SERVICE_ACCOUNT_JSON: ./service-account.json
          GOOGLE_DRIVE_FOLDER_ID: ${{ secrets.GOOGLE_DRIVE_FOLDER_ID }}
        run: |
          python backup_to_drive.py
```

Ajoutez ces secrets dans GitHub :
- `DATABASE_URL`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_DRIVE_FOLDER_ID`

### Option 3 : Service externe (EasyCron, cron-job.org)

Créez un endpoint API dans `app.py` :

```python
@app.route('/api/backup', methods=['POST'])
def trigger_backup():
    """Endpoint pour déclencher un backup (protégé par clé API)"""
    api_key = request.headers.get('X-API-Key')

    # Vérifier la clé API
    if api_key != os.environ.get('BACKUP_API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Lancer le backup en arrière-plan
        import subprocess
        subprocess.Popen(['python', 'backup_to_drive.py'])
        return jsonify({'success': True, 'message': 'Backup started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Puis configurez un cron externe pour appeler cet endpoint.

## 🧪 Test du backup manuel

### En local :

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export DATABASE_URL="postgresql://localhost/link_tracker"
export GOOGLE_SERVICE_ACCOUNT_JSON="./service-account.json"
export GOOGLE_DRIVE_FOLDER_ID="votre_folder_id"

# Lancer le backup
python backup_to_drive.py
```

### Sur Render :

Vous pouvez déclencher manuellement le cron job depuis le dashboard Render :
1. Allez dans votre service cron
2. Cliquez sur "Trigger Run"

## 📊 Format des fichiers de backup

### `links_backup_YYYYMMDD_HHMMSS.csv`

Colonnes :
- `id` : ID interne
- `link_id` : ID court du lien
- `first_name`, `last_name`, `email` : Informations prospect
- `icp` : Profil client idéal
- `campaign` : Nom de la campagne
- `destination_url` : URL de destination
- `created_at` : Date de création

### `clicks_backup_YYYYMMDD_HHMMSS.csv`

Colonnes :
- `id` : ID du clic
- `link_id` : ID du lien cliqué
- `clicked_at` : Date/heure du clic
- `ip_address` : Adresse IP
- `user_agent` : User agent du navigateur
- `country`, `city` : Géolocalisation
- `referer` : Page d'origine
- `first_name`, `last_name`, `email`, `campaign`, `icp` : Infos du prospect

## 🔄 Restauration depuis un backup

### Restaurer la table `links` :

```bash
# Se connecter à PostgreSQL
psql $DATABASE_URL

# Créer une table temporaire
CREATE TABLE links_restore (LIKE links);

# Copier les données depuis le CSV
\copy links_restore FROM 'links_backup.csv' WITH CSV HEADER;

# Vérifier les données
SELECT COUNT(*) FROM links_restore;

# Restaurer (ATTENTION : Cela écrase les données existantes !)
TRUNCATE links CASCADE;  -- CASCADE supprime aussi les clicks !
INSERT INTO links SELECT * FROM links_restore;

# Nettoyer
DROP TABLE links_restore;
```

### Restaurer la table `clicks` :

```bash
# Créer une table temporaire
CREATE TABLE clicks_restore (
    id SERIAL PRIMARY KEY,
    link_id VARCHAR(10),
    clicked_at TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    country VARCHAR(100),
    city VARCHAR(100),
    referer TEXT
);

# Copier les données (uniquement les colonnes de la table clicks)
\copy clicks_restore(id, link_id, clicked_at, ip_address, user_agent, country, city, referer) FROM 'clicks_backup.csv' WITH CSV HEADER;

# Vérifier
SELECT COUNT(*) FROM clicks_restore;

# Restaurer
TRUNCATE clicks;
INSERT INTO clicks SELECT * FROM clicks_restore;

# Nettoyer
DROP TABLE clicks_restore;
```

## 🔍 Vérification des backups

### Vérifier dans Google Drive :

1. Ouvrez le dossier de backup
2. Vous devriez voir 2 fichiers par jour :
   - `links_backup_20250115_020000.csv`
   - `clicks_backup_20250115_020000.csv`

### Script de vérification automatique :

```python
# verify_backups.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)

service = build('drive', 'v3', credentials=credentials)

# Lister les fichiers du dossier
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    orderBy='createdTime desc',
    fields='files(name, createdTime, size)'
).execute()

for file in results.get('files', []):
    print(f"{file['name']} - {file['createdTime']} - {file['size']} bytes")
```

## 📈 Monitoring et alertes

### Option 1 : Logs Render

Les logs du cron job sont disponibles dans Render Dashboard → Logs

### Option 2 : Alertes par email

Modifiez `backup_to_drive.py` pour envoyer des emails en cas d'erreur :

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    """Envoyer une alerte email en cas d'erreur"""
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = os.environ.get('ALERT_EMAIL_FROM')
    msg['To'] = os.environ.get('ALERT_EMAIL_TO')

    with smtplib.SMTP(os.environ.get('SMTP_SERVER'), 587) as server:
        server.starttls()
        server.login(os.environ.get('SMTP_USER'), os.environ.get('SMTP_PASS'))
        server.send_message(msg)

# Dans la fonction backup_database()
if not backup_successful:
    send_alert(
        "❌ Link Tracker Backup Failed",
        f"Backup failed on {datetime.now()}\nCheck logs for details."
    )
```

## 🔒 Sécurité

- ✅ Ne jamais committer le fichier `service-account.json`
- ✅ Utiliser des variables d'environnement pour les secrets
- ✅ Limiter les permissions du compte de service (accès Drive uniquement)
- ✅ Chiffrer les backups si données sensibles (RGPD)
- ✅ Définir une politique de rétention (ex: garder 30 jours)

## 💡 Conseils

1. **Testez régulièrement la restauration** : Un backup non testé n'est pas un vrai backup !
2. **Gardez plusieurs versions** : Configurez la rétention à 30 jours minimum
3. **Surveillez l'espace Drive** : Les backups peuvent prendre de la place
4. **Documentez les procédures** : En cas de catastrophe, pas le temps de chercher
5. **Backup hors-ligne** : Téléchargez occasionnellement des copies locales

## 🆘 Troubleshooting

### Erreur : "Service account file not found"

✅ Vérifiez que `GOOGLE_SERVICE_ACCOUNT_JSON` pointe vers le bon fichier

### Erreur : "Insufficient Permission"

✅ Vérifiez que le dossier Drive est partagé avec le compte de service
✅ Vérifiez que l'API Drive est activée

### Erreur : "No data found"

✅ Normal si la base de données est vide
✅ Le script créera quand même un fichier vide

### Le cron ne se lance pas

✅ Vérifiez le format du cron : `0 2 * * *`
✅ Vérifiez les logs du service
✅ Testez manuellement le script

## 📞 Support

Pour toute question ou problème :
1. Consultez les logs du backup
2. Vérifiez les permissions Google Drive
3. Testez le script manuellement en local

---

**Dernière mise à jour** : 2025-01-15
