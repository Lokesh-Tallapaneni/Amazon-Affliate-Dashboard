"""
Setup script for the Amazon Affiliate Dashboard.

This script helps set up the application for first-time use.
"""

import os
import secrets
import sys


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return

    if not os.path.exists('.env.example'):
        print("✗ .env.example not found!")
        return

    # Read template
    with open('.env.example', 'r') as f:
        template = f.read()

    # Generate a secure secret key
    secret_key = secrets.token_hex(32)
    template = template.replace(
        'your-secret-key-here-change-in-production',
        secret_key
    )

    # Write .env file
    with open('.env', 'w') as f:
        f.write(template)

    print("✓ Created .env file with generated SECRET_KEY")
    print("  → Please edit .env and add your API credentials")


def create_directories():
    """Create required directories."""
    directories = [
        'logs',
        'uploads',
        'static/images'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        import pandas
        import sklearn
        import matplotlib
        print("✓ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e.name}")
        print("  → Run: pip install -r requirements.txt")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("Amazon Affiliate Dashboard - Setup")
    print("=" * 60)
    print()

    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9 or higher required")
        print(f"  → Current version: {sys.version}")
        return

    print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    print()

    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print()
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
        return

    print()

    # Create directories
    print("Creating directories...")
    create_directories()
    print()

    # Create .env file
    print("Setting up environment...")
    create_env_file()
    print()

    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Edit .env file and add your API credentials:")
    print("   - AMAZON_API_KEY")
    print("   - AMAZON_SECRET_KEY")
    print("   - AMAZON_ASSOCIATE_TAG")
    print("   - OPENAI_API_KEY (for chat feature)")
    print()
    print("2. Run the application:")
    print("   python run.py")
    print()
    print("3. Open your browser to:")
    print("   http://localhost:5000")
    print()


if __name__ == '__main__':
    main()
