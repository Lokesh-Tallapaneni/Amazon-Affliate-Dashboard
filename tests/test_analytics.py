"""
Comprehensive test cases for analytics features.

This module tests all analytics routes, services, and calculations.
"""

import os
import sys
import shutil

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.services import AnalyticsService


# Test data file
DATA_FILE = "1761380244708-Fee-Tracking-f877264f-2299-4fd6-a84e-fb43a1baf6ba-XLSX.xlsx"


def test_analytics_service_initialization():
    """Test analytics service initialization."""
    print("\n" + "="*70)
    print("Test 1: Analytics Service Initialization")
    print("="*70)

    try:
        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)
            assert service is not None
            assert hasattr(service, 'config')
            print("✓ Analytics service initialization: PASS")
            return True
    except Exception as e:
        print(f"✗ Analytics service initialization failed: {e}")
        return False


def test_conversion_analytics():
    """Test conversion rate analytics calculation."""
    print("\n" + "="*70)
    print("Test 2: Conversion Analytics")
    print("="*70)

    try:
        # Ensure data file exists
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)
            data = service.get_conversion_analytics('data.xlsx')

            # Verify returned data structure
            assert 'average_conversion' in data
            assert 'best_day' in data
            assert 'worst_day' in data
            assert 'trend' in data
            assert 'total_clicks' in data
            assert 'total_orders' in data

            # Verify data types
            assert isinstance(data['average_conversion'], (int, float))
            assert isinstance(data['total_clicks'], int)
            assert isinstance(data['total_orders'], int)
            assert data['trend'] in ['up', 'down', 'stable']

            print(f"✓ Conversion analytics calculation: PASS")
            print(f"  - Average conversion: {data['average_conversion']}%")
            print(f"  - Total clicks: {data['total_clicks']}")
            print(f"  - Total orders: {data['total_orders']}")
            print(f"  - Trend: {data['trend']}")
            return True

    except Exception as e:
        print(f"✗ Conversion analytics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_analytics():
    """Test device type analytics calculation."""
    print("\n" + "="*70)
    print("Test 3: Device Analytics")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)
            data = service.get_device_analytics('data.xlsx')

            # Verify returned data structure
            assert 'devices' in data
            assert 'total_revenue' in data
            assert isinstance(data['devices'], list)
            assert len(data['devices']) > 0

            # Verify device data structure
            device = data['devices'][0]
            assert 'Device Type Group' in device
            assert 'Revenue' in device
            assert 'Items Shipped' in device
            assert 'Returns' in device
            assert 'Return_Rate' in device

            print(f"✓ Device analytics calculation: PASS")
            print(f"  - Total revenue: ${data['total_revenue']:.2f}")
            print(f"  - Device types tracked: {len(data['devices'])}")
            return True

    except Exception as e:
        print(f"✗ Device analytics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_link_type_analytics():
    """Test link type analytics calculation."""
    print("\n" + "="*70)
    print("Test 4: Link Type Analytics")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)
            data = service.get_link_type_analytics('data.xlsx')

            # Verify returned data structure
            assert 'link_types' in data
            assert 'best_performer' in data
            assert isinstance(data['link_types'], list)
            assert len(data['link_types']) > 0

            # Verify link type data structure
            link = data['link_types'][0]
            assert 'Link Type' in link
            assert 'Clicks' in link
            assert 'Conversion' in link

            print(f"✓ Link type analytics calculation: PASS")
            print(f"  - Best performer: {data['best_performer']}")
            print(f"  - Link types tracked: {len(data['link_types'])}")
            return True

    except Exception as e:
        print(f"✗ Link type analytics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_returns_analytics():
    """Test returns analytics calculation."""
    print("\n" + "="*70)
    print("Test 5: Returns Analytics")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)
            data = service.get_returns_analytics('data.xlsx')

            # Verify returned data structure
            assert 'overall_return_rate' in data
            assert 'total_returns' in data
            assert 'revenue_lost' in data
            assert 'top_returned_products' in data
            assert 'category_returns' in data

            # Verify data types
            assert isinstance(data['overall_return_rate'], (int, float))
            assert isinstance(data['total_returns'], int)
            assert isinstance(data['revenue_lost'], (int, float))

            print(f"✓ Returns analytics calculation: PASS")
            print(f"  - Overall return rate: {data['overall_return_rate']}%")
            print(f"  - Total returns: {data['total_returns']}")
            print(f"  - Revenue lost: ${data['revenue_lost']:.2f}")
            return True

    except Exception as e:
        print(f"✗ Returns analytics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_seller_analytics():
    """Test seller analytics calculation."""
    print("\n" + "="*70)
    print("Test 6: Seller Analytics")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)
            data = service.get_seller_analytics('data.xlsx')

            # Verify returned data structure
            assert 'sellers' in data
            assert isinstance(data['sellers'], list)
            assert len(data['sellers']) > 0

            # Verify seller data structure
            seller = data['sellers'][0]
            assert 'Seller' in seller
            assert 'Revenue' in seller
            assert 'Items Shipped' in seller
            assert 'Return_Rate' in seller

            print(f"✓ Seller analytics calculation: PASS")
            print(f"  - Seller types tracked: {len(data['sellers'])}")
            return True

    except Exception as e:
        print(f"✗ Seller analytics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_routes():
    """Test analytics blueprint routes."""
    print("\n" + "="*70)
    print("Test 7: Analytics Routes")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        client = app.test_client()

        # Set up session
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        routes_to_test = [
            ('/analytics/overview', 'Analytics Overview'),
            ('/analytics/conversion', 'Conversion Analytics'),
            ('/analytics/devices', 'Device Analytics'),
            ('/analytics/link-types', 'Link Type Analytics'),
            ('/analytics/returns', 'Returns Analytics'),
            ('/analytics/sellers', 'Seller Analytics'),
        ]

        all_pass = True
        for route, name in routes_to_test:
            response = client.get(route)
            if response.status_code == 200:
                print(f"  ✓ {name}: {response.status_code}")
            else:
                print(f"  ✗ {name}: {response.status_code}")
                all_pass = False

        if all_pass:
            print("✓ All analytics routes: PASS")
            return True
        else:
            print("✗ Some analytics routes failed")
            return False

    except Exception as e:
        print(f"✗ Analytics routes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_api_endpoints():
    """Test analytics API endpoints."""
    print("\n" + "="*70)
    print("Test 8: Analytics API Endpoints")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        client = app.test_client()

        # Set up session
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        api_routes = [
            ('/analytics/api/conversion-data', 'Conversion API'),
            ('/analytics/api/device-data', 'Device API'),
        ]

        all_pass = True
        for route, name in api_routes:
            response = client.get(route)
            if response.status_code == 200:
                data = response.get_json()
                if data:
                    print(f"  ✓ {name}: {response.status_code} (JSON returned)")
                else:
                    print(f"  ✗ {name}: No JSON data")
                    all_pass = False
            else:
                print(f"  ✗ {name}: {response.status_code}")
                all_pass = False

        if all_pass:
            print("✓ All analytics API endpoints: PASS")
            return True
        else:
            print("✗ Some API endpoints failed")
            return False

    except Exception as e:
        print(f"✗ Analytics API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chart_generation():
    """Test chart generation for analytics."""
    print("\n" + "="*70)
    print("Test 9: Chart Generation")
    print("="*70)

    try:
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        app = create_app('testing')
        with app.app_context():
            service = AnalyticsService(app.config)

            # Test each chart generation
            charts_generated = []

            # Conversion chart
            data = service.get_conversion_analytics('data.xlsx')
            if data.get('chart_path') and os.path.exists(data['chart_path']):
                charts_generated.append('conversion')

            # Device chart
            data = service.get_device_analytics('data.xlsx')
            if data.get('chart_path') and os.path.exists(data['chart_path']):
                charts_generated.append('device')

            # Link type chart
            data = service.get_link_type_analytics('data.xlsx')
            if data.get('chart_path') and os.path.exists(data['chart_path']):
                charts_generated.append('link_type')

            # Returns chart
            data = service.get_returns_analytics('data.xlsx')
            if data.get('chart_path') and os.path.exists(data['chart_path']):
                charts_generated.append('returns')

            # Seller chart
            data = service.get_seller_analytics('data.xlsx')
            if data.get('chart_path') and os.path.exists(data['chart_path']):
                charts_generated.append('seller')

            print(f"✓ Chart generation: PASS")
            print(f"  - Charts generated: {len(charts_generated)}/5")
            print(f"  - Types: {', '.join(charts_generated)}")
            return len(charts_generated) == 5

    except Exception as e:
        print(f"✗ Chart generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all analytics tests."""
    print("="*70)
    print("ANALYTICS FEATURES - COMPREHENSIVE TESTING")
    print("="*70)

    results = {}

    # Run all tests
    results['service_init'] = test_analytics_service_initialization()
    results['conversion'] = test_conversion_analytics()
    results['devices'] = test_device_analytics()
    results['link_types'] = test_link_type_analytics()
    results['returns'] = test_returns_analytics()
    results['sellers'] = test_seller_analytics()
    results['routes'] = test_analytics_routes()
    results['api_endpoints'] = test_analytics_api_endpoints()
    results['charts'] = test_chart_generation()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY - ANALYTICS FEATURES")
    print("="*70)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL ANALYTICS TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review issues above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
