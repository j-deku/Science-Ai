from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash




def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()




def create_user(db: Session, email: str, password: str):
    db_user = User(email=email, hashed_password=get_password_hash(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user