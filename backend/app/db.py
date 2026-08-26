from contextlib import contextmanager

@contextmanager
def transaction():
    """Transaction seam for the PostgreSQL implementation used in deployment."""
    try:
        yield
    except Exception:
        raise

