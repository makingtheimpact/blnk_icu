from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.url import Base
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "blnkcatdb")
DB_PASSWORD = os.getenv("DB_PASSWORD", "EzEbKOB1Q.MbDR#8=zGm$5rXSSjnhlBCl")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "blnk_icu")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Blnk URL Shortener",
             description="A simple URL shortener service",
             version="1.0.0")

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