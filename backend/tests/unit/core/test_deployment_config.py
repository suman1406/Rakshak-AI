import pytest
from pydantic import ValidationError
from app.core.config import Settings


@pytest.mark.parametrize('secret', [
    'replace-with-a-strong-random-secret',
    'dev-secret-key-change-in-production-12345',
    'validation-only-do-not-deploy-this-key-2026',
    'short',
])
def test_production_rejects_documented_placeholder_secrets(secret):
    with pytest.raises(ValidationError, match='unique JWT_SECRET_KEY'):
        Settings(_env_file=None, ENVIRONMENT='production', JWT_SECRET_KEY=secret,
                 STORAGE_BACKEND='s3', DATABASE_URL='postgresql+psycopg://db/app')
