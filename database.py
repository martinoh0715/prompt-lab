from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create database file (creates prompts.db)
engine = create_engine("sqlite:///prompts.db")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Define the prompts table
class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)         # Prompt name
    version = Column(Integer, default=1)           # Version number
    system_prompt = Column(Text, nullable=False)   # Actual prompt content
    commit_message = Column(String)                # Reason for change
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=0)         # Is this the active version?

# Create tables
Base.metadata.create_all(engine)
print("✅ Database ready!")