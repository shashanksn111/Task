import psycopg2
import feedparser
from datetime import datetime
import os

# Database connection parameters
conn = psycopg2.connect(
    host='localhost',
    database='newsdb',
    user='postgres',
    password='postgres'
)

# Create a cursor object
cur = conn.cursor()

# Ensure the 'published_at' column exists
# Ensure the table exists
try:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS news_articles (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        published_at TIMESTAMP NOT NULL,
        url TEXT NOT NULL,
        category TEXT NOT NULL
    );
    """)
    conn.commit()  # Commit the change
except Exception as e:
    print("Error creating table:", e)


# RSS feed URLs
rss_urls = [
    'http://rss.cnn.com/rss/cnn_topstories.rss',
    'http://qz.com/feed',
    'http://feeds.foxnews.com/foxnews/politics',
    'http://feeds.reuters.com/reuters/businessNews',
    'http://feeds.feedburner.com/NewshourWorld',
    'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
]

# Loop through each RSS feed URL
for rss_url in rss_urls:
    try:
        # Parse the RSS feed
        feed = feedparser.parse(rss_url)

        # Check for parsing errors
        if feed.bozo:
            print("Error parsing feed:", feed.bozo_exception)
            continue  # Skip to the next feed

        for entry in feed.entries:
            title = entry.title
            content = entry.content[0].value if 'content' in entry else 'No Content'
            published = entry.published if 'published' in entry else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            url = entry.link
            category = entry.get('category', 'Others')  # Default category if not found

            # Debug print for each article entry
            print(f'Debug - Title: {title}, Content Length: {len(content)}, Published: {published}, URL: {url}, Category: {category}')

            # Insert data into database
            try:
                cur.execute(
                    "INSERT INTO news_articles (title, content, published_at, url, category) VALUES (%s, %s, %s, %s, %s)",
                    (title, content, published, url, category)
                )
                print("Successfully inserted article into the database.")
            except Exception as e:
                print(f"Error saving article: {e}")
                conn.rollback()  # Rollback the transaction
                break  # Exit the loop on error
    except Exception as e:
        print(f"Failed to parse {rss_url}: {e}")

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()

print("Data export complete.")
