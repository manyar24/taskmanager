import re
from flask import Blueprint, current_app, request
from sqlalchemy import select
from app.db import get_db
from app.models import User
from app.utils.errors import ApiError
from app.utils.security import create_access_token, hash_password, verify_password

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

@bp.post("/register")
def register():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_json", "Request body must be a valid JSON object.")
    name = body.get("name")
    email = body.get("email")
    password = body.get("password")
    errors = {}
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        errors["name"] = "Name is required and must be at most 100 characters."
    if not isinstance(email, str) or not EMAIL_RE.match(email.strip().lower()):
        errors["email"] = "A valid email address is required."
    if not isinstance(password, str) or len(password) < 8 or len(password) > 128:
        errors["password"] = "Password must be 8-128 characters."
    if errors:
        raise ApiError(422, "validation_error", "Validation failed.", errors)

    db = get_db()
    email = email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise ApiError(409, "email_exists", "An account with this email already exists.")
    user = User(name=name.strip(), email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    token = create_access_token(user.id, current_app.config["JWT_SECRET_KEY"], current_app.config["JWT_EXP_MINUTES"])
    return {"data": {"user": {"id": user.id, "name": user.name, "email": user.email}, "access_token": token, "token_type": "Bearer"}}, 201

@bp.post("/login")
def login():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_json", "Request body must be a valid JSON object.")
    email = body.get("email")
    password = body.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        raise ApiError(422, "validation_error", "Email and password are required.")
    db = get_db()
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise ApiError(401, "invalid_credentials", "Invalid email or password.")
    token = create_access_token(user.id, current_app.config["JWT_SECRET_KEY"], current_app.config["JWT_EXP_MINUTES"])
    return {"data": {"user": {"id": user.id, "name": user.name, "email": user.email}, "access_token": token, "token_type": "Bearer"}}
