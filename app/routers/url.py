import random
import string
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.url import URL
from app.main import SessionLocal, limiter
from fastapi.responses import RedirectResponse
import httpx
import os
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "6Lc7i6EqAAAAABMMNoTnsbZ0RkJRbNGX7kbCmo3Q")

class URLResponse(BaseModel):
    short_url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_recaptcha(recaptcha_response: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response,
            },
        )
        result = response.json()
        logger.info(f"reCAPTCHA response: {result}")
        # Lower threshold to 0.1 for testing
        return result.get("success", False) and result.get("score", 0) > 0.5

@router.post("/shorten", response_model=URLResponse)
@limiter.limit("5/minute")
async def shorten_url(
    request: Request,
    original_url: str = Form(...),
    recaptcha_response: str = Form(..., alias="g-recaptcha-response"),
    db: Session = Depends(get_db)
):
    # Log the received token
    logger.info(f"Received reCAPTCHA token: {recaptcha_response[:20]}...")
    
    # Verify reCAPTCHA
    verification_result = await verify_recaptcha(recaptcha_response)
    if not verification_result:
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed or score too low")

    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    new_url = URL(original_url=original_url, short_code=short_code)
    db.add(new_url)
    db.commit()
    return {"short_url": f"http://localhost:8000/{short_code}"}

@router.get("/{short_code}")
@limiter.limit("30/minute")
def redirect_url(request: Request, short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=url.original_url)
