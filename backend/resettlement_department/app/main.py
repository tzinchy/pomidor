from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router

# Инициализация FastAPI приложения
app = FastAPI()

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD", "TRACE", "CONNECT"],
    allow_headers=["*"],
)

# Подключение роутера
app.include_router(router)