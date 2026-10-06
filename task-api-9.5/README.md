# Task Management REST API

A Flask-based REST API for managing tasks. The application supports user authentication, task CRUD operations, search, filtering, pagination, sorting, validation, database persistence, API documentation, automated tests, and Docker-based PostgreSQL development.

## Tech stack

- Python 3.12+
- Flask 3
- SQLAlchemy 2
- SQLite for local development
- PostgreSQL for Docker/production use
- PyJWT for authentication
- Alembic for database migrations
- pytest and pytest-cov for testing
- Docker Compose
- GitHub Actions

## Project structure

```text
task-api/
├── app/
│   ├── models/       # Database models
│   ├── routes/       # API routes
│   ├── services/     # Task business logic
│   ├── utils/        # Validation, security and errors
│   ├── config.py
│   ├── db.py
│   ├── openapi.py
│   └── __init__.py
├── tests/
├── migrations/
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── .env.example
├── requirements.txt
└── run.py
```

## Run locally on Windows

Open Command Prompt in the project directory:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

The API runs at `http://localhost:5000`.

A simple web frontend is available at `http://localhost:5000/`. It handles login/register, stores the session token for the current browser tab, and provides task creation, editing, deletion, search, filtering, and status/priority views without requiring Swagger authorization.

Useful endpoints:

- Health check: `http://localhost:5000/health`
- OpenAPI JSON: `http://localhost:5000/openapi.json`
- API documentation: `http://localhost:5000/api/docs`

## Run the tests

```cmd
pytest -q --cov=app --cov-report=term-missing
```

You can also use the standard library test runner:

```cmd
python -m unittest discover -s tests -v
```

## Run with Docker and PostgreSQL

```cmd
docker compose up --build
```

The API is available at `http://localhost:5000` and connects to the PostgreSQL service defined in `docker-compose.yml`.

For a real deployment, set a strong `JWT_SECRET_KEY` and keep the `.env` file out of source control.

## Authentication

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "Manya",
  "email": "manya@example.com",
  "password": "StrongPass123"
}
```

The response includes an access token.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "manya@example.com",
  "password": "StrongPass123"
}
```

Send the returned token with protected task requests:

```http
Authorization: Bearer <access_token>
```

Tasks are scoped to the authenticated user, so users cannot access another user's tasks.

## Task fields

| Field | Type | Rules |
|---|---|---|
| id | integer | read-only |
| title | string | required, 1–200 characters |
| description | string/null | maximum 2000 characters |
| status | string | `todo`, `in_progress`, `done` |
| priority | string | `low`, `medium`, `high` |
| due_date | date/null | `YYYY-MM-DD` |
| created_at | datetime | UTC |
| updated_at | datetime | UTC |

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a user |
| POST | `/api/v1/auth/login` | Login and receive a JWT |
| GET | `/api/v1/tasks` | List, search, filter, sort and paginate tasks |
| POST | `/api/v1/tasks` | Create a task |
| GET | `/api/v1/tasks/{id}` | Get a task |
| PUT | `/api/v1/tasks/{id}` | Replace a task |
| PATCH | `/api/v1/tasks/{id}` | Partially update a task |
| DELETE | `/api/v1/tasks/{id}` | Delete a task |
| GET | `/health` | Check API and database status |
| GET | `/openapi.json` | Get the OpenAPI specification |

## Search, filtering, pagination and sorting

Example:

```text
GET /api/v1/tasks?q=report&status=todo&priority=high&sort=due_date&order=asc&limit=20&offset=0
```

Supported sort fields are `id`, `title`, `status`, `priority`, `due_date`, `created_at`, and `updated_at`.

## Error responses

Errors use a consistent JSON structure:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation failed.",
    "details": {
      "title": "Title is required."
    }
  }
}
```

## Database migrations

The application creates missing tables on startup so it can be run easily for local evaluation. Alembic is included for controlled schema changes in longer-lived environments.

Example:

```cmd
alembic revision --autogenerate -m "create users and tasks"
alembic upgrade head
```

Before running migrations against PostgreSQL, make sure the Alembic database URL is configured for that database.

## Security

- Passwords are stored using salted `scrypt` hashes.
- JWT access tokens expire after the configured number of minutes.
- Task routes require a Bearer token.
- Database queries are scoped to the authenticated user's ID.
- SQLAlchemy handles parameterized database queries.
- Secrets are read from environment variables.
- Replace the development JWT secret before deployment.

## CI

The GitHub Actions workflow installs the dependencies and runs the test suite with coverage on pushes and pull requests.

## Manual verification checklist

1. Start the API.
2. Register a user.
3. Log in and copy the access token.
4. Create several tasks.
5. Test search, filtering, sorting, and pagination.
6. Update a task with `PATCH` and replace one with `PUT`.
7. Delete a task.
8. Register a second user and confirm that the first user's tasks are not visible.
9. Open the API documentation and run a few requests.
10. Run the test suite and check the coverage report.
