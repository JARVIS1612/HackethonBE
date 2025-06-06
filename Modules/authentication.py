from fastapi import APIRouter
import bcrypt
from Models.models import Users as UserSchema
from Models.models import Login as LoginSchema
from Helpers.custom_response import unified_response
from Helpers.jwt_helpers import create_access_token, hash_password, verify_password
from prisma.models import Users as PrismaUsers
from prisma.errors import UniqueViolationError

auth = APIRouter(prefix="/auth", tags=["Auth"])

@auth.post("/signup")
async def create_user(user: UserSchema):
    try:
        hashed_password = hash_password(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password

        response = PrismaUsers.prisma().create(data=user_data)
        return unified_response(True, "User created successfully", data=response.dict())

    except UniqueViolationError as error_msg:
        if "Unique constraint failed on the fields: (`email`)" in str(error_msg):
            return unified_response(False, "Email already exists", status_code=400)

        if "Unique constraint failed on the fields: (`username`)" in str(error_msg):
            return unified_response(False, "Username already exists", status_code=400)

    except Exception as e:
        return unified_response(False, f"An error occurred: {str(e)}", status_code=500)

@auth.post("/login")
async def login(user: LoginSchema):
    response = ""

    if user.email:
        response = PrismaUsers.prisma().find_first(where={"email": user.email})
    else:
        response = PrismaUsers.prisma().find_first(where={"username": user.username})
    if not response:
        return unified_response(False, "User not found", status_code=404)

    if verify_password(user.password, response.password):
        token_data = {"sub": response.email, "id": response.id}
        token = create_access_token(token_data)
        return unified_response(True, "Login successful", data=create_access_token({"token": token}))
    else:
        return unified_response(False, "Invalid password", status_code=401)