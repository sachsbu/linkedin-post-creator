from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class Story(BaseModel):
    id: str
    title: str
    url: str
    hn_url: str
    author: str
    score: int
    comments_count: int
    published_at: Optional[datetime] = None
    rank_score: float = 0.0
    source_name: str = "Hacker News"

class ArticleSummary(BaseModel):
    what_happened: str = Field(description="Summary of what actually occurred")
    why_it_matters: str = Field(description="Context on why this story is significant")
    impact: str = Field(description="Impact on developers, startups, AI, or business")
    key_takeaway: str = Field(description="Core practical takeaway")

class GeneratePostRequest(BaseModel):
    story_id: Optional[str] = None
    source: Optional[str] = "hacker_news"
    tone: str = "professional"  # professional, founder, developer, investor
    provider: Optional[str] = None  # gemini, openai, ollama
    model: Optional[str] = None
    custom_url: Optional[str] = None
    custom_title: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    story_id: str
    source_name: str
    title: str
    source_url: str
    hn_url: str
    author: str
    score: int
    comments_count: int
    summary: ArticleSummary
    linkedin_caption: str
    hashtags: List[str]
    word_count: int
    tone: str
    image_path: str
    image_type: str  # "og_image" or "generated_card"
    output_folder: str
    model_used: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

