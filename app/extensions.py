
"""
Flask Extensions

Initializes and configures all Flask extensions used by the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()


def init_extensions(app):
    """Initialize all Flask extensions."""

    # Initialize SQLAlchemy
    db.init_app(app)
    app.logger.info("Database initialized successfully")

    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    # Initialize Flask-Caching
    cache.init_app(app)
    app.logger.info("Cache initialized successfully")

    # Clear cache on startup
    with app.app_context():
        try:
            cache.clear()
        except Exception as e:
            app.logger.warning(
                f"Could not clear cache on startup: {e}"
            )
