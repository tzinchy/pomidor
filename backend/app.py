from fastapi import FastAPI
from auth.router import router as auth

app = FastAPI() 

app.include_router(auth)

