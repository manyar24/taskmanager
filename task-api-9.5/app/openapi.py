OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "Task Management REST API", "version": "1.0.0", "description": "Production-style task API with JWT authentication."},
    "servers": [{"url": "http://localhost:5000"}],
    "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}},
    "paths": {
        "/health": {"get": {"summary": "Health check", "responses": {"200": {"description": "Healthy"}}}},
        "/api/v1/auth/register": {"post": {"summary": "Register", "responses": {"201": {"description": "Created"}, "409": {"description": "Email exists"}}}},
        "/api/v1/auth/login": {"post": {"summary": "Login", "responses": {"200": {"description": "JWT issued"}}}},
        "/api/v1/tasks": {
            "get": {"summary": "List tasks", "security": [{"bearerAuth": []}], "parameters": [{"name": "q", "in": "query", "schema": {"type": "string"}}, {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["todo", "in_progress", "done"]}}, {"name": "priority", "in": "query", "schema": {"type": "string", "enum": ["low", "medium", "high"]}}, {"name": "sort", "in": "query", "schema": {"type": "string"}}, {"name": "order", "in": "query", "schema": {"type": "string", "enum": ["asc", "desc"]}}, {"name": "limit", "in": "query", "schema": {"type": "integer"}}, {"name": "offset", "in": "query", "schema": {"type": "integer"}}], "responses": {"200": {"description": "Task list"}}},
            "post": {"summary": "Create task", "security": [{"bearerAuth": []}], "responses": {"201": {"description": "Created"}}}
        },
        "/api/v1/tasks/{id}": {
            "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "get": {"summary": "Get task", "security": [{"bearerAuth": []}], "responses": {"200": {"description": "Task"}, "404": {"description": "Not found"}}},
            "put": {"summary": "Replace task", "security": [{"bearerAuth": []}], "responses": {"200": {"description": "Updated"}}},
            "patch": {"summary": "Update task", "security": [{"bearerAuth": []}], "responses": {"200": {"description": "Updated"}}},
            "delete": {"summary": "Delete task", "security": [{"bearerAuth": []}], "responses": {"204": {"description": "Deleted"}}}
        }
    }
}
