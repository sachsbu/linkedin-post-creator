import pytest
from pathlib import Path
from PIL import Image
from app.scraper.image_service import ImageService

def test_generate_social_card(tmp_path: Path):
    card_path = tmp_path / "test_card.png"
    ImageService.generate_social_card(
        title="Python 3.13 Released with Free-Threaded GIL Disabling Option",
        publication="Hacker News",
        save_path=card_path
    )
    
    assert card_path.exists()
    assert card_path.stat().st_size > 5000
    
    with Image.open(card_path) as img:
        assert img.width > 0 and img.height > 0
        assert img.format == "PNG"

