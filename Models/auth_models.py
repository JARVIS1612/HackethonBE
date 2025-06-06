from pydantic import BaseModel

class Users(BaseModel):
    username: str
    email: str
    password: str

class Login(BaseModel):
    username: str | None = None
    password: str
    email: str | None = None