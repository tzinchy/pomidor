from fastapi import FastAPI
from api.v1.endpoints.apartment_endpoints import router as apartment_router 

app = FastAPI()

app.include_router(apartment_router)

