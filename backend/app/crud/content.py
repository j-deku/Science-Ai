from sqlalchemy.orm import Session
from app.models.content import Content




def create_content(db: Session, content_in):
    db_content = Content(**content_in.dict())
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content




def get_contents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Content).offset(skip).limit(limit).all()




def get_content(db: Session, content_id: int):
    return db.query(Content).filter(Content.id == content_id).first()