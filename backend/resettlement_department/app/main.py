from fastapi import FastAPI
from api.v1.endpoints.apartment_endpoints import router as apartment_router 
from api.v1.endpoints.matching_endpoints import router as matching_router

app = FastAPI()

app.include_router(apartment_router)
app.include_router(matching_router)
