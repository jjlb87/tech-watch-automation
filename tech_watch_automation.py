#!/usr/bin/env python3
"""
Script d'automatisation de veille technologique
Collecte des articles depuis RSS, les ajoute à Notion et envoie un email récapitulatif
"""

import os
import sys
import json
import feedparser
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import List, Dict

# Configuration
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '').strip()
NOTION_DATABASE_ID = "a91dd97aa92b4d239293810d4700bdc8"  # ID de votre base "Veille Technologique Hebdomadaire"
EMAIL_FROM = os.getenv('EMAIL_FROM', '').strip()
EMAIL_TO = os.getenv('EMAIL_TO', '').strip()
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '').strip()
SMTP_SERVER = os.getenv('SMTP_SERVER', '').strip() or 'smtp.gmail.com'

# Gestion sécurisée du port SMTP
smtp_port_str = os.getenv('SMTP_PORT', '587').strip()
if not smtp_port_str:  # Si vide ou None
    smtp_port_str = '587'
try:
    SMTP_PORT = int(smtp_port_str)
except (ValueError, AttributeError, TypeError):
    print("⚠️  SMTP_PORT invalide, utilisation du port par défaut 587")
    SMTP_PORT = 587

# Sources RSS par catégorie et langue
RSS_FEEDS = {
    "Full Stack": {
        "fr": [
            "https://www.blogdumoderateur.com/feed/",
            "https://grafikart.fr/feed",
            "https://korben.info/feed",
            "https://blog.zenika.com/feed/",
        ],
        "en": [
            "https://dev.to/feed",
            "https://web.dev/feed.xml",
        ]
    },
    "IA/ML": {
        "fr": [
            "https://www.actuia.com/feed/",
            "https://www.lemondeinformatique.fr/flux-rss/thematique/intelligence-artificielle/rss.xml",
        ],
        "en": [
            "https://huggingface.co/blog/feed.xml",
            "https://openai.com/blog/rss/",
        ]
    },
    "Cloud": {
        "fr": [
            "https://www.lemagit.fr/rss/Cloud-Computing.xml",
            "https://blog.scaleway.com/fr/feed/",
        ],
        "en": [
            "https://aws.amazon.com/blogs/aws/feed/",
            "https://cloud.google.com/blog/rss",
        ]
    },
    "DevSecOps": {
        "fr": [
            "https://www.silicon.fr/feed",
            "https://www.undernews.fr/feed",
        ],
        "en": [
            "https://www.docker.com/blog/feed/",
            "https://kubernetes.io/feed.xml",
        ]
    }
}

# Mots-clés pour filtrer les articles anglais importants
IMPORTANT_KEYWORDS = {
    "IA/ML": ["gpt", "llama", "claude", "mistral", "gemini", "training", "fine-tuning", "transformer"],
    "Cloud": ["aws", "azure", "gcp", "kubernetes", "lambda", "serverless", "terraform"],
    "DevSecOps": ["security", "vulnerability", "cve", "docker", "kubernetes", "ci/cd"],
    "Full Stack": ["react 19", "vue 3", "angular", "next.js", "typescript 5", "node.js"]
}


def detect_language(text: str) -> str:
    """Détecte la langue d'un texte (simple heuristique)"""
    if not text:
        return "unknown"
    
    # Mots français courants
    french_words = ["le", "la", "les", "un", "une", "des", "et", "est", "dans", "pour", "sur", "avec", "par", "plus", "comment", "pourquoi"]
    # Mots anglais courants
    english_words = ["the", "a", "an", "and", "is", "in", "for", "on", "with", "by", "how", "why", "what"]
    
    text_lower = text.lower()
    
    french_count = sum(1 for word in french_words if f" {word} " in text_lower)
    english_count = sum(1 for word in english_words if f" {word} " in text_lower)
    
    if french_count > english_count:
        return "fr"
    elif english_count > french_count:
        return "en"
    else:
        return "unknown"


def is_important_english_article(title: str, summary: str, category: str) -> bool:
    """Vérifie si un article anglais contient des mots-clés importants"""
    text = (title + " " + summary).lower()
    keywords = IMPORTANT_KEYWORDS.get(category, [])
    
    return any(keyword.lower() in text for keyword in keywords)


def fetch_rss_articles(category: str, feed_urls: Dict[str, List[str]], max_age_days: int = 7) -> List[Dict]:
    """Récupère les articles récents depuis les flux RSS avec gestion de la langue"""
    articles = []
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    # Traiter d'abord les sources françaises
    for lang in ["fr", "en"]:
        if lang not in feed_urls:
            continue
            
        for feed_url in feed_urls[lang]:
            try:
                feed = feedparser.parse(feed_url)
                source_name = feed.feed.get('title', feed_url)
                
                for entry in feed.entries[:5]:  # Limite à 5 articles par source
                    published = entry.get('published_parsed') or entry.get('updated_parsed')
                    if published:
                        pub_date = datetime(*published[:6])
                        if pub_date < cutoff_date:
                            continue
                    
                    title = entry.get('title', 'Sans titre')
                    summary = entry.get('summary', '')
                    
                    # Détecter la langue
                    detected_lang = detect_language(title + " " + summary)
                    
                    # Si c'est anglais, vérifier l'importance
                    if detected_lang == "en" and lang == "en":
                        if not is_important_english_article(title, summary, category):
                            print(f"   ⏭️  Article anglais filtré (non prioritaire): {title[:50]}...")
                            continue
                    
                    # Emoji selon la langue
                    lang_emoji = "🇫🇷" if detected_lang == "fr" else "🇬🇧" if detected_lang == "en" else "🌐"
                    
                    article = {
                        "title": f"{lang_emoji} {title}",
                        "url": entry.get('link', ''),
                        "summary": summary[:300],  # Limite à 300 caractères
                        "source": source_name,
                        "category": category,
                        "date": datetime.now().isoformat()[:10],
                        "language": detected_lang
                    }
                    articles.append(article)
                    
            except Exception as e:
                print(f"Erreur lors de la récupération de {feed_url}: {e}")
                continue
    
    # Trier : français en premier
    articles.sort(key=lambda x: (x.get('language') != 'fr', x.get('title', '')))
    
    return articles


