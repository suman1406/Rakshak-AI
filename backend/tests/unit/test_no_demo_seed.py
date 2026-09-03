from app.core.config import Settings


def test_runtime_configuration_has_no_demo_seed_switch() -> None:
    """Production startup must not have a path that inserts synthetic records."""
    assert "SEED_DEMO_DATA" not in Settings.model_fields
