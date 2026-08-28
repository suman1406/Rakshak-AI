from sqlalchemy import false
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
    return farm_scope(current_user)


def diagnosis_scope(current_user: User) -> ColumnElement:
    return farm_scope(current_user)
