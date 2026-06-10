from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .routers import predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sign Language Recognition API", version="1.0")

# CORS – allow React dev server (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api", tags=["prediction"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": True}