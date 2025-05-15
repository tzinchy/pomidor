from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router as v1_router 

app = FastAPI()

app.include_router(v1_router)

origins = [
    "http://localhost",  # React Dev Server
    "http://127.0.0.1",
    "http://10.9.96.160:3001",
    "http://dsa.mlc.gov",
    "http://auth.dsa.mlc.gov"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
