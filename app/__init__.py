"""
Flask application factory.

This module creates and configures the Flask application using the
application factory pattern for better modularity and testability.
"""

import os
import random
from flask import Flask

from config import get_config
from app.logger import setup_logging


def create_app(config_name=None):
    """
    Application factory function.

    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')

    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__,
                static_folder='../static',
                template_folder='../templates')

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Setup logging
    setup_logging(
        log_level=app.config.get('LOG_LEVEL', 'INFO'),
        log_file=app.config.get('LOG_FILE'),
        log_dir='logs'
    )

    # Ensure required directories exist
    _ensure_directories(app)

    # Register Jinja2 filters
    _register_filters(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _ensure_directories(app):
    """
    Ensure required directories exist.

    Args:
        app (Flask): Flask application instance
    """
    directories = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('IMAGES_FOLDER'),
        'logs'
    ]

    for directory in directories:
        if directory:
            os.makedirs(directory, exist_ok=True)


def _register_filters(app):
    """
    Register custom Jinja2 filters.

    Args:
        app (Flask): Flask application instance
    """
    @app.template_filter('shuffle')
    def shuffle_filter(lst):
        """Shuffle a list (for randomizing product display)."""
        if not lst:
            return lst
        shuffled = lst[:]
        random.shuffle(shuffled)
        return shuffled


def _register_blueprints(app):
    """
    Register application blueprints.

    Args:
        app (Flask): Flask application instance
    """
    from app.blueprints import (
        auth_bp,
        dashboard_bp,
        data_bp,
        recommendations_bp,
        chat_bp,
        analytics_bp
    )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(analytics_bp)


def _register_error_handlers(app):
    """
    Register error handlers.

    Args:
        app (Flask): Flask application instance
    """
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return "Page not found", 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal server error: {str(error)}")
        return "Internal server error", 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """Handle unhandled exceptions."""
        app.logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return "An unexpected error occurred", 500
