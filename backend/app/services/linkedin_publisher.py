import logging
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class LinkedInPublisherService:
    @classmethod
    async def publish_to_company_page(
        cls,
        caption: str,
        hashtags: List[str],
        access_token: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        token = access_token or settings.LINKEDIN_ACCESS_TOKEN
        org_id = organization_id or settings.LINKEDIN_ORGANIZATION_ID

        if not token or not token.strip():
            raise ValueError(
                "LinkedIn auto-publishing requires LINKEDIN_ACCESS_TOKEN. "
                "Please configure LINKEDIN_ACCESS_TOKEN in your .env file."
            )

        if not org_id or not org_id.strip():
            raise ValueError(
                "LinkedIn auto-publishing requires LINKEDIN_ORGANIZATION_ID. "
                "Please configure LINKEDIN_ORGANIZATION_ID in your .env file."
            )

        clean_org_id = org_id.replace("urn:li:organization:", "").strip()
        author_urn = f"urn:li:organization:{clean_org_id}"

        hashtag_text = " ".join(hashtags) if hashtags else ""
        full_text = f"{caption}\n\n{hashtag_text}".strip()

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": full_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        logger.info(f"Publishing post to LinkedIn Organization URN '{author_urn}'...")

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code not in (200, 201):
                logger.error(f"LinkedIn API error ({resp.status_code}): {resp.text}")
                raise RuntimeError(f"LinkedIn API error ({resp.status_code}): {resp.text}")

            result = resp.json()
            post_urn = result.get("id", "urn:li:ugcPost:success")
            logger.info(f"Successfully published post to LinkedIn Company Page! Post URN: {post_urn}")

            return {
                "status": "published",
                "post_urn": post_urn,
                "organization_id": clean_org_id,
                "message": "Successfully published post to LinkedIn Company Page!"
            }
