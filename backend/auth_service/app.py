from fastapi import FastAPI
from auth.router import router as auth, test

app = FastAPI() 

app.include_router(auth)
app.include_router(test)
