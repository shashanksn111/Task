from tasks import process_articles

if __name__ == '__main__':
    # Trigger the Celery task to fetch and process RSS articles
    process_articles.delay()
    print("Task to process articles has been triggered!")
