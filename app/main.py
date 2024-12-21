from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.url import Base
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "blnkcatdb")
DB_PASSWORD = os.getenv("DB_PASSWORD", "EzEbKOB1QMbDR89zGm5rXSSjnhlBCl")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "blnk_icu")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="blnk.icu URL Shortener & QR Code Generator",
             description="A simple URL shortener service",
             version="1.0.0")

# Add limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Create tables
Base.metadata.create_all(bind=engine)

from app.routers import url
app.include_router(url.router)