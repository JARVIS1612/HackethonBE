from fastapi import FastAPI
from prisma import Prisma, register
from Modules.authentication import auth
from Modules.movies import movies

app = FastAPI()

# SQL Database
db = Prisma()
db.connect()
register(db)

app.include_router(auth)
app.include_router(movies)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}