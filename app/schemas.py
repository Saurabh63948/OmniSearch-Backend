from pydantic import BaseModel ,EmailStr
from typing import Optional

#Signup/Login data 
class UserCreate(BaseModel):
   email:EmailStr
   password:str

#res that user get with hashpaswword

class UserResponse(BaseModel):
   id:int
   email:EmailStr

   class Config:
      from_attributes=True

#After login successful user found the token
class Token(BaseModel):
   access_token:str
   token_type:str
   user_id:int         