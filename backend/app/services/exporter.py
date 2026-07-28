import json
import re
from pathlib import Path
from typing import Dict, Any, List
from app.models.domain import Story, ArticleSummary

class ArtifactExporter:
    @staticmethod
    def export_all(
        output_dir: Path,
        story: Story,
        summary: ArticleSummary,
        caption: str,
        hashtags: List[str],
        image_path: Path,
        image_type: str,
        tone: str,
        model_used: str
    ) -> Dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        hashtag_str = " ".join(hashtags)
        relative_img_name = image_path.name

        # 1. Write post.md
        source_link = f"[{story.url}]({story.url})" if story.url.startswith("http") else story.url
        hn_link = f"[{story.hn_url}]({story.hn_url})" if story.hn_url.startswith("http") else story.hn_url

        post_md_content = f"""# {story.title}

## LinkedIn Caption

{caption}

{hashtag_str}

---
- **Source Article**: {source_link}
- **Discussion/Ref**: {hn_link}
- **Author**: {story.author}
- **Score**: {story.score} points | {story.comments_count} comments
- **Tone**: {tone.capitalize()}
- **Image**: `![Card]({relative_img_name})`
"""
        post_md_file = output_dir / "post.md"
        post_md_file.write_text(post_md_content, encoding="utf-8")

        # 2. Write post.txt (Pure copy-paste content)
        post_txt_content = f"{caption}\n\n{hashtag_str}"
        post_txt_file = output_dir / "post.txt"
        post_txt_file.write_text(post_txt_content, encoding="utf-8")

        # 3. Write metadata.json
        metadata = {
            "story": {
                "id": story.id,
                "title": story.title,
                "source_url": story.url,
                "hn_url": story.hn_url,
                "author": story.author,
                "score": story.score,
                "comments_count": story.comments_count,
                "source_name": story.source_name
            },
            "summary": summary.model_dump(),
            "post": {
                "caption": caption,
                "hashtags": hashtags,
                "word_count": len(caption.split()),
                "tone": tone
            },
            "image": {
                "filename": relative_img_name,
                "path": str(image_path.resolve()),
                "type": image_type
            },
            "generation": {
                "model_used": model_used,
                "output_dir": str(output_dir.resolve())
            }
        }
        metadata_file = output_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return {
            "post_md": post_md_file,
            "post_txt": post_txt_file,
            "metadata_json": metadata_file
        }

    @staticmethod
    def to_html(title: str, caption: str, hashtags: List[str], source_url: str, img_name: str) -> str:
        formatted_caption = caption.replace('\n', '<br>')
        hashtag_spans = " ".join([f'<span style="color:#0A66C2; font-weight:600;">{tag}</span>' for tag in hashtags])
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - LinkedIn Post</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F3F2EF; padding: 40px; display: flex; justify-content: center; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 0 0 1px rgba(0,0,0,0.15); width: 550px; padding: 20px; }}
        .header {{ font-weight: bold; font-size: 16px; color: #181818; margin-bottom: 12px; }}
        .body {{ font-size: 14px; color: #181818; line-height: 1.5; margin-bottom: 14px; }}
        .hashtags {{ font-size: 14px; margin-bottom: 14px; }}
        .img-container img {{ width: 100%; border-radius: 6px; border: 1px solid #E0E0E0; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">{title}</div>
        <div class="body">{formatted_caption}</div>
        <div class="hashtags">{hashtag_spans}</div>
        <div class="img-container">
            <img src="{img_name}" alt="Post image" />
        </div>
    </div>
</body>
</html>
"""
