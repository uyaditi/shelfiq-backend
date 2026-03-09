from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routes import chat, rag
from routes.data import router as data_router
from routes import oos_detect

load_dotenv()

app = FastAPI(title="Retail Copilot API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(data_router, prefix="/api")
app.include_router(oos_detect.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}