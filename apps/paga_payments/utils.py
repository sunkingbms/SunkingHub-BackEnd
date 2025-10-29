import os
from dotenv import load_dotenv
import hashlib, uuid, requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
load_dotenv()
DEFAULT_TIMEOUT = 25

def generate_reference() -> str:
    """
        Generate a unique 16-characters reference number
    """
    
    return uuid.uuid4().hex[:16].upper()

def sha512_hash(concat_str: str) -> str:
    """
        Compute SHA-512 hash(concat + hashKey)
    """
    raw = concat_str + os.getenv("PAGA_HASHKEY")
    return hashlib.sha512(raw.encode("utf-8")).hexdigest()

def paga_post(endpoint: str, payload: dict, concat_str: str):
    """Generic POST request to Paga with principal, credentials, hash."""
    # Get base url and validate
    base = (os.getenv("PAGA_BASE_URL")  or "").rstrip('/')
    if not base:
        raise RuntimeError("Missing required environment variable: PAGA_BASE_URL")
    # Safe url to be used
    url = f"{base}/{endpoint.lstrip('/')}"
    
    # validation of principal and credential variables
    principal = os.getenv("PAGA_PRINCIPAL")
    credentials = os.getenv("PAGA_CREDENTIALS")
    
    if not principal and not credentials:
        logger.warning("PAGA_PRINCIPAL or PAGA_CREDENTIALS is not in environment")
        
    headers = {
        "principal": principal,
        "credentials": credentials,
        "hash": sha512_hash(concat_str),
        "Content-Type": "application/json",
    }
    return requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)