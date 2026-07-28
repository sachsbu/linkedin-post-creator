import logging
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class LinkedInPublisherService:
    @classmethod
    async def get_user_person_urn(cls, client: httpx.AsyncClient, token: str) -> Optional[str]:
        headers = {"Authorization": f"Bearer {token}"}
        # Try OpenID Connect /v2/userinfo
        try:
            resp = await client.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            if resp.status_code == 200:
                user_id = resp.json().get("sub")
                if user_id:
                    return f"urn:li:person:{user_id}"
        except Exception:
            pass

        # Try legacy /v2/me
        try:
            headers_v2 = {
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            resp = await client.get("https://api.linkedin.com/v2/me", headers=headers_v2)
            if resp.status_code == 200:
                user_id = resp.json().get("id")
                if user_id:
                    return f"urn:li:person:{user_id}"
        except Exception:
            pass

        return None

    @classmethod
    async def resolve_author_urn(cls, client: httpx.AsyncClient, token: str, org_id_setting: str) -> str:
        clean = org_id_setting.replace("urn:li:organization:", "").replace("urn:li:person:", "").strip()

        # If explicitly a person URN
        if org_id_setting.startswith("urn:li:person:"):
            return org_id_setting

        # If numeric organization ID
        if clean.isdigit():
            return f"urn:li:organization:{clean}"

        # Try auto-resolving numeric Organization URN via LinkedIn API
        logger.info(f"LINKEDIN_ORGANIZATION_ID '{org_id_setting}' is not numeric. Attempting auto-resolution via LinkedIn API...")
        try:
            acls_url = "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee"
            headers = {
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            resp = await client.get(acls_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("elements", [])
                for elem in elements:
                    target = elem.get("organizationalTarget", "")
                    if target.startswith("urn:li:organization:"):
                        logger.info(f"Successfully auto-resolved LinkedIn Organization URN: '{target}'")
                        return target
            else:
                logger.warning(f"Organizational ACL API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Failed to auto-resolve LinkedIn organization URN: {e}")

        # Fallback error guidance if not numeric and auto-resolution failed
        raise ValueError(
            f"LINKEDIN_ORGANIZATION_ID in .env must be numeric (e.g. '135824181'), but got '{org_id_setting}'. "
            "To find your numeric ID: open your LinkedIn Company Page as admin and copy the digits from the URL."
        )

    @classmethod
    async def _post_via_ugc(cls, client: httpx.AsyncClient, token: str, author_urn: str, full_text: str) -> Optional[Dict[str, Any]]:
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
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code in (200, 201):
            return resp.json()
        logger.warning(f"ugcPosts API returned {resp.status_code}: {resp.text}")
        return None

    @classmethod
    async def _post_via_rest(cls, client: httpx.AsyncClient, token: str, author_urn: str, full_text: str) -> Optional[Dict[str, Any]]:
        url = "https://api.linkedin.com/rest/posts"
        headers = {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": "202401",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        payload = {
            "author": author_urn,
            "commentary": full_text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code in (200, 201):
            res_data = resp.json() if resp.text else {}
            post_id = resp.headers.get("x-restli-id") or res_data.get("id") or "urn:li:share:success"
            return {"id": post_id}
        logger.warning(f"rest/posts API returned {resp.status_code}: {resp.text}")
        return None

    @classmethod
    async def publish_to_company_page(
        cls,
        caption: str,
        hashtags: List[str],
        access_token: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        token = (access_token or settings.LINKEDIN_ACCESS_TOKEN or "").strip()
        org_id = (organization_id or settings.LINKEDIN_ORGANIZATION_ID or "").strip()

        if not token:
            raise ValueError(
                "LinkedIn auto-publishing requires LINKEDIN_ACCESS_TOKEN. "
                "Please configure LINKEDIN_ACCESS_TOKEN in your .env file."
            )

        if not org_id:
            raise ValueError(
                "LinkedIn auto-publishing requires LINKEDIN_ORGANIZATION_ID. "
                "Please configure LINKEDIN_ORGANIZATION_ID in your .env file."
            )

        async with httpx.AsyncClient(timeout=20.0) as client:
            author_urn = await cls.resolve_author_urn(client, token, org_id)

            hashtag_text = " ".join(hashtags) if hashtags else ""
            full_text = f"{caption}\n\n{hashtag_text}".strip()

            logger.info(f"Attempting to publish post to LinkedIn Author URN '{author_urn}'...")

            # 1. Try modern rest/posts API first
            result = await cls._post_via_rest(client, token, author_urn, full_text)

            # 2. Try legacy ugcPosts API if rest/posts failed
            if not result:
                result = await cls._post_via_ugc(client, token, author_urn, full_text)

            if result:
                post_urn = result.get("id", "urn:li:ugcPost:success")
                logger.info(f"Successfully published post to LinkedIn! Post URN: {post_urn}")
                return {
                    "status": "published",
                    "post_urn": post_urn,
                    "organization_id": author_urn,
                    "message": f"Successfully published post to LinkedIn ({author_urn})!"
                }

            # 3. Fallback: If company page publishing failed (likely due to missing w_organization_social scope),
            # try publishing to the user's personal member profile
            logger.info("Company page posting failed. Attempting fallback to personal profile...")
            person_urn = await cls.get_user_person_urn(client, token)
            if person_urn:
                result_person = await cls._post_via_rest(client, token, person_urn, full_text) or await cls._post_via_ugc(client, token, person_urn, full_text)
                if result_person:
                    post_urn = result_person.get("id", "urn:li:ugcPost:success")
                    return {
                        "status": "published",
                        "post_urn": post_urn,
                        "organization_id": person_urn,
                        "message": (
                            "Published to your LinkedIn Personal Profile! "
                            "(To publish directly to your UVERA Company Page, ensure your token has the 'w_organization_social' scope "
                            "and your developer app is added under Company Page -> Admin Tools)."
                        )
                    }

            # If all failed, throw actionable diagnostic error
            raise ValueError(
                f"LinkedIn API Access Denied for author '{author_urn}'.\n\n"
                "To fix this issue:\n"
                "1. Go to LinkedIn Developer Portal -> your App -> Auth tab.\n"
                "2. Ensure the scope 'w_organization_social' is checked when generating your OAuth token.\n"
                "3. Ensure the LinkedIn user account generating the token is an Admin of the UVERA Company Page (ID: 135824181)."
            )
