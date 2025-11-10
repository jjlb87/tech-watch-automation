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
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')
NOTION_DATABASE_ID = "04e8ee4a-9d2a-4830-9086-4ab02669a118"
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = 587

# Sources RSS par catégorie
RSS_FEEDS = {
    "Full Stack": [
        "https://dev.to/feed",
        "https://daily.dev/blog/rss.xml",
        "https://web.dev/feed.xml",
        "https://css-tricks.com/feed/",
    ],
    "IA/ML": [
        "https://huggingface.co/blog/feed.xml",
        "https://blog.tensorflow.org/feeds/posts/default",
        "https://openai.com/blog/rss/",
        "https://www.deeplearning.ai/the-batch/feed/",
    ],
    "Cloud": [
        "https://aws.amazon.com/blogs/aws/feed/",
        "https://azure.microsoft.com/en-us/blog/feed/",
        "https://cloud.google.com/blog/rss",
        "https://www.infoq.com/cloud-computing/rss/",
    ],
    "DevSecOps": [
        "https://www.docker.com/blog/feed/",
        "https://kubernetes.io/feed.xml",
        "https://owasp.org/blog/feed.xml",
        "https://github.blog/feed/",
    ]
}


def fetch_rss_articles(category: str, feed_urls: List[str], max_age_days: int = 7) -> List[Dict]:
    """Récupère les articles récents depuis les flux RSS"""
    articles = []
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    for feed_url in feed_urls:
        try:
            feed = feedparser.parse(feed_url)
            source_name = feed.feed.get('title', feed_url)
            
            for entry in feed.entries[:5]:  # Limite à 5 articles par source
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < cutoff_date:
                        continue
                
                article = {
                    "title": entry.get('title', 'Sans titre'),
                    "url": entry.get('link', ''),
                    "summary": entry.get('summary', '')[:300],  # Limite à 300 caractères
                    "source": source_name,
                    "category": category,
                    "date": datetime.now().isoformat()[:10]
                }
                articles.append(article)
                
        except Exception as e:
            print(f"Erreur lors de la récupération de {feed_url}: {e}")
            continue
    
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
