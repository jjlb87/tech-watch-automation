# 🚀 Démarrage Rapide - 5 minutes

## Étape 1 : Récupérer les fichiers (1 min)

Téléchargez ou clonez ce projet sur votre machine.

## Étape 2 : Créer un dépôt GitHub (2 min)

1. Allez sur https://github.com/new
2. Nom : `tech-watch-automation`
3. Type : Private
4. Créez et uploadez tous les fichiers

## Étape 3 : Configurer Notion (3 min)

### 3.1 Créer l'intégration
1. https://www.notion.so/my-integrations
2. "+ New integration"
3. Nom : "Tech Watch Bot"
4. Copiez la clé API (commence par `secret_`)

### 3.2 Connecter la base
1. Ouvrez votre base "📚 Veille Technologique Hebdomadaire"
2. Menu "..." → "Add connections" → "Tech Watch Bot"

## Étape 4 : Configurer Gmail (2 min)

1. https://myaccount.google.com/apppasswords
2. Créez "Tech Watch Bot"
3. Copiez le mot de passe (16 caractères)

## Étape 5 : Ajouter les secrets GitHub (3 min)

Dans votre dépôt GitHub → **Settings** → **Secrets** → **Actions** :

```
NOTION_API_KEY      → secret_abc123...
EMAIL_FROM          → votre@gmail.com
EMAIL_TO            → votre@gmail.com
EMAIL_PASSWORD      → abcd efgh ijkl mnop
SMTP_SERVER         → smtp.gmail.com
SMTP_PORT           → 587
```

## Étape 6 : Tester ! (1 min)

1. GitHub → **Actions** → "Veille Technologique"
2. "Run workflow" → "Run workflow"
3. Attendez 2 minutes
4. Vérifiez Notion et vos emails !

## ✅ C'est terminé !

Chaque lundi à 9h, vous recevrez automatiquement :
- ✉️ Un email avec les nouveaux articles
- 📚 Les articles ajoutés dans Notion

---

## 🆘 Problème ?

**Les articles n'apparaissent pas** → Vérifiez que l'intégration est connectée à la base

**Pas d'email** → Vérifiez l'App Password Gmail et les secrets

**Erreur GitHub** → Actions → Logs pour voir l'erreur détaillée

---

📖 Guide complet : Voir **README.md**
