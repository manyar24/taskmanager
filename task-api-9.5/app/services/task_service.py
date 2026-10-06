from datetime import datetime, timezone
from datetime import timezone
from sqlalchemy import asc, desc, func, select
from app.models import Task
from app.utils.errors import ApiError
from app.utils.validation import PRIORITIES, SORT_FIELDS, STATUSES


def serialize_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "updated_at": task.updated_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def get_task_or_404(db, task_id, user_id):
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    if task is None:
        raise ApiError(404, "not_found", f"Task {task_id} not found.")
    return task


def list_tasks(db, user_id, args):
    stmt = select(Task).where(Task.user_id == user_id)
    count_stmt = select(func.count()).select_from(Task).where(Task.user_id == user_id)

    status = args.get("status")
    if status:
        if status not in STATUSES:
            raise ApiError(400, "invalid_query", f"status must be one of: {', '.join(STATUSES)}.")
        stmt = stmt.where(Task.status == status)
        count_stmt = count_stmt.where(Task.status == status)

    priority = args.get("priority")
    if priority:
        if priority not in PRIORITIES:
            raise ApiError(400, "invalid_query", f"priority must be one of: {', '.join(PRIORITIES)}.")
        stmt = stmt.where(Task.priority == priority)
        count_stmt = count_stmt.where(Task.priority == priority)

    q = args.get("q", "").strip()
    if q:
        stmt = stmt.where(Task.title.ilike(f"%{q}%"))
        count_stmt = count_stmt.where(Task.title.ilike(f"%{q}%"))

    sort = args.get("sort", "id")
    order = args.get("order", "asc").lower()
    if sort not in SORT_FIELDS:
        raise ApiError(400, "invalid_query", f"sort must be one of: {', '.join(SORT_FIELDS)}.")
    if order not in ("asc", "desc"):
        raise ApiError(400, "invalid_query", "order must be 'asc' or 'desc'.")

    try:
        limit = int(args.get("limit", 20))
        offset = int(args.get("offset", 0))
    except ValueError:
        raise ApiError(400, "invalid_query", "limit and offset must be integers.")
    if not 1 <= limit <= 100:
        raise ApiError(400, "invalid_query", "limit must be between 1 and 100.")
    if not 0 <= offset <= 10**9:
        raise ApiError(400, "invalid_query", "offset must be between 0 and 1000000000.")

    column = getattr(Task, sort)
    stmt = stmt.order_by((asc(column) if order == "asc" else desc(column)), asc(Task.id)).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    total = db.scalar(count_stmt)
    return [serialize_task(x) for x in rows], {"total": total, "limit": limit, "offset": offset}
