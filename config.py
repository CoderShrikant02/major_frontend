import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> None:
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    # Database configuration loaded from environment/.env
    DB_HOST = os.environ.get("DB_HOST", "")
    DB_USER = os.environ.get("DB_USER", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "")

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "")

    # Backward-compatible aliases for existing code paths.
    MYSQL_HOST = DB_HOST
    MYSQL_USER = DB_USER
    MYSQL_PASSWORD = DB_PASSWORD
    MYSQL_DB = DB_NAME

    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = 1800
