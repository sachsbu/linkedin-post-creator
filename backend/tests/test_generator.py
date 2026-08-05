import pytest
from pathlib import Path
from app.models.domain import Story, ArticleSummary
from app.services.exporter import ArtifactExporter

def test_artifact_exporter(tmp_path: Path):
    story = Story(
        id="9999",
        title="Meta Releases Llama 3.3 70B Open Weight Model",
        url="https://example.com/llama33",
        hn_url="https://news.ycombinator.com/item?id=9999",
        author="meta_dev",
        score=1250,
        comments_count=430,
        source_name="Hacker News"
    )
    
    summary = ArticleSummary(
        what_happened="Meta launched Llama 3.3 70B featuring state-of-the-art reasoning at lower inference cost.",
        why_it_matters="Open-weights AI models are now matching proprietary flagship models.",
        impact="Startups can self-host enterprise AI models at a fraction of the cost.",
        key_takeaway="Evaluate Llama 3.3 for local open-source deployment."
    )
    
    caption = "Meta just dropped Llama 3.3 70B and it changes open source AI.\n\nMatching top proprietary models while drastically reducing compute costs.\n\nWhat is your team's stance on open weights?"
    hashtags = ["#AI", "#MachineLearning", "#OpenSource", "#Meta", "#LLM"]
    
    image_path = tmp_path / "social_card.png"
    image_path.write_bytes(b"dummy image content")
    
    output_files = ArtifactExporter.export_all(
        output_dir=tmp_path,
        story=story,
        summary=summary,
        caption=caption,
        hashtags=hashtags,
        image_path=image_path,
        image_type="generated_card",
        tone="founder",
        model_used="Gemini"
    )
    
    assert output_files["post_md"].exists()
    assert output_files["post_txt"].exists()
    assert output_files["metadata_json"].exists()
    
    assert "#OpenSource" in output_files["metadata_json"].read_text(encoding="utf-8")

