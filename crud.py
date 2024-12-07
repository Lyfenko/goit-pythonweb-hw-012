import os
import json
from sqlalchemy.orm import Session
from fastapi import UploadFile
from datetime import datetime, timedelta
from jose import jwt, JWTError
from datetime import date
from database import redis_client
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import cloudinary
import cloudinary.uploader

import models
import schemas

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user.

    Args:
        db (Session): The database session.
        user (schemas.UserCreate): The user data.

    Returns:
        models.User: The created user.
    """
    db_user = models.User(email=user.email)
    db_user.set_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate a verification token
    verification_token = str(uuid.uuid4())

    # Send the verification email
    send_verification_email(user.email, verification_token)

    return db_user


def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by email.

    Args:
        db (Session): The database session.
        email (str): The email of the user.

    Returns:
        models.User: The user with the specified email.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user.

    Args:
        db (Session): The database session.
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
        models.User: The authenticated user.
    """
    # Check if the user details are present in the cache
    cached_user = redis_client.get(email)
    if cached_user:
        user_data = json.loads(cached_user)
        user = models.User(**user_data)
    else:
        # If user details are not in the cache, fetch from the database
        user = get_user_by_email(db, email)
        if user:
            # Store the user details in the cache
            redis_client.set(email, json.dumps(user.dict()))

    if not user:
        return False

    if not user.check_password(password):
        return False

    # Update the cached user details
    redis_client.set(email, json.dumps(user.dict()))

    return user


def create_access_token(email: str):
    """
    Create an access token.

    Args:
        email (str): The email associated with the token.

    Returns:
        str: The generated access token.
    """
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(email: str):
    """
    Create a refresh token.

    Args:
        email (str): The email associated with the token.

    Returns:
        str: The generated refresh token.
    """
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, password_reset: bool = False):
    """
    Verify a token.

    Args:
        token (str): The token to verify.
        password_reset (bool): Flag indicating if the token is for password reset.

    Returns:
        str: The email associated with the token, or None if the token is invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise JWTError
        return email
    except JWTError:
        return None


def get_current_user(token: str = None, db: Session = None):
    """
    Get the current authenticated user.

    Args:
        token (str): The access token.
        db (Session): The database session.

    Returns:
        models.User: The current authenticated user.
    """
    if not token:
        return None
    email = verify_token(token)
    if not email:
        return None
    user = get_user_by_email(db, email)
    return user


def get_current_user_token(token: str = None):
    """
    Get the current user token.

    Args:
        token (str): The access token.

    Returns:
        str: The current user token.
    """
    if not token:
        return None
    email = verify_token(token)
    if not email:
        return None
    access_token = create_access_token(email)
    return access_token


def get_user_contacts(db: Session, user_id: int):
    """
    Get contacts of a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[models.Contact]: The contacts of the user.
    """
    return db.query(models.Contact).filter(models.Contact.user_id == user_id).all()


def create_contact(db: Session, contact: schemas.ContactCreate):
    """
    Create a new contact.

    Args:
        db (Session): The database session.
        contact (schemas.ContactCreate): The contact data.

    Returns:
        models.Contact: The created contact.
    """
    db_contact = models.Contact(
        name=contact.name,
        surname=contact.surname,
        email=contact.email,
        phone=contact.phone,
        birthday=contact.birthday,
        additional_data=contact.additional_data,
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all contacts.

    Args:
        db (Session): The database session.
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to retrieve.

    Returns:
        List[models.Contact]: The contacts.
    """
    return db.query(models.Contact).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int):
    """
    Get a contact by ID.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact.

    Returns:
        models.Contact: The contact with the specified ID.
    """
    return db.query(models.Contact).get(contact_id)


def update_contact(
    db: Session,
    db_contact: models.Contact,
    contact: schemas.ContactUpdate,
    avatar: UploadFile = None,
):
    """
    Update a contact.

    Args:
        db (Session): The database session.
        db_contact (models.Contact): The contact to update.
        contact (schemas.ContactUpdate): The updated contact data.
        avatar (UploadFile, optional): The avatar file.

    Returns:
        models.Contact: The updated contact.
    """
    # Update contact fields
    for field in contact.dict(exclude_unset=True):
        setattr(db_contact, field, contact.dict()[field])

    # Update avatar if provided
    if avatar:
        result = cloudinary.uploader.upload(avatar.file, folder="avatars")
        db_contact.avatar_url = result.get("secure_url")

    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, db_contact: models.Contact):
    """
    Delete a contact.

    Args:
        db (Session): The database session.
        db_contact (models.Contact): The contact to delete.

    Returns:
        models.Contact: The deleted contact.
    """
    db.delete(db_contact)
    db.commit()
    return db_contact


def search_contacts(db: Session, query: str):
    """
    Search contacts based on a query.

    Args:
        db (Session): The database session.
        query (str): The search query.

    Returns:
        List[models.Contact]: The matched contacts.
    """
    return (
        db.query(models.Contact)
        .filter(
            models.Contact.name.ilike(f"%{query}%")
            | models.Contact.surname.ilike(f"%{query}%")
            | models.Contact.email.ilike(f"%{query}%")
        )
        .all()
    )


def birthday_contacts(db: Session):
    """
    Get contacts with birthdays in the next week.

    Args:
        db (Session): The database session.

    Returns:
        List[models.Contact]: The contacts with upcoming birthdays.
    """
    today = date.today()
    next_week = today.replace(day=today.day + 7)
    return (
        db.query(models.Contact)
        .filter(models.Contact.birthday >= today, models.Contact.birthday <= next_week)
        .all()
    )


def send_verification_email(email: str, token: str):
    """
    Send a verification email to the specified email address.

    Args:
        email (str): The email address to send the verification email to.
        token (str): The verification token.
    """
    message = Mail(
        from_email="lyfenko@meta.ua",
        to_emails=email,
        subject="Email Verification",
        html_content=f"Click the link to verify your email: <a href='http://127.0.0.1:8000/verify/{token}'>Verify Email</a>",
    )
    try:
        sg = SendGridAPIClient("SENDGRID_API_KEY")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))


def send_password_reset_email(email: str, token: str):
    """
    Send a password reset email to the specified email address.

    Args:
        email (str): The email address to send the password reset email to.
        token (str): The password reset token.
    """
    message = Mail(
        from_email="lyfenko@meta.ua",
        to_emails=email,
        subject="Password Reset",
        html_content=f"Click the link to reset your password: <a href='http://127.0.0.1:8000/reset-password/{token}'>Reset Password</a>",
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))