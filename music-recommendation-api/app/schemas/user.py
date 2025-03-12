from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    firebase_uid: str
    email: EmailStr
    username: str


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: int
    firebase_uid: str
    email: EmailStr
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    pass


class FirebaseUserProfile(BaseModel):
    uid: str
    email: EmailStr
    email_verified: bool
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    disabled: bool = False


class UserRegistration(BaseModel):
    firebase_uid: str
    email: EmailStr
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'username must be alphanumeric'
        return v