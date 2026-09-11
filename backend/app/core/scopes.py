from sqlalchemy import false, or_, and_, exists, select
from sqlalchemy.sql.elements import ColumnElement

from ..models.farm import Farm
from ..models.identity import User, UserRole


def _scope(current_user: User, owner_column: ColumnElement, org_column: ColumnElement) -> ColumnElement:
    if current_user.role == UserRole.farmer:
        return owner_column == current_user.id
    if current_user.org_id:
        return org_column == current_user.org_id
    return false()


def farm_scope(current_user: User) -> ColumnElement:
    return _scope(current_user, Farm.owner_user_id, Farm.org_id)


def field_scope(current_user: User) -> ColumnElement:
    return farm_scope(current_user)


def video_scope(current_user: User) -> ColumnElement:
    if current_user.role == UserRole.agronomist:
        from ..models.prediction import VideoDiagnosis
        from ..models.verification import ReviewWorkItem
        from ..models.video import Video
        requested = exists(select(ReviewWorkItem.id).join(VideoDiagnosis, VideoDiagnosis.id == ReviewWorkItem.video_diagnosis_id).where(VideoDiagnosis.video_id == Video.id, or_(ReviewWorkItem.assigned_agronomist_id.is_(None), ReviewWorkItem.assigned_agronomist_id == current_user.id))).correlate(Video)
        return or_(farm_scope(current_user), and_(Farm.org_id.is_(None), requested))
    return farm_scope(current_user)


def diagnosis_scope(current_user: User) -> ColumnElement:
    if current_user.role == UserRole.agronomist:
        from ..models.prediction import VideoDiagnosis
        from ..models.verification import ReviewWorkItem
        requested = exists(select(ReviewWorkItem.id).where(ReviewWorkItem.video_diagnosis_id == VideoDiagnosis.id, or_(ReviewWorkItem.assigned_agronomist_id.is_(None), ReviewWorkItem.assigned_agronomist_id == current_user.id))).correlate(VideoDiagnosis)
        return or_(farm_scope(current_user), and_(Farm.org_id.is_(None), requested))
    return farm_scope(current_user)
