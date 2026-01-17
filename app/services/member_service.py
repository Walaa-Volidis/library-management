from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models, schemas

class MemberService:
    @staticmethod
    def create(db: Session, member_in: schemas.MemberCreate):
        existing_member = db.query(models.member.Member).filter(models.member.Member.email == member_in.email).first()
        if existing_member:
            raise HTTPException(status_code=409, detail="Email already registered")
        member_data = member_in.model_dump()
        db_member = models.member.Member(**member_data)    
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    
    @staticmethod
    def get_all(db: Session):
        return db.query(models.member.Member).all()

    @staticmethod
    def get_one(db: Session, member_id: int):
        db_member = db.query(models.member.Member).filter(models.member.Member.id == member_id).first()
        if not db_member:
            raise HTTPException(status_code=404, detail="Member not found")
        return db_member

    @staticmethod
    def delete(db: Session, member_id: int):
           db_member = db.query(models.member.Member).filter(models.member.Member.id == member_id).first()
           if not db_member:
            raise HTTPException(status_code=404, detail="Member not found")
            
           db.delete(db_member)
           db.commit()
           return {"message": f"Member with id {member_id} has been deleted successfully"}

