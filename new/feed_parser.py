import feedparser
from datetime import datetime

feeds = [
    'http://rss.cnn.com/rss/cnn_topstories.rss',
    'http://qz.com/feed',
    'http://feeds.foxnews.com/foxnews/politics',
    'http://feeds.reuters.com/reuters/businessNews',
    'http://feeds.feedburner.com/NewshourWorld',
    'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
]

def parse_feeds():
    articles = []
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            article = {
                'title': entry.title,
                'content': entry.description,
                'pub_date': entry.published if 'published' in entry else datetime.now(),
                'source_url': entry.link
            }
            articles.append(article)
    return articles
