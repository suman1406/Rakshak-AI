from pathlib import Path
from tempfile import gettempdir

class EvidenceStorage:
    """Local development storage seam; production maps this interface to S3."""
    def __init__(self, root: str | None = None):
        self.root = Path(root or Path(gettempdir()) / "rakshak-evidence")
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, content: bytes) -> str:
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return str(target)

