from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router as v1_router 

app = FastAPI()


origins = [
    "http://localhost",  
    "http://127.0.0.1",
    "http://10.9.96.160:3001",
    "http://dsa.mlc.gov",
    "http://auth.dsa.mlc.gov",
    "http://doccontrol.dsa.mlc.gov",
    "https://dsa.mlc.gov",
    "https://auth.dsa.mlc.gov",
    "https://doccontrol.dsa.mlc.gov",
    "https://auth.dsa.mlc.gov",
    "https://testdsa.mlc.gov",
    "https://auth.testdsa.mlc.gov",
    "https://doccontrol.testdsa.mlc.gov",
    "https://rstl.testdsa.mlc.gov",
    "https://up.testdsa.mlc.gov",
    "http://10.9.96.162:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

