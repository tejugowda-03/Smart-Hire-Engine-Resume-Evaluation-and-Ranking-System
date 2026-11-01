
"""
Application Factory

Creates and configures Flask application instances.
"""

from flask import Flask
from app.config.settings import get_config
from app.extensions import init_extensions
from app.controllers import register_blueprints
from app.utils.error_handlers import register_error_handlers

import logging.config
import logging
import os


def create_app(config_name='development'):
    """
    Create and configure the Flask application.
    """

    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)

    # Validate production configuration before loading it
    if config_name == 'production':
        config.validate()

    app.config.from_object(config)

    # Ensure required directories exist
    _create_required_directories(app)

    # Setup logging
    _setup_logging(app)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    app.logger.info(
        f"RSART application created with config: {config_name}"
    )

    return app


def _create_required_directories(app):
    """Create required application directories."""

    directories = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('JOB_DESCRIPTIONS_FOLDER'),
        app.config.get('LOG_FILE').parent
        if app.config.get('LOG_FILE') else None
    ]

    for directory in directories:
        if directory:
            directory.mkdir(parents=True, exist_ok=True)


def _setup_logging(app):
    """Configure application logging."""

    logging_config = app.config.get('LOGGING_CONFIG')

    if logging_config and os.path.exists(logging_config):
        logging.config.fileConfig(
            logging_config,
            disable_existing_loggers=False
        )
    else:
        logging.basicConfig(
            level=getattr(
                logging,
                app.config.get('LOG_LEVEL', 'INFO')
            ),
            format=(
                '%(asctime)s - %(name)s - '
                '%(levelname)s - %(message)s'
            )
        )
