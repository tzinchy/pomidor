from fastapi import FastAPI
from api.v1.endpoints.auth_endpoints import router as auth_roter 
from api.v1.endpoints.user_endpoints import router as user_router
from fastapi.templating import Jinja2Templates

app = FastAPI(root_path='/dgi') 

app.include_router(auth_roter)
app.include_router(user_router)

<<<<<<< HEAD

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
=======
# Укажите директорию для шаблонов
templates = Jinja2Templates(directory="app/templates")
>>>>>>> f787b29 (add frontend table view with tree)
