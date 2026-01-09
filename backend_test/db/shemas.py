from pydantic import BaseModel

class UserBase(BaseModel):
    login: str
    name : str
    surname: str
    age: int

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    login: str | None = None
    role:  str | None = None
