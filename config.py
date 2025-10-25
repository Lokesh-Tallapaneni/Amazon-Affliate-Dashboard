"""
Configuration management for the Flask application.

This module provides configuration classes for different environments
(development, testing, production) and manages sensitive data through
environment variables.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False

    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Access token expires in 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh token expires in 30 days

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

    # Amazon API settings
    AMAZON_API_KEY = os.environ.get('AMAZON_API_KEY')
    AMAZON_SECRET_KEY = os.environ.get('AMAZON_SECRET_KEY')
    AMAZON_ASSOCIATE_TAG = os.environ.get('AMAZON_ASSOCIATE_TAG')
    AMAZON_COUNTRY = os.environ.get('AMAZON_COUNTRY', 'IN')
    AMAZON_THROTTLING = int(os.environ.get('AMAZON_THROTTLING', 1))

    # AI Chat Provider Settings (supports multiple providers)
    # OpenAI (GPT-3.5, GPT-4)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # Google Gemini
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

    # Anthropic Claude
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

    # ML model settings
    MODEL_PICKLE_PATH = 'cmodel_pkl'
    FEATURE_EXTRACTION_PATH = 'feature_extraction'

    # Data file paths
    DATA_FILE = 'data.xlsx'
    DATA_CSV = 'data.csv'
    PRODUCT_DETAILS_FILE = 'product_details.xlsx'

    # Static files
    STATIC_FOLDER = 'static'
    IMAGES_FOLDER = os.path.join(STATIC_FOLDER, 'images')

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'app.log'


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False

    @property
    def SECRET_KEY(self):
        """Ensure secret key is set in production."""
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError('SECRET_KEY must be set in production environment')
        return secret_key


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration object based on environment.

    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')

    Returns:
        Config: Configuration object
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(config_name, config['default'])
