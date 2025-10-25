"""
Authentication blueprint.

This module handles user login and logout routes with JWT authentication.
"""

import logging
import os
import multiprocessing
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, make_response, jsonify

from amazon_paapi.errors.exceptions import RequestError

from app.services import AmazonAPIService, MLService, JWTService
from app.services.product_service import run_product_fetch
from app.utils import validate_api_credentials, safe_file_save, cleanup_files

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirect to login page."""
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display login page."""
    return render_template('index.html')


@auth_bp.route('/submit', methods=['POST'])
def submit():
    """
    Handle login form submission.

    Validates Amazon API credentials and uploads user data file.
    """
    try:
        # Get form data
        api_key = request.form.get('api_key', '').strip()
        secret_key = request.form.get('secret_key', '').strip()
        associate_tag = request.form.get('associate_tag', '').strip()
        uploaded_file = request.files.get('api_file')

        # Validate inputs
        if not validate_api_credentials(api_key, secret_key, associate_tag):
            flash('All API credentials are required.', 'error')
            return render_template('index.html')

        if not uploaded_file or uploaded_file.filename == '':
            flash('Please upload a data file.', 'error')
            return render_template('index.html')

        # Verify API credentials
        amazon_service = AmazonAPIService(api_key, secret_key, associate_tag)

        if not amazon_service.verify_credentials():
            flash('Invalid API credentials. Please check and try again.', 'error')
            return render_template('index.html')

        # Save uploaded file to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = safe_file_save(
            uploaded_file,
            project_root,
            current_app.config['DATA_FILE']
        )

        if not file_path:
            flash('Error saving uploaded file.', 'error')
            return render_template('index.html')

        # Train ML model
        ml_service = MLService(current_app.config)
        ml_service.train_model(current_app.config['DATA_FILE'])

        # Start background product fetch process
        product_fetch_process = multiprocessing.Process(
            target=run_product_fetch,
            args=(api_key, secret_key, associate_tag, current_app.config)
        )
        product_fetch_process.start()

        # Prepare user data for JWT
        user_data = {
            'api_key': api_key,
            'secret_key': secret_key,
            'associate_tag': associate_tag,
            'product_fetch_pid': product_fetch_process.pid
        }

        # Generate JWT tokens
        jwt_service = JWTService(current_app.config)
        tokens = jwt_service.generate_tokens(user_data)

        # Store credentials in session (for backward compatibility)
        session['logged_in'] = True
        session['api_key'] = api_key
        session['secret_key'] = secret_key
        session['associate_tag'] = associate_tag
        session['product_fetch_pid'] = product_fetch_process.pid

        logger.info("User logged in successfully with JWT tokens")
        flash('Login successful!', 'success')

        # Create response and set JWT cookie
        response = make_response(redirect(url_for('dashboard.dashboard')))

        # Set access token cookie (HttpOnly for security)
        response.set_cookie(
            'access_token',
            tokens['access_token'],
            max_age=int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()),
            httponly=True,
            secure=current_app.config['SESSION_COOKIE_SECURE'],
            samesite=current_app.config['SESSION_COOKIE_SAMESITE']
        )

        # Set refresh token cookie (HttpOnly for security)
        response.set_cookie(
            'refresh_token',
            tokens['refresh_token'],
            max_age=int(current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds()),
            httponly=True,
            secure=current_app.config['SESSION_COOKIE_SECURE'],
            samesite=current_app.config['SESSION_COOKIE_SAMESITE']
        )

        return response

    except RequestError as e:
        logger.error(f"Amazon API error: {str(e)}")
        flash('Invalid API credentials. Please check and try again.', 'error')
        return render_template('index.html')

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('index.html')


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """
    Handle user logout with JWT token blacklisting.

    Terminates background processes, cleans up files, and blacklists JWT tokens.
    """
    try:
        # Get JWT token from cookie or header
        access_token = request.cookies.get('access_token')
        if not access_token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]

        # Blacklist the JWT token
        if access_token:
            jwt_service = JWTService(current_app.config)
            jwt_service.blacklist_token(access_token)
            logger.info("JWT token blacklisted")

        # Terminate product fetch process if running
        pid = session.get('product_fetch_pid')
        if pid:
            try:
                process = multiprocessing.Process()
                process._popen = type('obj', (object,), {'pid': pid})
                if process.is_alive():
                    process.terminate()
                    logger.info(f"Terminated product fetch process (PID: {pid})")
            except Exception as e:
                logger.warning(f"Could not terminate process: {str(e)}")

        # Clear session
        session.clear()

        # Cleanup files
        files_to_remove = [
            current_app.config['DATA_FILE'],
            current_app.config['DATA_CSV'],
            current_app.config['MODEL_PICKLE_PATH'],
            current_app.config['FEATURE_EXTRACTION_PATH'],
            current_app.config['PRODUCT_DETAILS_FILE'],
            'api_credintials.txt'  # Legacy file
        ]

        cleanup_files(files_to_remove)

        logger.info("User logged out successfully")
        flash('You have been logged out.', 'info')

        # Create response and clear JWT cookies
        response = make_response(redirect(url_for('auth.login')))
        response.set_cookie('access_token', '', max_age=0)
        response.set_cookie('refresh_token', '', max_age=0)

        return response

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        response = make_response(redirect(url_for('auth.login')))
        response.set_cookie('access_token', '', max_age=0)
        response.set_cookie('refresh_token', '', max_age=0)
        return response
