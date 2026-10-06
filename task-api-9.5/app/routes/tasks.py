from functools import wraps
from flask import Blueprint, current_app, request
from sqlalchemy import select
import jwt
from app.db import get_db
from app.models import Task
from app.services.task_service import get_task_or_404, list_tasks, serialize_task
from app.utils.errors import ApiError
from app.utils.security import decode_access_token
from app.utils.validation import read_json_object, validate_task

bp = Blueprint("tasks", __name__, url_prefix="/api/v1/tasks")

def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise ApiError(401, "missing_token", "Authorization Bearer token is required.")
        token = header[7:].strip()
        if not token:
            raise ApiError(401, "missing_token", "Authorization Bearer token is required.")
        try:
            payload = decode_access_token(token, current_app.config["JWT_SECRET_KEY"])
            user_id = int(payload["sub"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError, TypeError):
            raise ApiError(401, "invalid_token", "Token is invalid or expired.")
        return fn(user_id, *args, **kwargs)
    return wrapper

@bp.get("")
@auth_required
def list_route(user_id):
    rows, meta = list_tasks(get_db(), user_id, request.args)
    return {"data": rows, "meta": meta}

@bp.post("")
@auth_required
def create_route(user_id):
    clean = validate_task(read_json_object(request), partial=False)
    db = get_db()
    task = Task(user_id=user_id, title=clean["title"], description=clean.get("description"), status=clean.get("status", "todo"), priority=clean.get("priority", "medium"), due_date=clean.get("due_date"))
    db.add(task)
    db.commit()
    response = {"data": serialize_task(task)}
    from flask import jsonify
    resp = jsonify(response)
    resp.status_code = 201
    resp.headers["Location"] = f"/api/v1/tasks/{task.id}"
    return resp

@bp.get("/<int:task_id>")
@auth_required
def get_route(user_id, task_id):
    return {"data": serialize_task(get_task_or_404(get_db(), task_id, user_id))}

def update_task(user_id, task_id, partial):
    db = get_db()
    task = get_task_or_404(db, task_id, user_id)
    clean = validate_task(read_json_object(request), partial=partial)
    if not partial:
        merged = {"title": None, "description": None, "status": "todo", "priority": "medium", "due_date": None}
    else:
        merged = {"title": task.title, "description": task.description, "status": task.status, "priority": task.priority, "due_date": task.due_date}
    merged.update(clean)
    for key, value in merged.items():
        setattr(task, key, value)
    db.commit()
    return {"data": serialize_task(task)}

@bp.put("/<int:task_id>")
@auth_required
def put_route(user_id, task_id):
    return update_task(user_id, task_id, False)

@bp.patch("/<int:task_id>")
@auth_required
def patch_route(user_id, task_id):
    return update_task(user_id, task_id, True)

@bp.delete("/<int:task_id>")
@auth_required
def delete_route(user_id, task_id):
    db = get_db()
    task = get_task_or_404(db, task_id, user_id)
    db.delete(task)
    db.commit()
    return "", 204
