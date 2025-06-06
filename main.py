from fastapi import FastAPI
from prisma import Prisma, register
from Models.models import Users
import bcrypt
from Helpers.custom_response import unified_response
from Modules.authentication import auth
app = FastAPI()

# SQL Database
db = Prisma()
db.connect()
register(db)

app.include_router(auth)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}