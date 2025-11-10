# 🚀 Veille Technologique Automatisée - Guide d'Installation

Système automatisé de veille technologique qui :
- ✅ Collecte automatiquement des articles depuis des flux RSS
- ✅ Les ajoute à votre base Notion
- ✅ Vous envoie un email récapitulatif chaque lundi matin à 9h
- ✅ Totalement GRATUIT via GitHub Actions

## 📋 Prérequis

1. Un compte GitHub (gratuit)
2. Un compte Notion avec la base "📚 Veille Technologique Hebdomadaire" créée
3. Une adresse Gmail (ou autre SMTP)

## 🔧 Installation (15 minutes)

### Étape 1 : Créer un dépôt GitHub

1. Allez sur https://github.com/new
2. Nommez votre dépôt : `tech-watch-automation`
3. Cochez "Private" (recommandé)
4. Cliquez sur "Create repository"

### Étape 2 : Uploader les fichiers

Dans votre nouveau dépôt, cliquez sur "Add file" > "Upload files" et uploadez :
- `tech_watch_automation.py`
- `requirements.txt`
- `.github/workflows/tech-watch.yml`

Ou en ligne de commande :
```bash
git clone https://github.com/VOTRE_USERNAME/tech-watch-automation.git
cd tech-watch-automation
# Copiez les 3 fichiers ici
git add .
git commit -m "Initial setup"
git push
```

### Étape 3 : Obtenir votre clé API Notion

1. Allez sur https://www.notion.so/my-integrations
2. Cliquez sur "+ New integration"
3. Nommez-la "Tech Watch Bot"
4. Sélectionnez votre workspace
5. Dans "Capabilities", cochez :
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
6. Cliquez sur "Submit"
7. **COPIEZ LA CLÉ API** (commence par `secret_...`)

### Étape 4 : Connecter Notion à l'intégration

1. Ouvrez votre base "📚 Veille Technologique Hebdomadaire" dans Notion
2. Cliquez sur les "..." en haut à droite
3. Sélectionnez "Add connections"
4. Cherchez "Tech Watch Bot" et ajoutez-le

### Étape 5 : Configurer Gmail pour les emails

#### Option A : App Password Gmail (RECOMMANDÉ)

1. Allez sur https://myaccount.google.com/security
2. Activez la validation en 2 étapes (si pas déjà fait)
3. Cherchez "App passwords" ou allez sur https://myaccount.google.com/apppasswords
4. Créez un nouveau mot de passe d'application :
   - Nom : "Tech Watch Bot"
   - **COPIEZ LE MOT DE PASSE** (16 caractères)

#### Option B : Autre fournisseur email

Si vous utilisez un autre service (Outlook, etc.), vous aurez besoin :
- Serveur SMTP (ex: smtp.office365.com)
- Port SMTP (souvent 587)
- Votre email et mot de passe

### Étape 6 : Configurer les Secrets GitHub

1. Dans votre dépôt GitHub, allez dans **Settings** > **Secrets and variables** > **Actions**
2. Cliquez sur "New repository secret" et ajoutez ces secrets un par un :

| Nom du Secret | Valeur | Exemple |
|---------------|--------|---------|
| `NOTION_API_KEY` | Votre clé API Notion | `secret_abcd1234...` |
| `EMAIL_FROM` | Votre adresse Gmail | `votre.email@gmail.com` |
| `EMAIL_TO` | Adresse destinataire | `votre.email@gmail.com` |
| `EMAIL_PASSWORD` | App Password Gmail (16 car.) | `abcd efgh ijkl mnop` |
| `SMTP_SERVER` | Serveur SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP | `587` |

⚠️ **IMPORTANT** : Ne partagez JAMAIS ces secrets avec personne !

### Étape 7 : Tester l'installation

1. Dans GitHub, allez dans **Actions**
2. Cliquez sur "Veille Technologique Automatisée" (à gauche)
3. Cliquez sur "Run workflow" (bouton à droite)
4. Cliquez sur "Run workflow" (confirmation)
5. Attendez 1-2 minutes
6. Vérifiez :
   - ✅ Des articles sont apparus dans votre Notion
   - ✅ Vous avez reçu un email récapitulatif

## 📅 Planification Automatique

Le script s'exécutera automatiquement **chaque lundi à 9h00** (heure de Paris).

