import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import httpx
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class ImageService:
    @staticmethod
    async def resolve_or_generate_image(
        og_image_url: Optional[str],
        title: str,
        publication: str,
        output_dir: Path
    ) -> Tuple[Path, str]:
        """
        Attempts to download the OpenGraph image.
        If unavailable or invalid, generates a sleek tech social card.
        Returns tuple of (Image File Path, Image Type ['og_image' or 'generated_card']).
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

        # 2. Fallback: Generate custom high-res social card card (1200x630)
        card_path = output_dir / "social_card.png"
        ImageService.generate_social_card(title, publication, card_path)
        return card_path, "generated_card"

    @staticmethod
    def generate_social_card(title: str, publication: str, save_path: Path):
        """
        Generates a modern, clean 1200x630 social card for social media sharing.
        """
        width, height = 1200, 630
        image = Image.new("RGB", (width, height), color="#0F172A")  # Slate 900
        draw = ImageDraw.Draw(image)

        # 1. Draw subtle tech gradient canvas lines / accents
        for i in range(height):
            # Gradient overlay from dark navy (#0F172A) to deep indigo (#1E1B4B)
            r = int(15 + (30 - 15) * (i / height))
            g = int(23 + (27 - 23) * (i / height))
            b = int(42 + (75 - 42) * (i / height))
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        # Top accent bar (Cyan/Blue gradient accent)
        draw.rectangle([0, 0, width, 12], fill="#38BDF8")  # Sky blue accent bar

        # Subtle card boundary box
        margin = 60
        draw.rectangle(
            [margin, margin, width - margin, height - margin],
            outline="#334155",
            width=2
        )

        # 2. Try loading font or fallback to default
        try:
            # Common font paths on Windows/Linux
            font_title = ImageFont.truetype("arial.ttf", 46)
            font_tag = ImageFont.truetype("arial.ttf", 26)
            font_sub = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            font_title = ImageFont.load_default()
            font_tag = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        # Badge: TECH NEWS
        badge_box = [margin + 40, margin + 40, margin + 220, margin + 85]
        draw.rectangle(badge_box, fill="#1E293B", outline="#0EA5E9", width=1)
        draw.text((margin + 55, margin + 50), "TECH NEWS", fill="#38BDF8", font=font_tag)

        # Publication Name / Source
        pub_text = f"SOURCE: {publication.upper() if publication else 'HACKER NEWS'}"
        draw.text((width - margin - 350, margin + 52), pub_text, fill="#94A3B8", font=font_sub)

        # Wrap Title Text
        max_width_px = width - (margin * 2) - 80
        wrapped_lines = ImageService._wrap_text(title, font_title, max_width_px, draw)

        # Title position
        y_text = margin + 140
        for line in wrapped_lines[:4]:  # Max 4 lines
            draw.text((margin + 40, y_text), line, fill="#F8FAFC", font=font_title)
            y_text += 60

        # Footer / Branding
        footer_y = height - margin - 60
        draw.line([(margin + 40, footer_y - 20), (width - margin - 40, footer_y - 20)], fill="#334155", width=1)
        draw.text((margin + 40, footer_y), "AUTOMATED TECH SUMMARY", fill="#64748B", font=font_sub)
        draw.text((width - margin - 260, footer_y), "LINKEDIN POST CREATOR", fill="#38BDF8", font=font_sub)

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
