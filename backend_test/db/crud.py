from sqlalchemy.orm import Session
from . import models, shemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated = "auto") # argon2 можна змінити

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()

def get_users(db:Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: shemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        login = user.login,
        name = user.name,
        surname = user.surname,
        age = user.age,
        password_hash = hashed_password,
        role = "user"
    )
    # user.dict() -> {"login": "jfh", "name": "jfg"} -> login = "jfh", name = "jfg"
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, login: str, user: shemas.UserCreate):
    db_user = get_user_by_login(db, login)
    if not db_user:
        return None
    db_user.login = user.login
    db_user.name = user.name
    db_user.surname = user.surname
    db_user.age = user.age 
    if user.password:
        db_user.password_hash = pwd_context.hash(user.password)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, login: str):
    db_user = get_user_by_login(db, login)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password) # True / False

def get_user_by_credentials(db: Session, login: str, password: str):
    user = get_user_by_login(db, login)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user