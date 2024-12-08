from fastapi import FastAPI
from api.v1.api.router import router as auth

app = FastAPI() 

app.include_router(auth)
