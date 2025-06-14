from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from Models.auth_models import Users as UserSchema
from Models.auth_models import Login as LoginSchema
from Helpers.custom_response import unified_response
from Helpers.jwt_helpers import create_access_token, hash_password, verify_password, verify_access_token
from database.user_db import create_user_in_db, find_user_by_email_or_username

auth = APIRouter(prefix="/auth", tags=["Auth"])

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization.split(" ")[1]
    user = verify_access_token(token)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user.id, "email": user.email, "username": user.username}

@auth.post("/signup")
async def create_user(user: UserSchema):
    hashed_password = hash_password(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password

    response, error = create_user_in_db(user_data)
    if response:
        return unified_response(True, "User created successfully", data=response)

    if "Unique constraint failed on the fields: (`email`)" in error:
        return unified_response(False, "Email already exists", status_code=400)

    if "Unique constraint failed on the fields: (`username`)" in error:
        return unified_response(False, "Username already exists", status_code=400)

    return unified_response(False, f"An error occurred: {error}", status_code=500)

@auth.post("/login")
async def login(user: LoginSchema):
    response = find_user_by_email_or_username(email=user.email, username=user.username)
    if not response:
        return unified_response(False, "User not found", status_code=404)

    if verify_password(user.password, response.password):
        token_data = {"email": response.email, "id": response.id}
        token = create_access_token(token_data)
        return unified_response(True, "Login successful", data=token)
    else:
        return unified_response(False, "Invalid password", status_code=401)

@auth.get("/verify-token")
async def verify_token(authorization: Optional[str] = Header(None)):
    print(authorization)
    if not authorization or not authorization.startswith("Bearer "):
        return unified_response(False, "Invalid token format", status_code=401)
    
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    
    if not payload:
        return unified_response(False, payload, status_code=401)
    
    return unified_response(True, "Token is valid", data=payload, status_code=200)
    
    