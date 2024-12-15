from fastapi import FastAPI
from api.v1.endpoints.router import router as apartment_router 

app = FastAPI()

app.include_router(apartment_router)


