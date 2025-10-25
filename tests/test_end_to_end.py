"""
End-to-end testing with real credentials.

This script tests the complete application flow with actual Amazon API credentials.
"""

import os
import sys
import shutil
import time

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.services import AmazonAPIService, MLService, DataProcessor

# Read updated credentials
with open('../api_credentials.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    API_KEY = lines[0]
    SECRET_KEY = lines[1]
    ASSOCIATE_TAG = lines[2]

DATA_FILE = "../1761380244708-Fee-Tracking-f877264f-2299-4fd6-a84e-fb43a1baf6ba-XLSX.xlsx"


def test_amazon_credentials():
    """Test Amazon API with updated credentials."""
    print("\n" + "="*70)
    print("1. Testing Amazon API Credentials")
    print("="*70)

    try:
        amazon_service = AmazonAPIService(API_KEY, SECRET_KEY, ASSOCIATE_TAG)
        result = amazon_service.verify_credentials()

        if result:
            print("✓ Amazon API credentials: VALID")
            return True
        else:
            print("✗ Amazon API credentials: INVALID")
            return False
    except Exception as e:
        print(f"✗ Amazon API test failed: {e}")
        return False


def test_product_search():
    """Test product search functionality."""
    print("\n" + "="*70)
    print("2. Testing Product Search")
    print("="*70)

    try:
        amazon_service = AmazonAPIService(API_KEY, SECRET_KEY, ASSOCIATE_TAG)
        products = amazon_service.search_products("laptop")

        if products and len(products) > 0:
            print(f"✓ Product search: Found {len(products)} products")
            print(f"  Sample product: {products[0]['Product_Name'][:50]}...")
            return True
        else:
            print("✗ Product search: No products found")
            return False
    except Exception as e:
        print(f"✗ Product search failed: {e}")
        return False


def test_ml_training():
    """Test ML model training."""
    print("\n" + "="*70)
    print("3. Testing ML Model Training")
    print("="*70)

    try:
        # Ensure data file exists
        if not os.path.exists('../data.xlsx'):
            shutil.copy(DATA_FILE, '../data.xlsx')
            print("  Copied data.xlsx")

        app = create_app('testing')
        with app.app_context():
            ml_service = MLService(app.config)
            ml_service.train_model('data.xlsx')

        # Verify model files
        if os.path.exists('cmodel_pkl') and os.path.exists('feature_extraction'):
            print("✓ ML model training: SUCCESS")
            print("  - Model file created: cmodel_pkl")
            print("  - Feature extraction created: feature_extraction")
            return True
        else:
            print("✗ ML model training: Model files not created")
            return False
    except Exception as e:
        print(f"✗ ML model training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_processing():
    """Test data processing and chart generation."""
    print("\n" + "="*70)
    print("4. Testing Data Processing & Chart Generation")
    print("="*70)

    try:
        app = create_app('testing')
        with app.app_context():
            processor = DataProcessor(app.config)

            # Extract dates
            from app.utils import extract_dates_from_excel
            start_date, end_date, one_month_ago = extract_dates_from_excel('data.xlsx')

            print(f"  Date range: {start_date} to {end_date}")

            # Process data
            max_fee, max_qty = processor.process_data('data.xlsx', one_month_ago, end_date)

            # Check charts
            charts = ['dash.png', 'piepic.png', 'barpic.png', 'returns.png']
            all_exist = all(os.path.exists(f'static/images/{chart}') for chart in charts)

            if all_exist:
                print("✓ Data processing: SUCCESS")
                print(f"  - Charts generated: {len(charts)}/4")
                print(f"  - Max fee products: {len(max_fee)}")
                print(f"  - Max quantity products: {len(max_qty)}")
                return True
            else:
                missing = [c for c in charts if not os.path.exists(f'static/images/{c}')]
                print(f"✗ Data processing: Missing charts {missing}")
                return False
    except Exception as e:
        print(f"✗ Data processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_application_routes():
    """Test application routes."""
    print("\n" + "="*70)
    print("5. Testing Application Routes")
    print("="*70)

    try:
        app = create_app('testing')
        client = app.test_client()

        routes_to_test = [
            ('/', 'Index'),
            ('/login', 'Login Page'),
        ]

        all_pass = True
        for route, name in routes_to_test:
            response = client.get(route)
            if response.status_code in [200, 302]:
                print(f"  ✓ {name}: {response.status_code}")
            else:
                print(f"  ✗ {name}: {response.status_code}")
                all_pass = False

        # Test protected routes with session
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        protected_routes = [
            ('/dash', 'Dashboard'),
            ('/data', 'Data View'),
            ('/get_recommendations', 'Recommendations'),
            ('/chat', 'Chat'),
        ]

        for route, name in protected_routes:
            response = client.get(route)
            if response.status_code == 200:
                print(f"  ✓ {name}: {response.status_code}")
            else:
                print(f"  ✗ {name}: {response.status_code}")
                all_pass = False

        if all_pass:
            print("✓ All routes: PASS")
            return True
        else:
            print("✗ Some routes failed")
            return False
    except Exception as e:
        print(f"✗ Route testing failed: {e}")
        return False


def test_folder_structure():
    """Verify folder structure."""
    print("\n" + "="*70)
    print("6. Testing Folder Structure")
    print("="*70)

    required_dirs = [
        'app',
        'app/blueprints',
        'app/services',
        'app/utils',
        'static',
        'static/images',
        'templates',
        'logs',
        'uploads',
        'venv'
    ]

    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory}")
        else:
            print(f"  ✗ {directory} (missing)")
            all_exist = False

    if all_exist:
        print("✓ Folder structure: COMPLETE")
        return True
    else:
        print("✗ Folder structure: INCOMPLETE")
        return False


def main():
    """Run all end-to-end tests."""
    print("="*70)
    print("END-TO-END TESTING WITH REAL CREDENTIALS")
    print("="*70)

    results = {}

    # Test 1: Amazon credentials
    results['amazon_credentials'] = test_amazon_credentials()

    # Test 2: Product search (only if credentials valid)
    if results['amazon_credentials']:
        results['product_search'] = test_product_search()
    else:
        print("\n⚠️  Skipping product search (credentials invalid)")
        results['product_search'] = False

    # Test 3: ML training
    results['ml_training'] = test_ml_training()

    # Test 4: Data processing
    results['data_processing'] = test_data_processing()

    # Test 5: Application routes
    results['routes'] = test_application_routes()

    # Test 6: Folder structure
    results['folder_structure'] = test_folder_structure()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - PRODUCTION READY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review issues above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
