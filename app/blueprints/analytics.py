"""
Analytics blueprint.

This module handles advanced analytics routes including conversion rates,
device performance, link types, returns analysis, and seller performance.
"""

import logging
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app

from app.services import AnalyticsService
from app.utils import login_required

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/conversion')
@login_required
def conversion_analytics():
    """Display conversion rate analytics dashboard."""
    try:
        # Get date filters from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_conversion_analytics(
            current_app.config['DATA_FILE'],
            start_date,
            end_date
        )

        return render_template('analytics/conversion.html', data=data)

    except Exception as e:
        logger.error(f"Error in conversion analytics: {e}")
        return render_template('analytics/conversion.html', error=str(e))


@analytics_bp.route('/devices')
@login_required
def device_analytics():
    """Display device type performance dashboard."""
    try:
        # Get date filters from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_device_analytics(
            current_app.config['DATA_FILE'],
            start_date,
            end_date
        )

        return render_template('analytics/devices.html', data=data)

    except Exception as e:
        logger.error(f"Error in device analytics: {e}")
        return render_template('analytics/devices.html', error=str(e))


@analytics_bp.route('/link-types')
@login_required
def link_type_analytics():
    """Display link type performance dashboard."""
    try:
        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_link_type_analytics(current_app.config['DATA_FILE'])

        return render_template('analytics/link_types.html', data=data)

    except Exception as e:
        logger.error(f"Error in link type analytics: {e}")
        return render_template('analytics/link_types.html', error=str(e))


@analytics_bp.route('/returns')
@login_required
def returns_analytics():
    """Display enhanced returns analysis dashboard."""
    try:
        # Get date filters from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_returns_analytics(
            current_app.config['DATA_FILE'],
            start_date,
            end_date
        )

        return render_template('analytics/returns.html', data=data)

    except Exception as e:
        logger.error(f"Error in returns analytics: {e}")
        return render_template('analytics/returns.html', error=str(e))


@analytics_bp.route('/sellers')
@login_required
def seller_analytics():
    """Display seller performance comparison dashboard."""
    try:
        # Get date filters from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_seller_analytics(
            current_app.config['DATA_FILE'],
            start_date,
            end_date
        )

        return render_template('analytics/sellers.html', data=data)

    except Exception as e:
        logger.error(f"Error in seller analytics: {e}")
        return render_template('analytics/sellers.html', error=str(e))


@analytics_bp.route('/overview')
@login_required
def analytics_overview():
    """Display analytics overview with quick stats from all categories."""
    try:
        analytics_service = AnalyticsService(current_app.config)

        # Get quick stats from each analytics type
        conversion_data = analytics_service.get_conversion_analytics(current_app.config['DATA_FILE'])
        device_data = analytics_service.get_device_analytics(current_app.config['DATA_FILE'])
        link_data = analytics_service.get_link_type_analytics(current_app.config['DATA_FILE'])
        returns_data = analytics_service.get_returns_analytics(current_app.config['DATA_FILE'])

        overview_data = {
            'conversion': {
                'average': conversion_data['average_conversion'],
                'trend': conversion_data['trend'],
                'total_clicks': conversion_data['total_clicks'],
                'total_orders': conversion_data['total_orders']
            },
            'devices': {
                'total_revenue': device_data['total_revenue'],
                'device_count': len(device_data['devices'])
            },
            'link_types': {
                'best_performer': link_data['best_performer'],
                'link_count': len(link_data['link_types'])
            },
            'returns': {
                'return_rate': returns_data['overall_return_rate'],
                'revenue_lost': returns_data['revenue_lost'],
                'total_returns': returns_data['total_returns']
            }
        }

        return render_template('analytics/overview.html', data=overview_data)

    except Exception as e:
        logger.error(f"Error in analytics overview: {e}")
        return render_template('analytics/overview.html', error=str(e))


# API endpoints for AJAX requests
@analytics_bp.route('/api/conversion-data')
@login_required
def api_conversion_data():
    """API endpoint for conversion data (for AJAX)."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_conversion_analytics(
            current_app.config['DATA_FILE'],
            start_date,
            end_date
        )

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error in conversion API: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/api/device-data')
@login_required
def api_device_data():
    """API endpoint for device data (for AJAX)."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        analytics_service = AnalyticsService(current_app.config)
        data = analytics_service.get_device_analytics(
            current_app.config['DATA_FILE'],
            start_date,
            end_date
        )

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error in device API: {e}")
        return jsonify({'error': str(e)}), 500
