from pydantic import BaseModel
from typing import Optional

class Users(BaseModel):
    username: str
    email: str
    password: str
    location: Optional[str]
    languages: Optional[str]
    genres: Optional[str]

class Login(BaseModel):
    username: Optional[str] = None
    password: str
    email: Optional[str] = None