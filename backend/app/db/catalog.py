"""
catalog.py — Idempotent Disease Catalog Seeder

Ensures the MVP soybean disease taxonomy exists in the database at every
startup.  The check is a lightweight SELECT — if records already exist the
function returns immediately without touching the database again.

Taxonomy (locked, v1.1-mvp5 — must stay in sync with classifier.py):
  Crop:     Soybean (taxonomy_version="v1.0")
  Diseases:
    - Soybean Rust          ← soybean_rust
    - Frogeye Leaf Spot     ← soybean_frogeye_leaf_spot
    - Sudden Death Syndrome ← soybean_bacterial_blight (ASDID label)
    - Healthy               ← soybean_healthy

The ingestion service maps classifier output slugs to these Disease.name
values (see ingestion/service.py › taxonomy_names dict).  Any change to
names here MUST be mirrored there and vice-versa.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.farm import Crop, Disease

logger = logging.getLogger("rakshak")

# ──────────────────────────────────────────────────────────────────────────────
# Locked catalog definition (v1.1-mvp5)
# ──────────────────────────────────────────────────────────────────────────────
_CATALOG_TAXONOMY_VERSION = "v1.0"

_CROP_NAME = "Soybean"

# Disease names must match the `taxonomy_names` mapping in ingestion/service.py
_DISEASE_NAMES: list[str] = [
    "Soybean Rust",
    "Frogeye Leaf Spot",
    "Sudden Death Syndrome",
    "Healthy",
]


async def ensure_disease_catalog(db: AsyncSession) -> None:
    """
    Idempotently seed the soybean crop and its four MVP diseases.

    Safe to call on every startup:
      - If the Crop row already exists (unique on name+taxonomy_version) the
        function returns without any INSERT.
      - If the Crop exists but a Disease is missing it is added individually,
        making the function resilient to partial seeds from previous deploys.

    Args:
        db: An active async SQLAlchemy session (caller owns commit/rollback).
    """
    # ── 1. Upsert Soybean Crop ─────────────────────────────────────────────
    crop: Crop | None = (
        await db.execute(
            select(Crop).where(
                Crop.name == _CROP_NAME,
                Crop.taxonomy_version == _CATALOG_TAXONOMY_VERSION,
            )
        )
    ).scalar_one_or_none()

    if crop is None:
        crop = Crop(
            name=_CROP_NAME,
            taxonomy_version=_CATALOG_TAXONOMY_VERSION,
            active=True,
        )
        db.add(crop)
        await db.flush()   # generate crop.id before Disease FKs reference it
        logger.info("Disease catalog: created Crop '%s' (%s)", _CROP_NAME, _CATALOG_TAXONOMY_VERSION)
    else:
        logger.debug("Disease catalog: Crop '%s' already present — skipping", _CROP_NAME)

    # ── 2. Upsert each Disease ─────────────────────────────────────────────
    for disease_name in _DISEASE_NAMES:
        existing: Disease | None = (
            await db.execute(
                select(Disease).where(
                    Disease.crop_id == crop.id,
                    Disease.name == disease_name,
                    Disease.taxonomy_version == _CATALOG_TAXONOMY_VERSION,
                )
            )
        ).scalar_one_or_none()

        if existing is None:
            db.add(Disease(
                crop_id=crop.id,
                name=disease_name,
                taxonomy_version=_CATALOG_TAXONOMY_VERSION,
                active=True,
            ))
            logger.info("Disease catalog: created Disease '%s'", disease_name)
        else:
            logger.debug("Disease catalog: Disease '%s' already present — skipping", disease_name)

    await db.commit()
    logger.info(
        "Disease catalog: bootstrap complete — Crop=%s, Diseases=%s",
        _CROP_NAME,
        _DISEASE_NAMES,
    )
