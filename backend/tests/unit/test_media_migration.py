import pytest
from app.core.config import settings
from app.media_storage import media_storage
from app.migrate_media import migrate
from app.models.video import Video, VideoStatus


@pytest.mark.asyncio
async def test_migration_is_dry_run_by_default_and_preserves_original(test_db, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'LOCAL_STORAGE_DIR', str(tmp_path))
    monkeypatch.setattr(settings, 'STORAGE_BACKEND', 's3')
    source = tmp_path / 'scan.mp4'
    source.write_bytes(b'legacy evidence')
    video = Video(field_id='field', uploaded_by='owner', storage_path=str(source), status=VideoStatus.ready)
    test_db.add(video)
    await test_db.commit()
    copied = []
    def store(key, path):
        copied.append(key)
        assert path.read_bytes() == b'legacy evidence'
        return 's3://evidence/' + key
    monkeypatch.setattr(media_storage, 'store', store)
    assert await migrate(test_db) == {'eligible': 1, 'copied': 0, 'unavailable': 0}
    assert copied == []
    assert (await migrate(test_db, apply=True))['copied'] == 1
    assert video.storage_path.startswith('s3://evidence/videos/')
    assert source.exists()
    assert (await migrate(test_db, apply=True))['eligible'] == 0
