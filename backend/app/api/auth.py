from fastapi import APIRouter, HTTPException, Depends, Header
from jose import jwt, JWTError
from app.models.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.database.mongodb import db
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

async def current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    try:
        payload = jwt.decode(authorization.split(" ", 1)[1], settings.secret_key, algorithms=["HS256"])
        user_id = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(401, "Invalid or expired token")
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(401, "User not found")
    return {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}

@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest):
    existing = await db.users.find_one({"email": str(body.email).lower()})
    if existing:
        raise HTTPException(409, "Email already registered")
    import uuid
    user_id = str(uuid.uuid4())
    user = {"_id": user_id, "name": body.name.strip(), "email": str(body.email).lower(), "password_hash": hash_password(body.password)}
    await db.users.insert_one(user)
    public = {"id": user_id, "name": user["name"], "email": user["email"]}
    return TokenResponse(access_token=create_access_token(user_id), user=public)

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = await db.users.find_one({"email": str(body.email).lower()})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    public = {"id": user["_id"], "name": user["name"], "email": user["email"]}
    return TokenResponse(access_token=create_access_token(user["_id"]), user=public)

@router.get("/me")
async def me(user: dict = Depends(current_user)):
    return user
