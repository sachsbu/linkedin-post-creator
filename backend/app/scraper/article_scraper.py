import logging
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ArticleScraper:
    @staticmethod
    async def scrape(url: str) -> Dict[str, Any]:
        """
        Scrapes article content and OpenGraph metadata from the target URL.
        """
        result = {
            "title": "",
            "content": "",
            "og_image": None,
            "site_name": "",
            "author": "",
        }

        # Skip scraping if url is self or not http(s) or direct HN item
        if not url or url == "self" or not url.startswith(("http://", "https://")) or "news.ycombinator.com/item" in url:
            return result

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: status {resp.status_code}")
                    return result

                html = resp.text
                soup = BeautifulSoup(html, "html.parser")

                # Remove non-content elements
                for element in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
                    element.decompose()

                # Extract OG image
                og_img_tag = (
                    soup.find("meta", property="og:image")
                    or soup.find("meta", attrs={"name": "og:image"})
                    or soup.find("meta", attrs={"name": "twitter:image"})
                )
                if og_img_tag and og_img_tag.get("content"):
                    result["og_image"] = og_img_tag.get("content")

                # Extract site name
                site_tag = soup.find("meta", property="og:site_name")
                if site_tag and site_tag.get("content"):
                    result["site_name"] = site_tag.get("content")

                # Extract author
                author_tag = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
                if author_tag and author_tag.get("content"):
                    result["author"] = author_tag.get("content")

                # Extract main text content
                article_body = soup.find("article") or soup.find("main") or soup.body
                if article_body:
                    paragraphs = [p.get_text().strip() for p in article_body.find_all("p") if len(p.get_text().strip()) > 30]
                    result["content"] = "\n\n".join(paragraphs[:15])  # Top paragraphs

                # Fallback title
                if soup.title:
                    result["title"] = soup.title.get_text().strip()

        except Exception as e:
            logger.error(f"Error scraping article at {url}: {e}")

        return result
