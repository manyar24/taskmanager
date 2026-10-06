import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'tasks.db')}")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-this-secret")
    JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))
    PORT = int(os.getenv("PORT", "5000"))
    TESTING = False
