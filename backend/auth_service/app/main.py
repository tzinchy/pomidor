from fastapi import FastAPI
from api.v1.endpoints.auth_endpoints import router as auth_roter 
from api.v1.endpoints.user_endpoints import router as user_router

app = FastAPI(root_path='/dgi') 

app.include_router(auth_roter)
app.include_router(user_router)


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)