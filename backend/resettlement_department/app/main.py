from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router
import time
from fastapi.responses import JSONResponse
from core.logger import logger



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD", "TRACE", "CONNECT"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"→ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"! {request.method} {request.url.path} failed: {str(exc)}")
        raise
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"← {request.method} {request.url.path} | Status: {response.status_code} | {process_time:.0f}ms")
    
    return response

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"!!! Error in {request.url.path}: {str(exc)}", context=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application started")