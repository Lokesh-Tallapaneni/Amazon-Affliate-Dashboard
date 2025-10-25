"""Blueprints package for route organization."""

from .auth import auth_bp
from .dashboard import dashboard_bp
from .data import data_bp
from .recommendations import recommendations_bp
from .chat import chat_bp
from .analytics import analytics_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'data_bp',
    'recommendations_bp',
    'chat_bp',
    'analytics_bp'
]
