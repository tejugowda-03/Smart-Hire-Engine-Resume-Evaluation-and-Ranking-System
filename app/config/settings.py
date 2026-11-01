
import os
from pathlib import Path


# ==========================================
# PROJECT ROOT DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_path(env_name, default_path):
    """Return an absolute path for a configured directory."""
    value = os.environ.get(env_name)

    path = Path(value) if value else Path(default_path)

    if not path.is_absolute():
        path = BASE_DIR / path

    return path.resolve()


def get_database_url():
    """Get and normalize the database connection URL."""
    url = os.environ.get("DATABASE_URL")

    if url:
        # Normalize older PostgreSQL URL formats.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        return url

    return "sqlite:///" + str(BASE_DIR / "rsart.db")


def get_cache_type():
    """Return the correct Flask-Caching backend name."""
    if os.environ.get("REDIS_URL"):
        return "RedisCache"

    return "SimpleCache"


# ==========================================
# BASE CONFIGURATION
# ==========================================

class BaseConfig:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    # File handling
    UPLOAD_FOLDER = get_path(
        "UPLOAD_FOLDER",
        "data/uploaded_resumes"
    )

    JOB_DESCRIPTIONS_FOLDER = get_path(
        "JOB_DESCRIPTIONS_FOLDER",
        "data/job_descriptions"
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "txt"
    }

    # Database
    SQLALCHEMY_DATABASE_URI = get_database_url()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # Cache
    CACHE_TYPE = get_cache_type()

    CACHE_REDIS_URL = os.environ.get(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    CACHE_DEFAULT_TIMEOUT = 3600

    # Logging
    LOGGING_CONFIG = (
        BASE_DIR / "app" / "config" / "logging.conf"
    )

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    LOG_FILE = BASE_DIR / "logs" / "rsart.log"

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Resume processing
    TOP_CANDIDATES_COUNT = int(
        os.environ.get("TOP_CANDIDATES_COUNT", 10)
    )

    SIMILARITY_THRESHOLD = float(
        os.environ.get("SIMILARITY_THRESHOLD", 0.1)
    )


# ==========================================
# DEVELOPMENT CONFIGURATION
# ==========================================

class DevelopmentConfig(BaseConfig):

    DEBUG = True
    TESTING = False

    CACHE_TYPE = "SimpleCache"


# ==========================================
# PRODUCTION CONFIGURATION
# ==========================================

class ProductionConfig(BaseConfig):

    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = get_database_url()

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 5
    }

    @classmethod
    def validate(cls):
        """Validate required production environment variables."""

        if not cls.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be configured in production"
            )

        if not os.environ.get("DATABASE_URL"):
            raise ValueError(
                "DATABASE_URL must be configured in production"
            )


# ==========================================
# TESTING CONFIGURATION
# ==========================================

class TestingConfig(BaseConfig):

    TESTING = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    WTF_CSRF_ENABLED = False

    CACHE_TYPE = "SimpleCache"


# ==========================================
# CONFIGURATION SELECTOR
# ==========================================

def get_config(config_name):

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    return config_map.get(
        config_name,
        DevelopmentConfig
    )
