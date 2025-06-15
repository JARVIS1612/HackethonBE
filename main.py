from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma, register
from Modules.authentication import auth
from Modules.movies import movies
from Modules.user_activity import router as user_activity
from Modules.vector_search import vector_search

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
app.include_router(user_activity)
app.include_router(vector_search)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}