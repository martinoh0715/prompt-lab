from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create database file (creates prompts.db)
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prompts.db")
# Railway PostgreSQL URL fix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
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