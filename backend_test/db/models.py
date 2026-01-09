from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    login = Column(String, unique = True, index = True, nullable = False)
    name = Column(String, nullable = False)
    surname = Column(String, nullable = False)
    age = Column(Integer, nullable = False)
    password_hash = Column(String, nullable= False)
    role = Column(String, nullable = False, default = "user")