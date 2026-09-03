from app.core.config import Settings


def test_runtime_configuration_has_no_demo_seed_switch() -> None:
    """Operational data cannot be inserted through the removed broad seed switch."""
    assert "SEED_DEMO_DATA" not in Settings.model_fields
