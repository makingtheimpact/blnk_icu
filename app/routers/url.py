import random
import string
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.url import URL
from app.main import SessionLocal
from fastapi.responses import RedirectResponse

router = APIRouter()

class URLResponse(BaseModel):
    short_url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/shorten", response_model=URLResponse)
def shorten_url(original_url: str = Form(...), db: Session = Depends(get_db)):
    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    new_url = URL(original_url=original_url, short_code=short_code)
    db.add(new_url)
    db.commit()
    return {"short_url": f"http://localhost:8000/{short_code}"}

@router.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=url.original_url)
