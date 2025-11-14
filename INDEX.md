# 📚 Link Tracker - Index de la Documentation

Navigation rapide vers tous les guides et fichiers importants.

---

## 🚀 Pour démarrer (ordre recommandé)

1. **[README.md](./README.md)** - Vue d'ensemble du projet
2. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Déployer sur Render (si pas encore fait)
3. **[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)** - ⚡ Configuration Wesser en 5 min

---

## 🎨 Configuration Clay

### Guide rapide (recommandé)
- **[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)** - Configuration en 5 minutes avec copy/paste

### Guide détaillé
- **[CLAY_WESSER_CONFIG.md](./CLAY_WESSER_CONFIG.md)** - Guide complet pas à pas avec screenshots textuels
- **[CLAY_VISUAL_GUIDE.txt](./CLAY_VISUAL_GUIDE.txt)** - Représentation visuelle ASCII de l'interface Clay

### Guide original (Aura)
- **[CLAY_INTEGRATION.md](./CLAY_INTEGRATION.md)** - Intégration Clay originale pour aura.camp

### Exemples prêts à l'emploi
- **[clay_config_example.json](./clay_config_example.json)** - Configurations JSON copy/paste

---

## 📖 Documentation technique

- **[API.md](./API.md)** - Documentation complète de l'API REST
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Déploiement sur Render avec PostgreSQL
- **[WESSER_SETUP.md](./WESSER_SETUP.md)** - Setup complet multi-domaine pour Wesser

---

## 🔗 Références rapides

- **[URLS_IMPORTANTES.md](./URLS_IMPORTANTES.md)** - Toutes les URLs, configs, et commandes utiles
  - URLs dashboard et API
  - Configurations Clay copy/paste
  - Tests rapides
  - Troubleshooting
  - Checklist de vérification

---

## 🧪 Tests et Scripts

- **[test_multi_campaign.py](./test_multi_campaign.py)** - Script de test automatisé pour les deux campagnes
  ```bash
  python3 test_multi_campaign.py
  ```

---

## 📁 Structure complète du projet

```
link-tracker/
├── 📖 Documentation
│   ├── README.md                   # Vue d'ensemble
│   ├── INDEX.md                    # Ce fichier (navigation)
│   ├── DEPLOYMENT.md               # Déploiement Render
│   ├── API.md                      # Documentation API
│   ├── WESSER_SETUP.md             # Setup Wesser complet
│   ├── URLS_IMPORTANTES.md         # Aide-mémoire URLs et configs
│   │
│   ├── 🎨 Guides Clay
│   │   ├── QUICK_START_WESSER.md         # Quick start 5 min
│   │   ├── CLAY_WESSER_CONFIG.md         # Guide détaillé Wesser
│   │   ├── CLAY_VISUAL_GUIDE.txt         # Guide visuel ASCII
│   │   ├── CLAY_INTEGRATION.md           # Guide original Aura
│   │   └── clay_config_example.json      # Exemples JSON
│   │
│   └── 🧪 Scripts de test
│       └── test_multi_campaign.py        # Tests automatisés
│
├── 🔧 Code source
│   ├── app.py                      # Application Flask principale
│   ├── init_db.py                  # Initialisation base de données
│   ├── dashboard_corporate.html    # Dashboard analytics
│   └── requirements.txt            # Dépendances Python
│
└── ⚙️ Configuration
    ├── render.yaml                 # Config auto-deploy Render
    ├── runtime.txt                 # Version Python
    └── .gitignore                  # Fichiers ignorés Git
```

---

## 🎯 Guides par cas d'usage

### Je veux démarrer rapidement avec Wesser
→ **[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)**

### Je veux comprendre comment tout fonctionne
→ **[README.md](./README.md)** puis **[CLAY_WESSER_CONFIG.md](./CLAY_WESSER_CONFIG.md)**

### Je veux déployer le link tracker
→ **[DEPLOYMENT.md](./DEPLOYMENT.md)**

### J'ai un problème technique
→ **[URLS_IMPORTANTES.md](./URLS_IMPORTANTES.md)** section "Troubleshooting"

### Je veux tester que tout fonctionne
→ Lancer `python3 test_multi_campaign.py`

### Je veux voir la documentation API
→ **[API.md](./API.md)**

### Je veux configurer plusieurs campagnes
→ **[WESSER_SETUP.md](./WESSER_SETUP.md)** section "Cas d'usage avancés"

---

## 📊 Workflows typiques

### Workflow 1 : Première installation

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Déployer sur Render
2. **[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)** - Configurer Clay
3. Lancer `test_multi_campaign.py` - Tester le système
4. Envoyer premiers messages

### Workflow 2 : Nouvelle campagne Wesser

1. **[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)** - Copier config Clay
2. Créer table Clay avec prospects
3. Configurer HTTP API
4. Envoyer messages
5. Suivre dans dashboard (filtre "wesser-recrutement.fr")

### Workflow 3 : Analyse des résultats

1. Ouvrir dashboard (voir **[URLS_IMPORTANTES.md](./URLS_IMPORTANTES.md)**)
2. Filtrer par campagne
3. Identifier hot leads (2+ clics)
4. Exporter CSV
5. Relancer prospects intéressés

---

## 🔑 Concepts clés

### Multi-campagne
Le système supporte nativement plusieurs campagnes via le champ `campaign` dans l'API.
- `aura.camp` pour les campagnes Aura
- `wesser-recrutement.fr` pour les campagnes Wesser
- Possibilité d'ajouter d'autres campagnes à volonté

### Liens trackés
Chaque prospect reçoit un lien unique (format: `https://app.onrender.com/c/AbC123`)
qui redirige vers votre landing page tout en enregistrant le clic.

### Dashboard filtré
Le dashboard permet de filtrer les statistiques par campagne pour analyser
les performances de chaque campagne séparément.

---

## ⚡ Commandes essentielles

### Tester le système
```bash
cd /Users/florian/Desktop/link-tracker
python3 test_multi_campaign.py
```

### Voir les fichiers du projet
```bash
ls -la /Users/florian/Desktop/link-tracker/
```

### Pousser modifications sur GitHub
```bash
cd /Users/florian/Desktop/link-tracker
git add .
git commit -m "Description"
git push
```

---

## 📞 Ressources externes

- **Render Dashboard:** https://dashboard.render.com
- **Clay App:** https://clay.com
- **GitHub Repo:** https://github.com/florian-create/link-tracker

---

## ✅ Checklist pour lancer Wesser

- [ ] Link tracker déployé sur Render (**[DEPLOYMENT.md](./DEPLOYMENT.md)**)
- [ ] Table Clay créée avec prospects
- [ ] HTTP API configuré (**[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)**)
- [ ] Test réussi (1 prospect)
- [ ] Dashboard affiche la campagne "wesser-recrutement.fr"
- [ ] Messages prêts avec `{{Wesser Tracking Link}}`
- [ ] Test batch 5-10 prospects
- [ ] Lancement campagne complète
- [ ] Suivi quotidien dans dashboard

---

## 🎉 Prêt à démarrer !

**Prochaines étapes recommandées :**

1. ⚡ Lire **[QUICK_START_WESSER.md](./QUICK_START_WESSER.md)** (5 minutes)
2. 🎨 Configurer Clay avec la config copy/paste
3. 🧪 Tester avec `python3 test_multi_campaign.py`
4. 🚀 Lancer votre première campagne Wesser

---

**Dernière mise à jour :** 14 novembre 2025
**Version :** 2.0 (Multi-campagne Aura + Wesser)
