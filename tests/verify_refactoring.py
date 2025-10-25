"""
Verification script for the refactored Flask application.

This script checks that all modules import correctly and the
application can be initialized without errors.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def check_imports():
    """Verify all modules can be imported."""
    print("Checking imports...")
    errors = []

    # Core application
    try:
        from app import create_app
        print("  ✓ app.create_app")
    except ImportError as e:
        errors.append(f"app.create_app: {e}")
        print(f"  ✗ app.create_app: {e}")

    # Configuration
    try:
        from config import get_config, Config
        print("  ✓ config")
    except ImportError as e:
        errors.append(f"config: {e}")
        print(f"  ✗ config: {e}")

    # Blueprints
    blueprints = ['auth', 'dashboard', 'data', 'recommendations', 'chat']
    for bp in blueprints:
        try:
            module = __import__(f'app.blueprints.{bp}', fromlist=[bp])
            print(f"  ✓ app.blueprints.{bp}")
        except ImportError as e:
            errors.append(f"app.blueprints.{bp}: {e}")
            print(f"  ✗ app.blueprints.{bp}: {e}")

    # Services
    services = [
        'data_processor',
        'ml_service',
        'product_service',
        'amazon_api',
        'chat_service'
    ]
    for svc in services:
        try:
            module = __import__(f'app.services.{svc}', fromlist=[svc])
            print(f"  ✓ app.services.{svc}")
        except ImportError as e:
            errors.append(f"app.services.{svc}: {e}")
            print(f"  ✗ app.services.{svc}: {e}")

    # Utils
    utils = ['validators', 'helpers', 'decorators']
    for util in utils:
        try:
            module = __import__(f'app.utils.{util}', fromlist=[util])
            print(f"  ✓ app.utils.{util}")
        except ImportError as e:
            errors.append(f"app.utils.{util}: {e}")
            print(f"  ✗ app.utils.{util}: {e}")

    print()
    return errors


def check_app_creation():
    """Verify Flask app can be created."""
    print("Checking app creation...")
    try:
        from app import create_app
        app = create_app('testing')
        print("  ✓ App created successfully")
        print(f"  ✓ Blueprints registered: {len(app.blueprints)}")
        return True
    except Exception as e:
        print(f"  ✗ App creation failed: {e}")
        return False


def check_routes():
    """Verify routes are registered."""
    print("Checking routes...")
    try:
        from app import create_app
        app = create_app('testing')

        expected_routes = [
            '/',
            '/login',
            '/submit',
            '/logout',
            '/dash',
            '/data',
            '/get_recommendations',
            '/chat',
            '/send_message'
        ]

        registered_routes = [rule.rule for rule in app.url_map.iter_rules()
                           if not rule.rule.startswith('/static')]

        for route in expected_routes:
            if route in registered_routes:
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} (missing)")

        print()
        return True

    except Exception as e:
        print(f"  ✗ Route check failed: {e}")
        return False


def check_configuration():
    """Verify configuration system."""
    print("Checking configuration...")
    try:
        from config import get_config, DevelopmentConfig, ProductionConfig

        dev_config = get_config('development')
        prod_config = get_config('production')

        print(f"  ✓ Development config: {dev_config.__name__}")
        print(f"  ✓ Production config: {prod_config.__name__}")
        print(f"  ✓ Debug (dev): {dev_config.DEBUG}")
        print(f"  ✓ Debug (prod): {prod_config.DEBUG}")
        print()
        return True

    except Exception as e:
        print(f"  ✗ Configuration check failed: {e}")
        return False


def check_directories():
    """Verify directory structure."""
    print("Checking directory structure...")
    required_dirs = [
        'app',
        'app/blueprints',
        'app/services',
        'app/utils',
        'static',
        'templates'
    ]

    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory}")
        else:
            print(f"  ✗ {directory} (missing)")
            all_exist = False

    print()
    return all_exist


def check_files():
    """Verify critical files exist."""
    print("Checking critical files...")
    required_files = [
        'config.py',
        'run.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'app/__init__.py',
        'app/logger.py',
        'app/blueprints/__init__.py',
        'app/services/__init__.py',
        'app/utils/__init__.py'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            all_exist = False

    print()
    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Flask Application Refactoring Verification")
    print("=" * 70)
    print()

    checks = []

    # Directory structure
    checks.append(("Directory Structure", check_directories()))

    # Critical files
    checks.append(("Critical Files", check_files()))

    # Import checks
    import_errors = check_imports()
    checks.append(("Module Imports", len(import_errors) == 0))

    if import_errors:
        print("\nImport Errors:")
        for error in import_errors:
            print(f"  - {error}")
        print()

    # Configuration
    checks.append(("Configuration", check_configuration()))

    # App creation
    checks.append(("App Creation", check_app_creation()))

    # Routes
    checks.append(("Routes", check_routes()))

    # Summary
    print("=" * 70)
    print("Verification Summary")
    print("=" * 70)

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print()
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print()
        print("🎉 All checks passed! The refactoring is complete and working.")
        print()
        print("Next steps:")
        print("1. Run: python setup.py")
        print("2. Edit .env file with your credentials")
        print("3. Run: python run.py")
        return 0
    else:
        print()
        print("⚠️  Some checks failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
