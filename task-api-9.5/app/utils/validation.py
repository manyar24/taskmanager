from datetime import date
from app.utils.errors import ApiError

STATUSES = ("todo", "in_progress", "done")
PRIORITIES = ("low", "medium", "high")
FIELDS = ("title", "description", "status", "priority", "due_date")
SORT_FIELDS = ("id", "title", "status", "priority", "due_date", "created_at", "updated_at")


def validate_task(body: dict, partial: bool):
    errors = {}
    clean = {}
    for key in body:
        if key not in FIELDS:
            errors[key] = "Unknown field."

    if "title" in body:
        value = body["title"]
        if not isinstance(value, str) or not value.strip():
            errors["title"] = "Title must be a non-empty string."
        elif len(value.strip()) > 200:
            errors["title"] = "Title must be at most 200 characters."
        else:
            clean["title"] = value.strip()
    elif not partial:
        errors["title"] = "Title is required."

    if "description" in body:
        value = body["description"]
        if value is not None and (not isinstance(value, str) or len(value) > 2000):
            errors["description"] = "Description must be a string of at most 2000 characters, or null."
        else:
            clean["description"] = value

    if "status" in body:
        if body["status"] not in STATUSES:
            errors["status"] = f"Status must be one of: {', '.join(STATUSES)}."
        else:
            clean["status"] = body["status"]

    if "priority" in body:
        if body["priority"] not in PRIORITIES:
            errors["priority"] = f"Priority must be one of: {', '.join(PRIORITIES)}."
        else:
            clean["priority"] = body["priority"]

    if "due_date" in body:
        value = body["due_date"]
        if value is None:
            clean["due_date"] = None
        else:
            try:
                if not isinstance(value, str):
                    raise ValueError
                clean["due_date"] = date.fromisoformat(value)
            except ValueError:
                errors["due_date"] = "Due date must be YYYY-MM-DD or null."

    if errors:
        raise ApiError(422, "validation_error", "Validation failed.", errors)
    return clean


def read_json_object(request):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_json", "Request body must be a valid JSON object.")
    return body
