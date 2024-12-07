from typing import Optional
from datetime import date
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    """
    Schema for creating a user.
    """
    password: str
    is_active: bool = True
    is_verified: bool = False


class User(UserBase):
    """
    Schema for representing a user.
    """
    id: int
    is_active: bool = True
    is_verified: bool = False
    contacts: Optional[list] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    """
    Schema for representing an access token.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for representing token data.
    """
    email: Optional[str] = None


class ContactBase(BaseModel):
    """
    Base schema for representing a contact.
    """
    name: str
    surname: str
    email: str
    phone: Optional[str] = None
    birthday: Optional[date] = None
    additional_data: Optional[str] = None


class ContactCreate(ContactBase):
    """
    Schema for creating a contact.
    """

    pass


class ContactUpdate(ContactBase):
    """
    Schema for updating a contact.
    """
    pass


class Contact(ContactBase):
    """
    Schema for representing a contact.
    """
    id: int

    class Config:
        orm_mode = True
