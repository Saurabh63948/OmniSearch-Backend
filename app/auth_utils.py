from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_db
import os
from .models import User
from dotenv import load_dotenv
load_dotenv()


pwd_context =CryptContext(schemes=["bcrypt"],deprecated="auto")

#jwt configuration
SECRET_KEY =os.getenv('SECRET_KEY',"your_fallback_secret_key_change_this")
ALGORITHM ='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES =1440 #24 Hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password:str):
  """it will make password hash and secure."""
  return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str):
  """it will compaire the plain passord and db password"""
  return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict):
    """It will generate a jwt token for the user after the user login"""
    to_encode = data.copy()
    # 1. UUID check and conversion

    if "id" in to_encode:
        to_encode["id"] = str(to_encode["id"])
        
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user