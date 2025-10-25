"""
Custom decorators for the application.

This module provides decorators for authentication, authorization,
and other cross-cutting concerns.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify, current_app, g
from app.services import JWTService


def login_required(f):
    """
    Decorator to require login for a route (legacy session-based).

    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "This requires login"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def jwt_required(f):
    """
    Decorator to require JWT authentication for a route.

    This decorator checks for a valid JWT token in:
    1. Authorization header (Bearer token)
    2. Cookie (access_token)
    3. Query parameter (?token=xxx)

    The decoded token payload is stored in g.current_user

    Usage:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            user_data = g.current_user
            return f"Hello {user_data['user_id']}"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check Authorization header first (Bearer token)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        # Fallback to cookie
        if not token:
            token = request.cookies.get('access_token')

        # Fallback to query parameter
        if not token:
            token = request.args.get('token')

        if not token:
            # For HTML pages, redirect to login
            if request.accept_mimetypes.accept_html:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            # For API requests, return JSON error
            return jsonify({'error': 'Missing authentication token'}), 401

        # Verify token
        jwt_service = JWTService(current_app.config)
        payload = jwt_service.verify_token(token)

        if not payload:
            # For HTML pages, redirect to login
            if request.accept_mimetypes.accept_html:
                flash('Your session has expired. Please log in again.', 'warning')
                return redirect(url_for('auth.login'))
            # For API requests, return JSON error
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Store user data in g object for use in the route
        g.current_user = jwt_service.extract_user_data(payload)
        g.token_payload = payload

        return f(*args, **kwargs)
    return decorated_function


def jwt_optional(f):
    """
    Decorator that allows but does not require JWT authentication.

    If a valid token is present, user data is stored in g.current_user.
    If no token or invalid token, g.current_user is None and request proceeds.

    Usage:
        @app.route('/optional-auth')
        @jwt_optional
        def optional_route():
            if g.current_user:
                return f"Hello {g.current_user['user_id']}"
            return "Hello guest"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check Authorization header first
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        # Fallback to cookie
        if not token:
            token = request.cookies.get('access_token')

        # Fallback to query parameter
        if not token:
            token = request.args.get('token')

        # If token exists, try to verify it
        if token:
            jwt_service = JWTService(current_app.config)
            payload = jwt_service.verify_token(token)

            if payload:
                g.current_user = jwt_service.extract_user_data(payload)
                g.token_payload = payload
            else:
                g.current_user = None
        else:
            g.current_user = None

        return f(*args, **kwargs)
    return decorated_function
