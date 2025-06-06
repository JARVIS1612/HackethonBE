from fastapi import FastAPI
from prisma import Prisma, register
from prisma.models import test

app = FastAPI()

# SQL Database
# db = Prisma()
# db.connect()
# register(db)


 
@app.get("/")
async def root():
    response = test.prisma().create(data={
        'name':"test"
    })
    print(response)
    return {"message": "Hello Bigger Applications!"}
