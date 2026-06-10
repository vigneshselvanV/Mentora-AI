# ═══════════════════════════════════════
# PRODUCTION DEPLOYMENT CHECKLIST
# ═══════════════════════════════════════
# ✅ 1. Set SECRET_KEY env variable
#       Use: python -c "import secrets;
#            print(secrets.token_hex(32))"
#
# ✅ 2. Set OPENROUTER_API_KEY
#
# ✅ 3. mentora_users.db NOT in .gitignore
#       Wait — it IS in .gitignore (correct)
#       Render disk will store it persistently
#
# ✅ 4. chroma_db/ IS committed to GitHub
#       (pre-built vectors)
#
# ✅ 5. DEMO_EMAIL and DEMO_PASSWORD set
#
# ✅ 6. Render disk configured (render.yaml)
#       Both chroma_db and mentora_users.db
#       stored on persistent disk
#
# ✅ 7. CORS in production:
#       Change allow_origins=["*"]
#       to your actual domain:
#       allow_origins=["https://mentora-ai.onrender.com"]
#
# ✅ 8. Test these flows before publishing:
#       → Signup new account
#       → Login existing account
#       → Demo account login
#       → Chat works with token
#       → Data saves and loads
#       → Logout clears session
#       → Invalid token returns 401
# ═══════════════════════════════════════

import logging
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import Optional
from datetime import datetime

from backend.rag import ask_ai_pipeline
from backend.vectorstore import VectorStore
from backend.embeddings import EmbeddingService

from auth import (verify_token, hash_password,
    verify_password, create_token,
    generate_user_id, validate_email,
    validate_password)
from database import (init_db, create_user,
    get_user_by_email, get_user_by_id,
    update_last_login, get_user_data,
    save_user_data)
from models import (SignupRequest, LoginRequest,
    ChatRequest, SaveDataRequest,
    AuthResponse, UserResponse)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def create_demo_account():
    demo_email = os.environ.get(
        'DEMO_EMAIL', 'demo@mentora.ai')
    demo_pass = os.environ.get(
        'DEMO_PASSWORD', 'Demo1234')
    existing = get_user_by_email(demo_email)
    if not existing:
        hashed = hash_password(demo_pass)
        create_user(
            generate_user_id(),
            demo_email,
            'Demo User',
            hashed
        )
        print("Demo account ready!")
    else:
        print("Demo account exists!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await create_demo_account()
    logger.info("Initializing vector DB and Embedding model...")
    EmbeddingService.get_instance()
    VectorStore.get_collection()
    yield
    logger.info("Shutting down...")

app = FastAPI(title="AI Teacher API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(
    authorization: Optional[str] =
        Header(None)):
    """Extract and verify user from token"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated")
    
    token = authorization.replace(
        'Bearer ', '').strip()
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token")
    
    user = get_user_by_id(payload['user_id'])
    if not user or not user['is_active']:
        raise HTTPException(
            status_code=401,
            detail="User not found")
    
    return user

@app.get("/health")
async def health_check():
    col = VectorStore.get_collection()
    chunks = col.count() if col else 0
    return {
        "status": "online",
        "chunks": chunks
    }

@app.post("/auth/signup",
          response_model=AuthResponse)
async def signup(request: SignupRequest):
    # Validate email
    if not validate_email(request.email):
        return AuthResponse(
            success=False,
            message="Invalid email format")
    
    # Validate password
    pwd_check = validate_password(
        request.password)
    if not pwd_check['valid']:
        return AuthResponse(
            success=False,
            message=". ".join(
                pwd_check['errors']))
    
    # Validate username
    if len(request.username.strip()) < 2:
        return AuthResponse(
            success=False,
            message="Username too short")
    
    # Hash password
    hashed = hash_password(request.password)
    user_id = generate_user_id()
    
    # Create user
    created = create_user(
        user_id,
        request.email,
        request.username.strip(),
        hashed
    )
    
    if not created:
        return AuthResponse(
            success=False,
            message="Email already registered")
    
    # Create token
    token = create_token(user_id,
                         request.email)
    
    user = get_user_by_id(user_id)
    
    return AuthResponse(
        success=True,
        token=token,
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "plan": user.get("plan", "free")
        },
        message="Account created successfully!"
    )

@app.post("/auth/login",
          response_model=AuthResponse)
async def login(request: LoginRequest):
    user = get_user_by_email(request.email)
    
    if not user:
        return AuthResponse(
            success=False,
            message="Invalid email or password")
    
    if not verify_password(
            request.password, user['password']):
        return AuthResponse(
            success=False,
            message="Invalid email or password")
    
    if not user['is_active']:
        return AuthResponse(
            success=False,
            message="Account is deactivated")
    
    update_last_login(user['id'])
    token = create_token(
        user['id'], user['email'])
    
    # CRITICAL: Return ACTUAL username from DB
    # NOT a default value
    return AuthResponse(
        success=True,
        token=token,
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "plan": user.get("plan", "free")
        },
        message=f"Welcome back, {user['username']}!"
    )

@app.get("/auth/me")
async def get_me(
    current_user: dict =
        Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "plan": current_user.get("plan", "free"),
        "created_at": current_user["created_at"],
        "last_login": current_user["last_login"]
    }

@app.post("/auth/logout")
async def logout_endpoint():
    """
    Logout endpoint.
    Always returns success. Token
    invalidation handled client-side.
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@app.get("/auth/test")
async def test_auth():
    return {
        "status": "auth working",
        "timestamp": datetime.utcnow()
                     .isoformat()
    }

@app.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict =
        Depends(get_current_user)):
    try:
        result = await asyncio.wait_for(ask_ai_pipeline(request.question), timeout=180.0)
        return result
    except asyncio.TimeoutError:
        logger.error("Request timed out")
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/data")
async def get_data(
    current_user: dict =
        Depends(get_current_user)):
    """Get user's saved progress from DB"""
    data = get_user_data(current_user['id'])
    if not data:
        return {"data": None}
    
    return {"data": {
        "totalQuestions":
            data.get('total_questions', 0),
        "topicsExplored": json.loads(
            data.get('topics_explored','{}')),
        "recentActivity": json.loads(
            data.get('recent_activity','[]')),
        "streak":
            data.get('streak', 0),
        "lastActiveDate":
            data.get('last_active_date'),
        "quizResults": json.loads(
            data.get('quiz_results','[]')),
        "bookmarks": json.loads(
            data.get('bookmarks','[]')),
        "sessions": json.loads(
            data.get('chat_sessions','[]')),
        "savedPaths": json.loads(
            data.get('saved_paths','[]')),
        "difficulty":
            data.get('difficulty','beginner')
    }}

@app.post("/user/data")
async def save_data(
    request: SaveDataRequest,
    current_user: dict =
        Depends(get_current_user)):
    """Save user progress to DB"""
    save_user_data(
        current_user['id'], request.data)
    return {"success": True}

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/")
async def serve_login():
    return FileResponse(
        "frontend/login.html")

@app.get("/login.html")
async def login_fallback():
    return FileResponse("frontend/login.html")

@app.get("/app")
async def serve_app():
    return FileResponse(
        "frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
