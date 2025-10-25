"""
Dashboard blueprint.

This module handles the main dashboard routes and data visualization.
"""

import logging
from datetime import datetime

import pandas as pd
from flask import Blueprint, render_template, request, current_app

from app.services import DataProcessor
from app.utils import login_required, extract_dates_from_excel, get_summary_data

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dash', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Display main dashboard with charts and data.

    Supports date range filtering via POST request.
    """
    try:
        data_file = current_app.config['DATA_FILE']

        # Extract date range from Excel file
        start_date, end_date, one_month_ago = extract_dates_from_excel(data_file)

        if not start_date or not end_date:
            logger.error("Could not extract dates from data file")
            return "Error: Could not extract date information from file", 500

        # Get summary data
        summary_df = get_summary_data(data_file)

        # Handle date filtering
        if request.method == 'POST':
            from_date = request.form.get('from_date', one_month_ago)
            to_date = request.form.get('to_date', end_date)

            # Validate dates
            try:
                from_date = datetime.strptime(from_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                logger.warning("Invalid date format, using defaults")
                from_date = one_month_ago
                to_date = end_date
        else:
            from_date = one_month_ago
            to_date = end_date

        # Process data and generate visualizations
        data_processor = DataProcessor(current_app.config)
        max_fee_products, max_quantity_products = data_processor.process_data(
            data_file,
            from_date,
            to_date
        )

        # Format max fee products
        max_fee_products = max_fee_products[
            pd.to_datetime(
                max_fee_products['Date Shipped'],
                format='%Y-%m-%d',
                errors='coerce'
            ).notna()
        ].copy()

        max_fee_products['Date Shipped'] = pd.to_datetime(
            max_fee_products['Date Shipped']
        ).dt.strftime('%Y-%m-%d')

        max_fee_products = max_fee_products.drop('Direct Sale', axis=1, errors='ignore')

        # Convert to dictionaries for template
        max_fee_dict = max_fee_products.to_dict(orient='records')
        max_quantity_dict = max_quantity_products.to_dict(orient='records')
        summary_dict = summary_df.to_dict(orient='records')

        return render_template(
            'dash.html',
            sm=summary_dict,
            mx_fee=max_fee_dict,
            mx_quan=max_quantity_dict,
            start_date=start_date,
            end_date=end_date,
            from_date=from_date,
            to_date=to_date
        )

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return f"Error loading dashboard: {str(e)}", 500
