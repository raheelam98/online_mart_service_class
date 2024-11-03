# user_service -  user_service/app/user_model.py   

from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class UserBase(SQLModel):
    user_name: str
    user_address: str
    user_country: str
    phone_number: int = Field(ge=100000000, le=9999999999999, description="Must be valid Phone Number with 9,10,12 digits" )

class UserAuth(SQLModel):
    user_email: EmailStr
    user_password : str

class UserModel(UserBase, UserAuth):
    pass 

class User(UserModel, table=True):
    user_id : Optional[int]  = Field(default=None, primary_key=True)

class Token(SQLModel):
    access_token: str
    token_type: str 

class UserUpdateModel(SQLModel):
    user_name: Optional[str]
    user_address: Optional[str]
    user_country: Optional[str]
    phone_number: Optional[int] = Field(ge=100000000, le=999999999999, description="Must be valid Phone Number with 9, 10, or 11 digits") 




