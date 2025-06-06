from pydantic import BaseModel

class Users(BaseModel):
    username: str
    email: str
    password: str