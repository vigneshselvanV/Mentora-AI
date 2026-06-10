import os
import uuid
import hashlib
import hmac
import base64
import json
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'mentora-secret-change-in-production')

TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    """Hash password using SHA-256 + salt"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return base64.b64encode(
        salt + key).decode('utf-8')

def verify_password(password: str,
                    stored: str) -> bool:
    """Verify password against stored hash"""
    try:
        decoded = base64.b64decode(
            stored.encode('utf-8'))
        salt = decoded[:32]
        stored_key = decoded[32:]
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return hmac.compare_digest(
            stored_key, key)
    except Exception:
        return False

def create_token(user_id: str,
                 email: str) -> str:
    """Create a simple signed token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': (datetime.utcnow() +
                timedelta(days=TOKEN_EXPIRE_DAYS))
               .isoformat(),
        'iat': datetime.utcnow().isoformat(),
        'jti': str(uuid.uuid4())
    }
    
    payload_b64 = base64.b64encode(
        json.dumps(payload).encode()
    ).decode()
    
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{payload_b64}.{signature}"

def verify_token(token: str) -> dict | None:
    """Verify token and return payload or None"""
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        
        payload_b64, signature = parts
        
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(
                signature, expected_sig):
            return None
        
        payload = json.loads(
            base64.b64decode(
                payload_b64).decode())
        
        exp = datetime.fromisoformat(
            payload['exp'])
        if datetime.utcnow() > exp:
            return None
        
        return payload
    except Exception:
        return None

def generate_user_id() -> str:
    return str(uuid.uuid4())

def validate_email(email: str) -> bool:
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> dict:
    errors = []
    if len(password) < 8:
        errors.append(
            "At least 8 characters required")
    if not any(c.isupper() for c in password):
        errors.append(
            "At least one uppercase letter")
    if not any(c.isdigit() for c in password):
        errors.append(
            "At least one number")
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
