from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma, register
from Modules.authentication import auth
from Modules.movies import movies

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# SQL Database
db = Prisma()
db.connect()
register(db)

app.include_router(auth)
app.include_router(movies)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}