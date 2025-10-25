"""
Application entry point.

This script creates and runs the Flask application.
"""

import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # Run application
    app.run(host=host, port=port, debug=debug)
