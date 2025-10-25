"""
Data display blueprint.

This module handles routes for displaying raw data tables.
"""

import logging

import pandas as pd
from flask import Blueprint, render_template, current_app

from app.utils import login_required

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)


@data_bp.route('/data', methods=['GET'])
@login_required
def view_data():
    """
    Display raw earnings data in table format.

    Returns:
        Rendered template with data table
    """
    try:
        data_file = current_app.config['DATA_FILE']

        # Read Excel file
        df = pd.read_excel(data_file, sheet_name="Fee-Earnings")

        # Set first row as headers
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        # Filter valid dates
        df = df[
            pd.to_datetime(
                df['Date Shipped'],
                format='%Y-%m-%d %H:%M:%S',
                errors='coerce'
            ).notna()
        ].copy()

        # Format dates
        df['Date Shipped'] = pd.to_datetime(df['Date Shipped']).dt.strftime('%Y-%m-%d')

        # Remove Direct Sale column if exists
        df = df.drop('Direct Sale', axis=1, errors='ignore')

        # Convert to dictionary for template
        data_dict = df.to_dict(orient='records')

        return render_template('excel_products.html', data=data_dict)

    except Exception as e:
        logger.error(f"Error displaying data: {str(e)}")
        return f"Error loading data: {str(e)}", 500
