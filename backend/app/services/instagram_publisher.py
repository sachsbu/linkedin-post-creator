import logging
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class InstagramPublisherService:
    GRAPH_API_VERSION = "v19.0"

    @classmethod
    async def publish_to_instagram(
        cls,
        caption: str,
        hashtags: List[str],
        media_url_or_path: str,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        account_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID.strip()
        token = settings.INSTAGRAM_ACCESS_TOKEN.strip()

        if not account_id or not token:
            raise ValueError(
                "Instagram publishing is not configured. Please set INSTAGRAM_BUSINESS_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN in your .env file."
            )

        if not media_url_or_path:
            raise ValueError("Media URL or file is required for publishing to Instagram.")

        # Ensure media URL is a full web URL
        if not media_url_or_path.startswith(("http://", "https://")):
            # If running locally or on server, wrap in host URL
            filename = media_url_or_path.split("/")[-1].split("\\")[-1]
            media_url = f"http://127.0.0.1:8001/output/uploads/{filename}"
        else:
            media_url = media_url_or_path

        full_caption = f"{caption.strip()}\n\n" + " ".join(hashtags)

        base_url = f"https://graph.facebook.com/{cls.GRAPH_API_VERSION}/{account_id}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. Step 1: Create Container
            container_params = {
                "caption": full_caption,
                "access_token": token
            }

            if media_type == "video":
                container_params["video_url"] = media_url
                container_params["media_type"] = "REELS"
            else:
                container_params["image_url"] = media_url

            logger.info(f"Creating Instagram media container for account {account_id}...")
            container_res = await client.post(f"{base_url}/media", params=container_params)

            if container_res.status_code != 200:
                logger.error(f"Instagram Container Error: {container_res.text}")
                raise RuntimeError(f"Meta Graph API error ({container_res.status_code}): {container_res.text}")

            container_data = container_res.json()
            container_id = container_data.get("id")

            if not container_id:
                raise RuntimeError(f"Meta Graph API did not return container ID: {container_data}")

            # 2. Step 2: Publish Container
            logger.info(f"Publishing Instagram media container {container_id}...")
            publish_res = await client.post(
                f"{base_url}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": token
                }
            )

            if publish_res.status_code != 200:
                logger.error(f"Instagram Publish Error: {publish_res.text}")
                raise RuntimeError(f"Meta Graph API publish error ({publish_res.status_code}): {publish_res.text}")

            publish_data = publish_res.json()
            post_id = publish_data.get("id", container_id)

            return {
                "status": "success",
                "post_id": post_id,
                "container_id": container_id,
                "message": f"Successfully published to Instagram handle! Post ID: {post_id}"
            }
