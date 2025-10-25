"""
Test script to verify all components of the refactored application.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services import AmazonAPIService, MLService, DataProcessor
from app import create_app

# Read credentials
with open('api_credentials.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    API_KEY = lines[0]
    SECRET_KEY = lines[1]
    ASSOCIATE_TAG = lines[2]

DATA_FILE = "1761380244708-Fee-Tracking-f877264f-2299-4fd6-a84e-fb43a1baf6ba-XLSX.xlsx"

def test_amazon_api():
    """Test Amazon API service."""
    print("\n=== Testing Amazon API Service ===")
    try:
        amazon_service = AmazonAPIService(API_KEY, SECRET_KEY, ASSOCIATE_TAG)
        result = amazon_service.verify_credentials()
        print(f"Credentials verification: {'PASS' if result else 'FAIL'}")
        return result
    except Exception as e:
        print(f"Amazon API test FAILED: {e}")
        return False


def test_ml_service():
    """Test ML model training."""
    print("\n=== Testing ML Service ===")
    try:
        app = create_app('testing')
        with app.app_context():
            ml_service = MLService(app.config)

            # Copy file to expected location
            import shutil
            if not os.path.exists('data.xlsx'):
                shutil.copy(DATA_FILE, 'data.xlsx')

            ml_service.train_model('data.xlsx')
            print("ML model training: PASS")

            # Check if model files were created
            if os.path.exists('cmodel_pkl') and os.path.exists('feature_extraction'):
                print("Model files created: PASS")
                return True
            else:
                print("Model files NOT created: FAIL")
                return False
    except Exception as e:
        print(f"ML Service test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_processor():
    """Test data processing and chart generation."""
    print("\n=== Testing Data Processor ===")
    try:
        app = create_app('testing')
        with app.app_context():
            processor = DataProcessor(app.config)

            # Ensure data file exists
            import shutil
            if not os.path.exists('data.xlsx'):
                shutil.copy(DATA_FILE, 'data.xlsx')

            # Test date extraction
            from app.utils import extract_dates_from_excel
            start_date, end_date, one_month_ago = extract_dates_from_excel('data.xlsx')

            if start_date and end_date:
                print(f"Date extraction: PASS (from {start_date} to {end_date})")

                # Test data processing
                max_fee, max_qty = processor.process_data('data.xlsx', one_month_ago, end_date)
                print(f"Data processing: PASS")
                print(f"  - Max fee products: {len(max_fee)}")
                print(f"  - Max quantity products: {len(max_qty)}")

                # Check if charts were created
                charts = ['dash.png', 'piepic.png', 'barpic.png', 'returns.png']
                all_exist = all(os.path.exists(f'static/images/{chart}') for chart in charts)

                if all_exist:
                    print("Chart generation: PASS (all 4 charts created)")
                    return True
                else:
                    missing = [c for c in charts if not os.path.exists(f'static/images/{c}')]
                    print(f"Chart generation: PARTIAL (missing: {missing})")
                    return False
            else:
                print("Date extraction: FAIL")
                return False

    except Exception as e:
        print(f"Data Processor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Component Testing for Refactored Flask Application")
    print("=" * 70)

    results = {}

    # Test Amazon API
    results['amazon_api'] = test_amazon_api()

    # Test ML Service
    results['ml_service'] = test_ml_service()

    # Test Data Processor
    results['data_processor'] = test_data_processor()

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