Pour changer l'horaire, modifiez la ligne `cron` dans `.github/workflows/tech-watch.yml` :
```yaml
schedule:
  - cron: '0 7 * * 1'  # Format: minute heure jour mois jour_semaine
```

Exemples :
- `0 7 * * 1` = Lundi 9h (Paris)
- `0 8 * * 1` = Lundi 10h (Paris)
- `0 7 * * 1,4` = Lundi et jeudi 9h
- `0 7 * * *` = Tous les jours à 9h

Outil pour générer des cron : https://crontab.guru/

## 🎯 Personnalisation

### Modifier les sources RSS

Éditez `tech_watch_automation.py` et modifiez le dictionnaire `RSS_FEEDS` :

```python
RSS_FEEDS = {
    "Full Stack": [
        "https://dev.to/feed",
        "VOTRE_FLUX_RSS_ICI",
    ],
    # ... autres catégories
}
```

### Ajouter une nouvelle catégorie

1. Dans Notion, ajoutez l'option dans la propriété "Catégorie"
2. Dans le script, ajoutez la catégorie dans `RSS_FEEDS`

### Modifier le nombre d'articles collectés

Dans `tech_watch_automation.py`, ligne ~57 :
```python
for entry in feed.entries[:5]:  # Changez 5 par le nombre souhaité
```

## 🐛 Dépannage

### Les articles n'apparaissent pas dans Notion

1. Vérifiez que l'intégration est connectée à la base de données
2. Vérifiez que `NOTION_API_KEY` est correct dans les secrets GitHub
3. Regardez les logs dans Actions pour voir les erreurs

### Je ne reçois pas d'email

1. Vérifiez que vous avez bien créé un "App Password" Gmail
2. Vérifiez les secrets `EMAIL_FROM`, `EMAIL_TO`, `EMAIL_PASSWORD`
3. Pour Gmail, le port doit être `587` et le serveur `smtp.gmail.com`

### Le workflow ne s'exécute pas

1. Vérifiez que le fichier `.github/workflows/tech-watch.yml` est bien dans ce dossier
2. Les Actions doivent être activées dans Settings > Actions
3. Le cron peut prendre jusqu'à 1h pour se déclencher la première fois

### Voir les logs d'exécution

1. Allez dans Actions
2. Cliquez sur l'exécution
3. Cliquez sur "tech-watch"
4. Consultez les logs détaillés

## 📊 Utilisation de la Base Notion

Votre base contient ces propriétés :

- **Titre** : Titre de l'article
- **Catégorie** : Full Stack, IA/ML, Cloud, DevSecOps
- **Source** : Site web d'origine
- **URL** : Lien vers l'article
- **Date Ajout** : Date d'ajout automatique
- **Priorité** : 🔥 Haute / ⚡ Moyenne / 📌 Basse (modifiable manuellement)
- **Statut** : 📥 À lire / 👀 En cours / ✅ Lu / ⭐ Favoris (modifiable manuellement)
- **Résumé** : Court résumé de l'article

### Vues recommandées dans Notion

Créez des vues filtrées :
1. **À lire cette semaine** : Statut = "📥 À lire", Date Ajout = Cette semaine
2. **Par priorité** : Triées par Priorité décroissante
3. **Favoris** : Statut = "⭐ Favoris"
4. **Par catégorie** : Groupées par Catégorie

## 🔄 Mises à jour

Pour mettre à jour le script :
1. Modifiez les fichiers localement
2. Commitez et poussez sur GitHub :
```bash
git add .
git commit -m "Update RSS feeds"
git push
```

## 💡 Améliorations Futures

Idées pour étendre le système :
- [ ] Ajouter des filtres par mots-clés
- [ ] Intégration avec des APIs (HackerNews, Reddit)
- [ ] Résumés automatiques avec IA
- [ ] Statistiques de lecture
- [ ] Partage sur Slack/Discord

## 📚 Ressources

- [Documentation Notion API](https://developers.notion.com/)
- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Feedparser Documentation](https://feedparser.readthedocs.io/)

## ❓ Support

Des questions ? Vous pouvez :
1. Consulter les logs d'exécution dans GitHub Actions
2. Vérifier que tous les secrets sont bien configurés
3. Tester manuellement avec "Run workflow"

---

✨ **Félicitations !** Votre système de veille est maintenant opérationnel et totalement automatisé !

Vous recevrez désormais chaque lundi matin un email avec les derniers articles tech, automatiquement ajoutés à votre Notion.
