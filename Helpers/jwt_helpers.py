from jose import jwt
from datetime import datetime, timedelta
import bcrypt
from database import user_db

SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256"
EXPIRY_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=EXPIRY_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload:
            result = user_db.find_user_by_email_or_username(email=payload.get("email"))
            return result.model_dump()
        
    except jwt.ExpiredSignatureError:
        return False
    except jwt.JWTError:
        return False
