from unittest.mock import MagicMock
import pytest
from app.core.config import settings
from app.media_storage import MediaStorage

def test_s3_roundtrip_uses_private_object_reference_and_local_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'STORAGE_BACKEND', 's3')
    monkeypatch.setattr(settings, 'LOCAL_STORAGE_DIR', str(tmp_path))
    monkeypatch.setattr(settings, 'S3_BUCKET_NAME', 'test-evidence')
    storage = MediaStorage()
    client = MagicMock()
    def download(bucket, key, filename):
        from pathlib import Path
        Path(filename).write_bytes(b'actual evidence')
    client.download_file.side_effect = download
    monkeypatch.setattr(storage, '_client', lambda: client)
    source = tmp_path / 'source.mp4'; source.write_bytes(b'actual evidence')
    reference = storage.store('videos/a/video.mp4', source)
    assert reference == 's3://test-evidence/videos/a/video.mp4'
    assert 'ACL' not in client.upload_file.call_args.kwargs['ExtraArgs']
    local = storage.local_path(reference)
    assert local.read_bytes() == source.read_bytes()
    storage.local_path(reference)
    assert client.download_file.call_count == 1
    storage.delete(reference)
    assert not local.exists()
    client.delete_object.assert_called_once_with(Bucket='test-evidence', Key='videos/a/video.mp4')

@pytest.mark.parametrize('key', ['../outside', '/absolute', 'videos/../../outside', 'videos\\outside'])
def test_storage_rejects_unsafe_keys(key):
    with pytest.raises(ValueError):
        MediaStorage().store(key, 'source')

def test_storage_will_not_delete_outside_root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'LOCAL_STORAGE_DIR', str(tmp_path / 'storage'))
    with pytest.raises(ValueError):
        MediaStorage().delete(str(tmp_path / 'other-file'))
