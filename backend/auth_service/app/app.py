from fastapi import FastAPI
from api.v1.api.router import router as auth
from fastapi import middleware


app = FastAPI() 

app.include_router(auth)

app.middleware()