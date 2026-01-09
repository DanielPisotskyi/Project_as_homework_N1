from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db import models, shemas, crud
from db.database import SessionLocal, engine, Base
from db.security import *
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse

Base.metadata.create_all(bind = engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None}
    )

@app.post("/login", response_class = HTMLResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db), request: Request = None):
    user = crud.get_user_by_credentials(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неправильний логін або пароль"}
    )
    access_token = create_token(data = {"sub": user.login, "role": user.role})
    response = RedirectResponse(url = "/", status_code=303)
    response.set_cookie(key = "access_token", value = access_token)
    return response

@app.post("/token", response_model=shemas.Token)
def login_for_api_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_credentials(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_token(data={"sub": user.login, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/add/", response_model=shemas.UserRead)
def add_user(user: shemas.UserCreate, db: Session = Depends(get_db), current_user: shemas.TokenData = Depends(get_current_user)):
    existing = crud.get_user_by_login(db, user.login)
    if existing:
        raise HTTPException(status_code=400, detail= "user already exists")
    db_user = crud.create_user(db, user)
    return db_user

@app.put("/user/edit/{login}", response_model=shemas.UserRead)
def edit_user(login: str, user: shemas.UserCreate, db: Session = Depends(get_db), current_user: shemas.TokenData = Depends(get_current_user)):
    if current_user.login != login and current_user.role != "admin":
        raise HTTPException(status_code=403, detail = "Not enough permissions")
    db_user = crud.update_user(db, login, user)
    if not db_user:
        return HTTPException(status_code=400, detail= "user is not exists")
    return db_user
    

@app.delete("/user/delete/{login}")
def delete_user(login: str, db: Session = Depends(get_db), current_user: shemas.TokenData = Depends(get_current_admin)):
    ok = crud.delete_user(db, login)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
