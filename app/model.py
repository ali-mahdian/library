from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserType(str, Enum):
    member = "member"
    librarian = "librarian"


class UserSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    role: UserType = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "alivmahdian@gmail.com",
                "password": "password",
                "role": "member"
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "alivmahdian@gmail.com",
                "password": "password"
            }
        }


class BookSchema(BaseModel):
    title: str = Field(...)
    author: str = Field(...)
    des: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to Algorithm",
                "author": "CLRS",
                "des": "basic & advanced book for algorithm & data structure"
            }
        }


class BookOperationSchema(BaseModel):
    title: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to Algorithm"
            }
        }
