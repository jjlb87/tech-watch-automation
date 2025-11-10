#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration
Exécutez ce script en local avant de déployer sur GitHub Actions
"""

import os
import sys

def check_env_var(var_name, required=True):
    """Vérifie qu'une variable d'environnement existe"""
    value = os.getenv(var_name)
    if value:
        print(f"✅ {var_name}: Défini")
        # Masquer les valeurs sensibles
        if "KEY" in var_name or "PASSWORD" in var_name:
            print(f"   Valeur: {value[:10]}...{value[-5:]}")
        else:
            print(f"   Valeur: {value}")
        return True
    else:
        if required:
            print(f"❌ {var_name}: NON DÉFINI (REQUIS)")
        else:
            print(f"⚠️  {var_name}: Non défini (optionnel)")
        return not required

def test_notion_connection():
    """Teste la connexion à l'API Notion"""
    import requests
    
    api_key = os.getenv('NOTION_API_KEY')
    if not api_key:
        print("\n❌ NOTION_API_KEY non définie, impossible de tester")
        return False
    
    print("\n🔗 Test de connexion Notion...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
        if response.status_code == 200:
            print("✅ Connexion Notion réussie!")
            user = response.json()
            print(f"   Workspace: {user.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur Notion: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_rss_feeds():
    """Teste la récupération d'un flux RSS"""
    import feedparser
    
    print("\n📡 Test de récupération RSS...")
    test_feed = "https://dev.to/feed"
    
    try:
        feed = feedparser.parse(test_feed)
        if feed.entries:
            print(f"✅ RSS fonctionnel!")
            print(f"   Premier article: {feed.entries[0].title}")
            return True
        else:
            print("⚠️  Flux RSS vide")
            return False
    except Exception as e:
        print(f"❌ Erreur RSS: {e}")
        return False

def test_email_config():
    """Vérifie la configuration email"""
    print("\n📧 Test de configuration email...")
    
    required_vars = ['EMAIL_FROM', 'EMAIL_TO', 'EMAIL_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    all_ok = True
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ {var} non défini")
            all_ok = False
    
    if all_ok:
        print("✅ Configuration email complète")
        print("   Note: Test d'envoi non effectué (lancez le script principal pour tester)")
    
    return all_ok

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🧪 TESTS DE CONFIGURATION - VEILLE TECHNOLOGIQUE")
    print("=" * 60)
    
    print("\n1️⃣  VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT")
    print("-" * 60)
    
    env_vars_ok = True
    env_vars_ok &= check_env_var('NOTION_API_KEY', required=True)
    env_vars_ok &= check_env_var('EMAIL_FROM', required=True)
    env_vars_ok &= check_env_var('EMAIL_TO', required=True)
    env_vars_ok &= check_env_var('EMAIL_PASSWORD', required=True)
    env_vars_ok &= check_env_var('SMTP_SERVER', required=False)
    env_vars_ok &= check_env_var('SMTP_PORT', required=False)
    
    print("\n2️⃣  VÉRIFICATION DES DÉPENDANCES")
    print("-" * 60)
    
    deps_ok = True
    try:
        import feedparser
        print("✅ feedparser installé")
    except ImportError:
        print("❌ feedparser non installé: pip install feedparser")
        deps_ok = False
    
    try:
        import requests
        print("✅ requests installé")
    except ImportError:
        print("❌ requests non installé: pip install requests")
        deps_ok = False
    
    if not deps_ok:
        print("\n⚠️  Installez les dépendances: pip install -r requirements.txt")
        return False
    
    print("\n3️⃣  TESTS DE CONNEXION")
    print("-" * 60)
    
    notion_ok = test_notion_connection()
    rss_ok = test_rss_feeds()
    email_ok = test_email_config()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    all_tests = [
        ("Variables d'environnement", env_vars_ok),
        ("Dépendances Python", deps_ok),
        ("Connexion Notion", notion_ok),
        ("Flux RSS", rss_ok),
        ("Configuration Email", email_ok),
    ]
    
    for test_name, result in all_tests:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    all_ok = all(result for _, result in all_tests)
    
    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("Vous pouvez maintenant:")
        print("  1. Exécuter tech_watch_automation.py en local")
        print("  2. Déployer sur GitHub Actions")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("Corrigez les erreurs avant de continuer")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
