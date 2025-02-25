#from fastapi_cache import FastAPICache
from fastapi import FastAPI

#from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router

#FastAPICache.init(InMemoryBackend())

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Явное указание методов,
    allow_headers=["*"],
)

app.include_router(
    router  
)

