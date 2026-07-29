import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.instagram_publisher import InstagramPublisherService
from app.config import settings

@pytest.mark.asyncio
async def test_instagram_publisher_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    monkeypatch.setattr(settings, "INSTAGRAM_ACCESS_TOKEN", "")

    with pytest.raises(ValueError) as exc_info:
        await InstagramPublisherService.publish_to_instagram(
            caption="Test caption",
            hashtags=["#Tech"],
            media_url_or_path="http://example.com/test.jpg"
        )
    assert "INSTAGRAM_BUSINESS_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_instagram_publisher_success(monkeypatch):
    monkeypatch.setattr(settings, "INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setattr(settings, "INSTAGRAM_ACCESS_TOKEN", "mock_access_token")

    mock_container_res = MagicMock()
    mock_container_res.status_code = 200
    mock_container_res.json.return_value = {"id": "container_12345"}

    mock_publish_res = MagicMock()
    mock_publish_res.status_code = 200
    mock_publish_res.json.return_value = {"id": "post_67890"}

    async def mock_post(url, params=None, **kwargs):
        if "/media_publish" in url:
            return mock_publish_res
        return mock_container_res

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_client_post:
        mock_client_post.side_effect = mock_post

        result = await InstagramPublisherService.publish_to_instagram(
            caption="Launching our AI platform!",
            hashtags=["#AI", "#TechStartup"],
            media_url_or_path="https://example.com/image.jpg",
            media_type="image"
        )

        assert result["status"] == "success"
        assert result["post_id"] == "post_67890"
        assert result["container_id"] == "container_12345"
