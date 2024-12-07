from sqlalchemy import Column, Integer, String, Date
from database import Base
from passlib.hash import bcrypt


class Contact(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Indicates whether the user account is active.
        is_verified (bool): Indicates whether the user's email is verified.
        contacts (List[Contact]): The list of contacts associated with the user.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    surname = Column(String(50), index=True)
    email = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    birthday = Column(Date)
    additional_data = Column(String(200))


class User(Base):
    """
    Represents a contact associated with a user.

    Attributes:
        id (int): The unique identifier for the contact.
        name (str): The name of the contact.
        surname (str): The surname of the contact.
        email (str): The email address of the contact.
        phone (str, optional): The phone number of the contact (optional).
        birthday (date, optional): The birthday of the contact (optional).
        additional_data (str, optional): Additional data about the contact (optional).
        owner (User): The user who owns the contact.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password_hash = Column(String(128))

    def set_password(self, password: str):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password: str):
        return bcrypt.verify(password, self.password_hash)
