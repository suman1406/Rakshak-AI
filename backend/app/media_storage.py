"""Private evidence storage shared by API and workers.

Database paths are local paths for the single-host pilot, or s3:// URIs for
separate API/worker hosts. Downloaded objects are an expendable local cache.
"""
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
from app.core.config import settings
import time


class MediaStorage:
    def prune_cache(self, max_age_seconds=86400):
        root = (Path(settings.LOCAL_STORAGE_DIR) / 'object-cache').resolve()
        if not root.exists():
            return 0
        cutoff = time.time() - max_age_seconds
        removed = 0
        for candidate in root.rglob('*'):
            if candidate.is_file() and not candidate.is_symlink() and candidate.resolve().is_relative_to(root) and candidate.stat().st_mtime < cutoff:
                candidate.unlink(missing_ok=True)
                removed += 1
        return removed

    def _client(self):
        import boto3
        from botocore.config import Config
        return boto3.client('s3', endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version='s3v4', connect_timeout=10, read_timeout=60,
                          retries={'max_attempts': 3}, s3={'addressing_style': 'path'}))

    def _key(self, key: str) -> str:
        path = PurePosixPath(key)
        if path.is_absolute() or '..' in path.parts or '\\' in key or not key:
            raise ValueError('Invalid evidence object key')
        return str(path)

    def store(self, key: str, source: str | Path) -> str:
        key = self._key(key)
        if settings.STORAGE_BACKEND == 'local':
            return str(source)
        if settings.STORAGE_BACKEND != 's3':
            raise ValueError('STORAGE_BACKEND must be local or s3')
        extra = {}
        if settings.S3_SERVER_SIDE_ENCRYPTION:
            extra['ServerSideEncryption'] = settings.S3_SERVER_SIDE_ENCRYPTION
        self._client().upload_file(str(source), settings.S3_BUCKET_NAME, key, ExtraArgs=extra)
        return f's3://{settings.S3_BUCKET_NAME}/{key}'

    def local_path(self, reference: str) -> Path:
        if not reference.startswith('s3://'):
            return Path(reference)
        uri = urlparse(reference)
        if uri.netloc != settings.S3_BUCKET_NAME:
            raise ValueError('Evidence belongs to an unconfigured bucket')
        key = self._key(uri.path.lstrip('/'))
        target = Path(settings.LOCAL_STORAGE_DIR) / 'object-cache' / key
        if target.is_file():
            return target
        target.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
        try:
            self._client().download_file(settings.S3_BUCKET_NAME, key, str(temporary))
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def delete(self, reference: str) -> None:
        if reference.startswith('s3://'):
            uri = urlparse(reference)
            if uri.netloc != settings.S3_BUCKET_NAME:
                raise ValueError('Evidence belongs to an unconfigured bucket')
            key = self._key(uri.path.lstrip('/'))
            self._client().delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            (Path(settings.LOCAL_STORAGE_DIR) / 'object-cache' / key).unlink(missing_ok=True)
        else:
            target = Path(reference).resolve()
            root = Path(settings.LOCAL_STORAGE_DIR).resolve()
            if not target.is_relative_to(root):
                raise ValueError('Evidence path is outside configured storage')
            target.unlink(missing_ok=True)


media_storage = MediaStorage()
