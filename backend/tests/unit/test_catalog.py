import pytest
from sqlalchemy import select

from app.db.catalog import ensure_disease_catalog, _CATALOG_TAXONOMY_VERSION, _CROP_NAME, _DISEASE_NAMES
from app.models.farm import Crop, Disease


@pytest.mark.asyncio
async def test_ensure_disease_catalog_seeds_crop_and_diseases(test_db):
    # Initial seed
    await ensure_disease_catalog(test_db)

    # Verify crop created
    crop = (
        await test_db.execute(
            select(Crop).where(
                Crop.name == _CROP_NAME,
                Crop.taxonomy_version == _CATALOG_TAXONOMY_VERSION,
            )
        )
    ).scalar_one_or_none()
    assert crop is not None
    assert crop.active is True

    # Verify all 4 diseases created and linked to crop
    diseases = (
        await test_db.execute(
            select(Disease).where(Disease.crop_id == crop.id).order_by(Disease.name)
        )
    ).scalars().all()
    assert len(diseases) == len(_DISEASE_NAMES)
    assert sorted([d.name for d in diseases]) == sorted(_DISEASE_NAMES)
    for d in diseases:
        assert d.taxonomy_version == _CATALOG_TAXONOMY_VERSION
        assert d.active is True


@pytest.mark.asyncio
async def test_ensure_disease_catalog_is_idempotent(test_db):
    # Call twice
    await ensure_disease_catalog(test_db)
    await ensure_disease_catalog(test_db)

    # Ensure no duplicates
    crops = (await test_db.execute(select(Crop))).scalars().all()
    assert len(crops) == 1

    diseases = (await test_db.execute(select(Disease))).scalars().all()
    assert len(diseases) == len(_DISEASE_NAMES)


@pytest.mark.asyncio
async def test_ensure_disease_catalog_handles_partial_seed(test_db):
    # Run first seed
    await ensure_disease_catalog(test_db)

    # Delete one disease to simulate a partial or interrupted seed
    deleted_disease_name = _DISEASE_NAMES[0]
    disease_to_delete = (
        await test_db.execute(
            select(Disease).where(Disease.name == deleted_disease_name)
        )
    ).scalar_one()
    await test_db.delete(disease_to_delete)
    await test_db.commit()

    # Verify one is missing
    diseases = (await test_db.execute(select(Disease))).scalars().all()
    assert len(diseases) == len(_DISEASE_NAMES) - 1

    # Run seeder again
    await ensure_disease_catalog(test_db)

    # Verify missing disease was restored
    diseases_restored = (await test_db.execute(select(Disease))).scalars().all()
    assert len(diseases_restored) == len(_DISEASE_NAMES)
    assert any(d.name == deleted_disease_name for d in diseases_restored)
