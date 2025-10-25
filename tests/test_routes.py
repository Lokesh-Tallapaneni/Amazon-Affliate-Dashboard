"""
Comprehensive route testing for the refactored Flask application.
"""

import os
import sys
import shutil
from io import BytesIO

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

DATA_FILE = "1761380244708-Fee-Tracking-f877264f-2299-4fd6-a84e-fb43a1baf6ba-XLSX.xlsx"


def test_routes():
    """Test all routes."""
    print("\n" + "=" * 70)
    print("Route Testing")
    print("=" * 70)

    app = create_app('testing')
    client = app.test_client()

    results = {}

    # Test 1: Index redirect
    print("\n[1/9] Testing index redirect...")
    try:
        response = client.get('/')
        if response.status_code == 302 and '/login' in response.location:
            print("✓ Index redirect: PASS")
            results['index_redirect'] = True
        else:
            print("✗ Index redirect: FAIL")
            results['index_redirect'] = False
    except Exception as e:
        print(f"✗ Index redirect: FAIL - {e}")
        results['index_redirect'] = False

    # Test 2: Login page
    print("\n[2/9] Testing login page...")
    try:
        response = client.get('/login')
        if response.status_code == 200:
            print("✓ Login page: PASS")
            results['login_page'] = True
        else:
            print("✗ Login page: FAIL")
            results['login_page'] = False
    except Exception as e:
        print(f"✗ Login page: FAIL - {e}")
        results['login_page'] = False

    # Test 3: Protected routes without login
    print("\n[3/9] Testing protected routes (should redirect)...")
    protected_routes = ['/dash', '/data', '/get_recommendations', '/chat']
    all_protected = True

    for route in protected_routes:
        try:
            response = client.get(route)
            if response.status_code == 302 and '/login' in response.location:
                print(f"  ✓ {route} protected")
            else:
                print(f"  ✗ {route} NOT protected")
                all_protected = False
        except Exception as e:
            print(f"  ✗ {route} error: {e}")
            all_protected = False

    results['protected_routes'] = all_protected
    print(f"✓ Protected routes: {'PASS' if all_protected else 'FAIL'}")

    # Test 4: Login submission (with file)
    print("\n[4/9] Testing login submission...")
    try:
        # Prepare Excel file
        if not os.path.exists('data.xlsx'):
            shutil.copy(DATA_FILE, 'data.xlsx')

        with open('data.xlsx', 'rb') as f:
            file_data = f.read()

        data = {
            'api_key': 'test_key',
            'secret_key': 'test_secret',
            'associate_tag': 'test_tag',
            'api_file': (BytesIO(file_data), 'data.xlsx')
        }

        with client:
            response = client.post('/submit', data=data, content_type='multipart/form-data', follow_redirects=False)

            # Should fail with invalid credentials but process the file
            if response.status_code in [200, 302]:
                print("✓ Login submission processed: PASS")
                results['login_submission'] = True
            else:
                print(f"✗ Login submission: FAIL (status: {response.status_code})")
                results['login_submission'] = False
    except Exception as e:
        print(f"✗ Login submission: FAIL - {e}")
        results['login_submission'] = False

    # Test 5: Test dashboard with session
    print("\n[5/9] Testing dashboard with session...")
    try:
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        response = client.get('/dash')
        if response.status_code == 200:
            print("✓ Dashboard: PASS")
            results['dashboard'] = True
        else:
            print(f"✗ Dashboard: FAIL (status: {response.status_code})")
            results['dashboard'] = False
    except Exception as e:
        print(f"✗ Dashboard: FAIL - {e}")
        import traceback
        traceback.print_exc()
        results['dashboard'] = False

    # Test 6: Test data view
    print("\n[6/9] Testing data view...")
    try:
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        response = client.get('/data')
        if response.status_code == 200:
            print("✓ Data view: PASS")
            results['data_view'] = True
        else:
            print(f"✗ Data view: FAIL")
            results['data_view'] = False
    except Exception as e:
        print(f"✗ Data view: FAIL - {e}")
        results['data_view'] = False

    # Test 7: Test recommendations
    print("\n[7/9] Testing recommendations...")
    try:
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        response = client.get('/get_recommendations')
        # Should show waiting or recommendations
        if response.status_code == 200:
            print("✓ Recommendations: PASS")
            results['recommendations'] = True
        else:
            print(f"✗ Recommendations: FAIL")
            results['recommendations'] = False
    except Exception as e:
        print(f"✗ Recommendations: FAIL - {e}")
        results['recommendations'] = False

    # Test 8: Test chat page
    print("\n[8/9] Testing chat page...")
    try:
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        response = client.get('/chat')
        if response.status_code == 200:
            print("✓ Chat page: PASS")
            results['chat_page'] = True
        else:
            print(f"✗ Chat page: FAIL")
            results['chat_page'] = False
    except Exception as e:
        print(f"✗ Chat page: FAIL - {e}")
        results['chat_page'] = False

    # Test 9: Test logout
    print("\n[9/9] Testing logout...")
    try:
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        response = client.post('/logout', follow_redirects=False)
        if response.status_code == 302 and '/login' in response.location:
            print("✓ Logout: PASS")
            results['logout'] = True
        else:
            print(f"✗ Logout: FAIL")
            results['logout'] = False
    except Exception as e:
        print(f"✗ Logout: FAIL - {e}")
        results['logout'] = False

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
    sys.exit(test_routes())
