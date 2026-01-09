from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from db.models import User, Base 
from db.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto") # bcrypt
hashed_password = pwd_context.hash("userpass") 

db = SessionLocal()

admin_user = User(
    login="user",
    name="User",
    surname="User",
    age=30,
    password_hash=hashed_password,
    role="user" 
)

db.add(admin_user)
db.commit()
db.refresh(admin_user)
db.close()

print("User створено з id:", admin_user.id)