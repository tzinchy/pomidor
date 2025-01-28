<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router

=======
#from fastapi_cache import FastAPICache
from fastapi import FastAPI

#from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router

#FastAPICache.init(InMemoryBackend())

>>>>>>> e4a872d7a5ab3cdd0182820aee14f75ad9ddc1d6
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router  
)
