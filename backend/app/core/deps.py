from fastapi import Depends, HTTPException, status
from app.core.security import oauth2_scheme, decode_token
from app.database import get_db
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_email




def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
	payload = decode_token(token)
	sub = payload.get("sub")
	if not sub:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	user = get_user_by_email(db, sub)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
	return user