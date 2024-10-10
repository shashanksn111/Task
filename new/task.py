import feedparser
from sqlalchemy.orm import sessionmaker
from models import NewsArticle, engine
from celery_config import app
import spacy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Categories and keywords for classification
categories = {
    'Terrorism / protest / political unrest / riot': ["terrorism", "protest", "riot", "violence", "war", "military", "attack"],
    'Positive/Uplifting': ["uplifting", "success", "celebration", "achievement", "joy", "hope"],
    'Natural Disasters': ["earthquake", "flood", "tsunami", "hurricane", "cyclone", "storm", "disaster"],
    'Others': []
}

# RSS feeds
rss_feeds = [
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://qz.com/feed",
    "http://feeds.foxnews.com/foxnews/politics",
    "http://feeds.reuters.com/reuters/businessNews",
    "http://feeds.feedburner.com/NewshourWorld",
    "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
]

# Function to categorize an article using spaCy
def categorize_article(text):
    doc = nlp(text.lower())
    for category, keywords in categories.items():
        if any(keyword in doc.text for keyword in keywords):
            return category
    return "Others"

# Celery task to fetch and categorize articles
@app.task
def process_articles():
    session = sessionmaker(bind=engine)()

    for feed_url in rss_feeds:
        parsed_feed = feedparser.parse(feed_url)
        for entry in parsed_feed.entries:
            # Check if the article is already in the database (avoid duplicates)
            existing_article = session.query(NewsArticle).filter_by(link=entry.link).first()
            if not existing_article:
                category = categorize_article(entry.title + ' ' + entry.get('summary', ''))

                # Add the article to the database
                article = NewsArticle(
                    title=entry.title,
                    link=entry.link,
                    description=entry.get('summary', ''),
                    published_date=entry.get('published', ''),
                    category=category
                )
                session.add(article)
                logger.info(f"Added article: {entry.title} | Category: {category}")
    
    # Commit changes to the database
    session.commit()
    session.close()
