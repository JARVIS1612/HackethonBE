from fastapi import APIRouter
import bcrypt
from Models.models import Users as UserSchema
from Helpers.custom_response import unified_response
from prisma.models import Users as PrismaUsers

auth = APIRouter(prefix="/auth", tags=["Auth"])

@auth.post("/signup")
async def create_user(user: UserSchema):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_data = user.model_dump()
    user_data["password"] = hashed_password.decode('utf-8')
    
    response = PrismaUsers.prisma().create(data=user_data)
    return unified_response(True, "User created successfully", data=response.dict())

@auth.post("/login")
async def login(user: UserSchema):
    response = PrismaUsers.prisma().find_first(where={"email": user.email})
    if not response:
        return unified_response(False, "User not found", status_code=404)

    if bcrypt.checkpw(user.password.encode('utf-8'), response.password.encode('utf-8')):
        return unified_response(True, "Login successful", data={"email": response.email})
    else:
        return unified_response(False, "Invalid password", status_code=401)