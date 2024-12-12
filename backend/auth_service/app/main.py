from fastapi import FastAPI
from api.v1.ednpoints.router import router as auth

app = FastAPI() 

app.include_router(auth)

