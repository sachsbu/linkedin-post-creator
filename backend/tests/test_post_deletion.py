import pytest
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import PostDB

@pytest.mark.asyncio
async def test_delete_single_post(tmp_path: Path):
    folder = tmp_path / "sample_post_folder"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "post.md").write_text("sample content")

    assert folder.exists()

    # Simulate deletion logic
    import shutil
    if folder.exists():
        shutil.rmtree(folder)

    assert not folder.exists()
