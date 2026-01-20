from typing import List

from fastapi import APIRouter

from app import schemas
from app.dependencies import db_dependency, user_dependency
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("/", response_model=schemas.MemberResponse)
def create_member(
    member_in: schemas.MemberCreate,
    db: db_dependency,
    current_user: user_dependency
):
    return MemberService.create(db, member_in)

@router.get("/", response_model=List[schemas.MemberResponse])
def get_all_members(db: db_dependency, skip: int = 0, limit: int = 10):
    return MemberService.get_all(db, skip, limit)

@router.get("/{member_id}", response_model=schemas.MemberResponse)
def get_member(member_id: int, db: db_dependency):
    return MemberService.get_one(db, member_id)

@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    db: db_dependency,
    current_user: user_dependency
):
    return MemberService.delete(db, member_id)