from fastapi import FastAPI
from api.v1.endpoints.apartment_endpoints import router as apartment_router 

app = FastAPI()

app.include_router(apartment_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или укажите конкретные домены ["http://127.0.0.1:8001"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
