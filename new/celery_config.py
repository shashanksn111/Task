# tasks.py

from celery import Celery

# Create a Celery app
app = Celery('tasks', broker='pyamqp://guest@localhost//')

# Define the task using the celery decorator
@app.task
def process_articles():
    # Your logic for processing articles
    print("Processing articles...")
