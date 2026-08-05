import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import httpx
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).parent.parent / "assets" / "template.png"

class ImageService:
    @staticmethod
    async def resolve_or_generate_image(
        og_image_url: Optional[str],
        title: str,
        publication: str,
        output_dir: Path,
        generate_custom_fallback: bool = True
    ) -> Tuple[Optional[Path], str]:
        """
        Attempts to download the OpenGraph image.
        If unavailable or invalid, generates a social card using the UVERA brand template.
        Returns tuple of (Optional[Path], Image Type ['og_image', 'generated_card', or 'none']).
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Attempt downloading OG image if available
        if og_image_url:
            try:
                img_path = output_dir / "image.jpg"
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.get(og_image_url)
                    if resp.status_code == 200 and len(resp.content) > 2000:
                        with open(img_path, "wb") as f:
                            f.write(resp.content)
                        # Verify image validity
                        with Image.open(img_path) as img:
                            img.verify()
                        logger.info(f"Successfully downloaded OG image to {img_path}")
                        return img_path, "og_image"
            except Exception as e:
                logger.warning(f"Failed to download/verify OG image ({og_image_url}): {e}")

        # 2. Fallback: Generate custom high-res social card using UVERA template ONLY if requested
        if generate_custom_fallback:
            card_path = output_dir / "social_card.png"
            ImageService.generate_social_card(title, publication, card_path)
            return card_path, "generated_card"

        return None, "none"

    @staticmethod
    def generate_social_card(title: str, publication: str, save_path: Path):
        """
        Generates a clean social card for social media sharing using the official UVERA template.
        """
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if TEMPLATE_PATH.exists():
            image = Image.open(TEMPLATE_PATH).convert("RGB")
        else:
            # Fallback canvas if template file is missing
            image = Image.new("RGB", (1024, 586), color="#070707")
        
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Load bold and regular fonts with cross-platform fallbacks
        font_title = None
        font_sub = None
        font_candidates_bold = ["arialbd.ttf", "Helvetica-Bold.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"]
        font_candidates_sub = ["arial.ttf", "Helvetica.ttf", "DejaVuSans.ttf"]

        for font_name in font_candidates_bold:
            try:
                font_title = ImageFont.truetype(font_name, 30)
                break
            except Exception:
                continue

        for font_name in font_candidates_sub:
            try:
                font_sub = ImageFont.truetype(font_name, 18)
                break
            except Exception:
                continue

        if font_title is None:
            font_title = ImageFont.load_default()
        if font_sub is None:
            font_sub = ImageFont.load_default()

        margin_left = 50
        max_width = 500  # Leave right side for neural graph graphic

        y_offset = 140
        # Optional publication tag above title in brand lime accent (#A3E635)
        if publication and publication.lower() not in ["self", "custom", "none"]:
            pub_text = publication.strip().upper()
            draw.text((margin_left, y_offset), pub_text, fill="#A3E635", font=font_sub)
            y_offset += 32

        # Wrap Title Text
        wrapped_lines = ImageService._wrap_text(title, font_title, max_width, draw)
        if len(wrapped_lines) > 4:
            # Scale down font slightly for longer titles
            for font_name in font_candidates_bold:
                try:
                    font_title = ImageFont.truetype(font_name, 24)
                    break
                except Exception:
                    continue
            wrapped_lines = ImageService._wrap_text(title, font_title, max_width, draw)

        for line in wrapped_lines[:5]:
            draw.text((margin_left, y_offset), line, fill="#FFFFFF", font=font_title)
            bbox = draw.textbbox((0, 0), line, font=font_title)
            line_h = bbox[3] - bbox[1]
            y_offset += int(line_h * 1.3) + 6

        image.save(save_path, "PNG")
        logger.info(f"Generated social card saved to {save_path}")

    @staticmethod
    def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list:
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_str = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_str, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

