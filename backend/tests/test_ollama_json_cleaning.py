import json
import pytest
from app.ai.ollama_provider import _clean_json_text, OllamaProvider
from app.models.domain import ArticleSummary

def test_clean_json_text_markdown_block():
    raw = '```json\n{\n  "what_happened": "Test story",\n  "why_it_matters": "Matters",\n  "impact": "High",\n  "key_takeaway": "Learn"\n}\n```'
    cleaned = _clean_json_text(raw)
    data = json.loads(cleaned)
    assert data["what_happened"] == "Test story"

def test_clean_json_text_extra_text():
    raw = 'Here is your output:\n```\n{"what_happened": "Extracted"}\n```\nHope this helps!'
    cleaned = _clean_json_text(raw)
    data = json.loads(cleaned)
    assert data["what_happened"] == "Extracted"

def test_clean_json_text_empty():
    assert _clean_json_text("") == "{}"
    assert _clean_json_text(None) == "{}"
