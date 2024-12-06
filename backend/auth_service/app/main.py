from fastapi import FastAPI
from api.v1.api.router import router as auth

app = FastAPI() 

app.include_router(auth)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)