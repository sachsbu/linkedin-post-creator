from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PostDB(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    platform = Column(String, default="linkedin", index=True)
    story_id = Column(String, index=True)
    source_name = Column(String, default="Hacker News")
    title = Column(String)
    source_url = Column(Text)
    hn_url = Column(Text)
    author = Column(String)
    score = Column(Integer)
    comments_count = Column(Integer)
    
    summary_what = Column(Text)
    summary_why = Column(Text)
    summary_impact = Column(Text)
    summary_takeaway = Column(Text)
    
    linkedin_caption = Column(Text)
    hashtags = Column(Text)  # stored as comma-separated string
    word_count = Column(Integer)
    tone = Column(String, default="professional")
    
    image_path = Column(Text)
    image_type = Column(String)  # og_image / generated_card
    output_folder = Column(Text)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
