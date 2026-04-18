from pydantic import BaseModel,EmailStr
from typing import Optional
from app.schemas import UserCreate,UserResponse
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.database import get_db
from ..models import User
from ..auth_utils import verify_password,create_access_token,hash_password,get_current_user
from fastapi.security import OAuth2PasswordRequestForm 
router =APIRouter(
  prefix="/auth",
  tags=["Authentication"]
)

# ---1 .SIGNUP Logic (creating new account)---
@router.post("/signup",status_code=status.HTTP_201_CREATED)
def signup(user:UserCreate , db:Session=Depends(get_db)):
  #check for existing user
  existing_user = db.query(User).filter(User.email == user.email).first()
  if existing_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='Email already registered'
    )
  #hashed password
  hashed_pwd=hash_password(user.password)
  new_user=User(email=user.email,hashed_password=hashed_pwd)
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return {"message":"User created successfully","user_id":new_user.id}

# ---2 .Login logic 
@router.post("/login")
def login(user_credentials:UserCreate,db:Session =Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_credentials.email).first()

    # Password verify karein
    if not db_user or not verify_password(user_credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # generate Token
    access_token = create_access_token(
        data={"sub": db_user.email, "id": str(db_user.id)}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "id": current_user.id,
        "status": "Authenticated"
    }