def add_to_notion(articles: List[Dict]) -> int:
    """Ajoute les articles à la base de données Notion"""
    if not NOTION_API_KEY:
        print("ERREUR: NOTION_API_KEY non définie")
        return 0
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    added_count = 0
    
    for article in articles:
        try:
            # Vérifier si l'article existe déjà (par URL)
            query_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
            query_data = {
                "filter": {
                    "property": "URL",
                    "url": {
                        "equals": article['url']
                    }
                }
            }
            
            response = requests.post(query_url, headers=headers, json=query_data)
            if response.status_code == 200 and response.json().get('results'):
                print(f"Article déjà existant: {article['title']}")
                continue
            
            # Ajouter l'article
            page_data = {
                "parent": {"database_id": NOTION_DATABASE_ID},
                "properties": {
                    "Titre": {
                        "title": [{"text": {"content": article['title'][:2000]}}]
                    },
                    "URL": {
                        "url": article['url']
                    },
                    "Catégorie": {
                        "select": {"name": article['category']}
                    },
                    "Source": {
                        "rich_text": [{"text": {"content": article['source']}}]
                    },
                    "Date Ajout": {
                        "date": {"start": article['date']}
                    },
                    "Statut": {
                        "select": {"name": "📥 À lire"}
                    },
                    "Priorité": {
                        "select": {"name": "⚡ Moyenne"}
                    },
                    "Résumé": {
                        "rich_text": [{"text": {"content": article['summary']}}]
                    }
                }
            }
            
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=headers,
                json=page_data
            )
            
            if response.status_code == 200:
                added_count += 1
                print(f"✅ Ajouté: {article['title']}")
            else:
                print(f"❌ Erreur lors de l'ajout de {article['title']}: {response.text}")
                
        except Exception as e:
            print(f"Erreur lors de l'ajout de {article['title']}: {e}")
            continue
    
    return added_count


def send_email_summary(articles: List[Dict], added_count: int):
    """Envoie un email récapitulatif"""
    if not all([EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD]):
        print("ERREUR: Configuration email incomplète")
        return False
    
    # Grouper par catégorie
    by_category = {}
    for article in articles:
        cat = article['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(article)
    
    # Construire le HTML
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            .article {{ margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            .article h3 {{ margin: 0 0 5px 0; color: #2c3e50; }}
            .article a {{ color: #3498db; text-decoration: none; }}
            .article a:hover {{ text-decoration: underline; }}
            .meta {{ color: #7f8c8d; font-size: 0.9em; }}
            .summary {{ margin-top: 8px; color: #555; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>📚 Veille Technologique - Semaine du {datetime.now().strftime('%d/%m/%Y')}</h1>
        <p><strong>{added_count} nouveaux articles</strong> ajoutés à votre base Notion cette semaine !</p>
    """
    
    # Emojis par catégorie
    category_emojis = {
        "Full Stack": "🔷",
        "IA/ML": "🤖",
        "Cloud": "☁️",
        "DevSecOps": "🔒"
    }
    
    for category, articles_list in by_category.items():
        emoji = category_emojis.get(category, "📌")
        html_content += f"""
        <h2>{emoji} {category} ({len(articles_list)} articles)</h2>
        """
        
        for article in articles_list[:10]:  # Limite à 10 par catégorie dans l'email
            html_content += f"""
            <div class="article">
                <h3><a href="{article['url']}">{article['title']}</a></h3>
                <div class="meta">Source: {article['source']}</div>
                <div class="summary">{article['summary']}</div>
            </div>
            """
    
    html_content += f"""
        <div class="footer">
            <p>🔗 <a href="https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}">Voir tous les articles dans Notion</a></p>
            <p>Ce récapitulatif est envoyé automatiquement chaque lundi matin.</p>
        </div>
    </body>
    </html>
    """
    
    # Créer le message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📚 Veille Tech - {added_count} nouveaux articles - {datetime.now().strftime('%d/%m/%Y')}"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    
    # Version texte simple
    text_content = f"Veille Technologique - {added_count} nouveaux articles ajoutés.\n\n"
    text_content += f"Consultez votre base Notion: https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}\n"
    
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Envoyer l'email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email envoyé avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email: {e}")
        return False


def main():
    """Fonction principale"""
    print("🚀 Démarrage de la veille technologique automatisée")
    print(f"📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    
    # Collecter les articles
    all_articles = []
    for category, feeds in RSS_FEEDS.items():
        print(f"🔍 Collecte des articles: {category}")
        articles = fetch_rss_articles(category, feeds)
        all_articles.extend(articles)
        print(f"   ➜ {len(articles)} articles trouvés\n")
    
    print(f"📊 Total: {len(all_articles)} articles collectés\n")
    
    if not all_articles:
        print("ℹ️  Aucun nouvel article à ajouter")
        return
    
    # Ajouter à Notion
    print("📝 Ajout des articles à Notion...")
    added_count = add_to_notion(all_articles)
    print(f"\n✅ {added_count} articles ajoutés à Notion\n")
    
    # Envoyer l'email
    if added_count > 0:
        print("📧 Envoi de l'email récapitulatif...")
        send_email_summary(all_articles, added_count)
    
    print("\n✨ Terminé!")


if __name__ == "__main__":
    main()
