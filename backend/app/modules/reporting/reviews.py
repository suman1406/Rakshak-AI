from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.verification import ReviewWorkItem, VerifiedLabel


async def review_summary(db, diagnosis_id):
    item = (await db.execute(select(ReviewWorkItem).where(ReviewWorkItem.video_diagnosis_id == diagnosis_id))).scalar_one_or_none()
    label = (await db.execute(select(VerifiedLabel).options(selectinload(VerifiedLabel.disease), selectinload(VerifiedLabel.agronomist)).where(VerifiedLabel.video_diagnosis_id == diagnosis_id).order_by(VerifiedLabel.created_at.desc()).limit(1))).scalar_one_or_none()
    if label:
        return {'status': 'completed', 'reviewed_at': label.created_at.isoformat(), 'reviewer': label.agronomist.display_name or 'Agronomist',
                'disease': 'No clear disease symptoms' if label.is_healthy_override else label.disease.name if label.disease else 'Uncertain',
                'severity_level': label.severity_level, 'notes': label.notes}
    return None if item is None else {'status': item.status.value}
