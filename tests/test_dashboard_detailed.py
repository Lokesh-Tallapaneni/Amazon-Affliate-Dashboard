"""
Detailed dashboard testing to find the issue.
"""

import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

DATA_FILE = "1761380244708-Fee-Tracking-f877264f-2299-4fd6-a84e-fb43a1baf6ba-XLSX.xlsx"

def test_dashboard():
    """Test dashboard in detail."""
    print("\nTesting Dashboard...")

    # Ensure data file exists
    if not os.path.exists('data.xlsx'):
        shutil.copy(DATA_FILE, 'data.xlsx')
        print("✓ Copied data.xlsx")

    app = create_app('testing')
    client = app.test_client()

    try:
        with client.session_transaction() as sess:
            sess['logged_in'] = True

        response = client.get('/dash')

        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print("Response data:")
            print(response.data.decode('utf-8')[:500])

        return response.status_code == 200

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_dashboard()
