import feedparser
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from celery import Celery

# Create a Celery app
app = Celery('tasks', broker='pyamqp://guest@localhost//')

# Define the task using the celery decorator
@app.task
def process_articles():
    # Your logic for processing articles
    print("Processing articles...")


# Database setup
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/newsdb' # Update with your credentials
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define the Article model
class Article(Base):
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    published_at = Column(DateTime)
    source_url = Column(String)
    category = Column(String)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Categorization function
def categorize_article(title, content):
    # Define keywords for each category
    categories = {
        "Terrorism / protest / political unrest / riot": ["terror", "protest", "riot", "unrest", "violence"],
        "Positive/Uplifting": ["hope", "success", "win", "achieve", "positive"],
        "Natural Disasters": ["earthquake", "flood", "hurricane", "disaster", "storm"],
        "Others": []
    }

    # Check for keywords in title and content
    for category, keywords in categories.items():
        if any(keyword.lower() in title.lower() or keyword.lower() in content.lower() for keyword in keywords):
            return category

    return "Others"  # Default category if no keywords match

def parse_rss_feeds(rss_feed_urls):
    for rss_url in rss_feed_urls:
        print(f"Parsing feed: {rss_url}")
        feed = feedparser.parse(rss_url)

        # Ensure we are iterating over feed entries correctly
        for entry in feed.entries:
            # Extract data safely from each entry
            title = entry.title if 'title' in entry else 'No Title'
            content = entry.content[0].value if 'content' in entry else 'No Content'
            source_url = entry.link if 'link' in entry else 'No source_url'
            category = 'Others'  # You can customize this based on your needs
            
            # Attempt to parse the published date safely
            published_at = None  # Initialize published_at as None
            
            # Check if the published attribute exists
            if 'published' in entry:
                try:
                    published_at = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    published_at = None

            # Logging the information
            print(f"Saving article - Title: {title}, Published At: {published_at}, source_url: {source_url}, Category: {category}")

            # Save the article to the database
            save_article_to_db(title, content, published_at, source_url, category)

def save_article_to_db(title, content, published_at, source_url, category):
    try:
        new_article = Article(
            title=title,
            content=content,
            published_at=published_at,  # Ensure this is a datetime object
            source_url=source_url,
            category=category
        )
        session.add(new_article)
        session.commit()
        print(f"Saved article with ID: {new_article.id}")
    except Exception as e:
        print(f"Error saving article: {e}")
        session.rollback()  # Rollback on error
    
# tasks.py
def process_articles():
    # Your logic for processing articles
    pass


# Example usage
rss_feed_urls = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        "http://feeds.foxnews.com/foxnews/politics",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.feedburner.com/NewshourWorld",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
]

if __name__ == "__main__":
    # Create the table if it doesn't exist
    Base.metadata.create_all(engine)

    parse_rss_feeds(rss_feed_urls)
