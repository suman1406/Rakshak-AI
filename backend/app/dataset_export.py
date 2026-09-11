"""Create a private, consent-filtered training manifest from expert-reviewed data.

Usage: python -m app.dataset_export --output /private/manifest.jsonl
No raw media is copied, and no data is sent to an external service.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import async_session_factory
from app.models.identity import User
from app.models.prediction import VideoDiagnosis
from app.models.verification import VerifiedLabel
from app.models.video import Video


async def eligible_records(db):
    rows = (await db.execute(select(VerifiedLabel, VideoDiagnosis, Video)
        .options(selectinload(VerifiedLabel.disease), selectinload(Video.frames))
        .join(VideoDiagnosis, VerifiedLabel.video_diagnosis_id == VideoDiagnosis.id)
        .join(Video, VideoDiagnosis.video_id == Video.id)
        .join(User, Video.uploaded_by == User.id)
        .where(User.training_consent.is_(True), Video.media_deleted_at.is_(None))
        .order_by(VerifiedLabel.created_at.desc()))).all()
    records, seen = [], set()
    for label, prediction, video in rows:
        if video.id in seen:
            continue
        seen.add(video.id)
        # Group every observation from a field together to avoid train/test leakage.
        group = hashlib.sha256(video.field_id.encode()).hexdigest()
        bucket = int(group[:8], 16) % 100
        split = 'train' if bucket < 80 else 'validation' if bucket < 90 else 'test'
        records.append({'schema_version': 'rakshak-reviewed-v1', 'video_id': video.id, 'field_group': group, 'split': split,
            'video_reference': video.storage_path, 'frame_references': [frame.storage_path for frame in video.frames if frame.is_selected],
            'crop': 'soybean', 'expert_label_id': label.id, 'disease': 'healthy' if label.is_healthy_override else label.disease.name if label.disease else 'unknown_other',
            'severity': label.severity_level, 'label_is_gold': label.is_gold, 'ai_suggestion_was_shown': label.ai_suggestion_was_shown,
            'reviewed_at': label.created_at.isoformat(), 'ai_confidence': prediction.confidence, 'aggregation_version': prediction.aggregation_model_version})
    return records


async def main(output):
    async with async_session_factory() as db:
        records = await eligible_records(db)
    path = Path(output)
    # Never silently overwrite an earlier exported dataset version.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        for record in records:
            stream.write(json.dumps(record) + '\n')
    print(json.dumps({'records': len(records), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'output': str(path)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    asyncio.run(main(parser.parse_args().output))
