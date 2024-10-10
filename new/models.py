from sqlalchemy import Column, Integer, String, Text, DateTime,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the Base class
Base = declarative_base()



Base = declarative_base()

class Article(Base):
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Ensure Text is imported
    published_at = Column(String, nullable=True)  # You can change this to DateTime if needed
    url = Column(String, nullable=False)
    category = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Article(title={self.title}, category={self.category})>"


# Database connection details (ensure DATABASE_URI is set correctly)
DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/newsdb'

# Create an engine
engine = create_engine(DATABASE_URI)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# To create the tables in the database, uncomment the following line
Base.metadata.create_all(engine)

