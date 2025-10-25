"""
Recommendations blueprint.

This module handles product recommendation routes using ML predictions.
"""

import logging
import multiprocessing
import os

import pandas as pd
from flask import Blueprint, render_template, render_template_string, session, current_app

from app.services import MLService
from app.utils import login_required

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/get_recommendations', methods=['GET', 'POST'])
@login_required
def get_recommendations():
    """
    Display ML-filtered product recommendations.

    Checks if product fetch is complete before showing recommendations.
    """
    try:
        # Check if product fetch process is still running
        pid = session.get('product_fetch_pid')

        if pid:
            # Check if process is alive
            try:
                process = multiprocessing.Process()
                process._popen = type('obj', (object,), {'pid': pid})

                if process.is_alive():
                    return render_template_string(
                        "<p style='text-align:center;font-size:16px;font-style:italic;"
                        "font-family:sans-serif;'>Wait for sometime to fetch the products... "
                        "try again after sometime..</p>"
                    )
            except Exception as e:
                logger.warning(f"Could not check process status: {str(e)}")

        # Check if product file exists
        product_file = current_app.config['PRODUCT_DETAILS_FILE']

        if not os.path.exists(product_file):
            return render_template_string(
                "<p style='text-align:center;font-size:16px;font-style:italic;"
                "font-family:sans-serif;'>Products not yet available. "
                "Please try again in a few moments.</p>"
            )

        # Run ML predictions
        ml_service = MLService(current_app.config)
        ml_service.predict_returns(current_app.config['DATA_FILE'])

        # Read predicted results
        products_df = pd.read_excel(product_file, sheet_name="Results")

        # Filter products with low return risk (result == 0)
        filtered_products = products_df[products_df["result"] == 0].copy()

        # Shuffle products for variety
        shuffled_products = filtered_products.sample(
            frac=1,
            random_state=100
        ).reset_index(drop=True)

        # Convert to dictionary
        products_dict = shuffled_products.to_dict(orient='records')

        logger.info(f"Displaying {len(products_dict)} recommended products")

        return render_template('recommendations.html', products=products_dict)

    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return f"Error loading recommendations: {str(e)}", 500
