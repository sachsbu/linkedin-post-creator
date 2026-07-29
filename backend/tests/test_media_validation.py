import pytest
from pathlib import Path
from PIL import Image
from app.services.media_validation_service import MediaValidationService

def test_classify_aspect_ratio():
    # Square 1:1
    ratio_name, warning = MediaValidationService.classify_aspect_ratio(1080, 1080)
    assert ratio_name == "1:1"
    assert warning is None

    # Portrait 4:5 (1080x1350)
    ratio_name, warning = MediaValidationService.classify_aspect_ratio(1080, 1350)
    assert ratio_name == "4:5"
    assert warning is None

    # Landscape 1.91:1 (1200x628)
    ratio_name, warning = MediaValidationService.classify_aspect_ratio(1200, 628)
    assert ratio_name == "1.91:1"
    assert warning is None

    # Non-standard ratio (16:9 -> 1.77)
    ratio_name, warning = MediaValidationService.classify_aspect_ratio(1920, 1080)
    assert warning is not None
    assert "differs from Instagram standard ratios" in warning


def test_validate_image(tmp_path: Path):
    img_path = tmp_path / "test_square.png"
    img = Image.new("RGB", (1080, 1080), color="blue")
    img.save(img_path)

    res = MediaValidationService.validate_image(img_path, filename="test_square.png", mime_type="image/png")
    assert res.is_valid is True
    assert res.aspect_ratio == "1:1"
    assert res.width == 1080
    assert res.height == 1080
    assert len(res.errors) == 0


def test_validate_oversized_image(tmp_path: Path):
    img_path = tmp_path / "huge.png"
    img_path.write_bytes(b"0" * (15 * 1024 * 1024))  # 15MB file

    res = MediaValidationService.validate_image(img_path, filename="huge.png")
    assert res.is_valid is False
    assert any("exceeds maximum allowed limit" in err for err in res.errors)
