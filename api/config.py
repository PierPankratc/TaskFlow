import os

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dev-only-change-in-production-32chars!",
)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todo.db")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in ("1", "true", "yes")
