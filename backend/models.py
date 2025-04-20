from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User model representing a bot user.
    
    Attributes:
        id (int): Telegram user ID, primary key
        username (str): Telegram username, optional
        first_name (str): User's first name
        last_name (str): User's last name, optional
        swapped (bool): Flag indicating if user is in RU-EN mode
        current_set (int): Current word set number user is working with
    """
    __tablename__ = "users"
    id = Column(BigInteger(), index=True, nullable=False, primary_key=True)
    username = Column(String(), default="")
    first_name = Column(String())
    last_name = Column(String(), default="")
    swapped = Column(Boolean(), default=False)
    current_set = Column(Integer(), default=1)


class Word(Base):
    """Word model representing a vocabulary word.
    
    Attributes:
        id (int): Unique word ID, auto-incrementing primary key
        user_id (int): ID of the user who owns this word
        word (str): The word itself
        translated (str): Translation of the word
        definitions (str): Definitions of the word
        set (int): Set number this word belongs to
        flag (bool): Flag indicating if word is marked for special attention
    """
    __tablename__ = "words"
    id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger(), ForeignKey("users.id"))
    word = Column(String())
    translated = Column(String())
    definitions = Column(String(), nullable=True, default=None)
    set = Column(Integer())
    flag = Column(Boolean(), default=False)