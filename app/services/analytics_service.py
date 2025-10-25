"""
Analytics service for advanced data analysis.

This module provides analytics calculations for conversion rates,
device performance, link types, returns analysis, and more.
"""

import logging
from typing import Dict, List, Tuple, Any
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for advanced analytics calculations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize analytics service."""
        self.config = config
        self.images_folder = config.get('IMAGES_FOLDER') if hasattr(config, 'get') else config.IMAGES_FOLDER

    def get_conversion_analytics(self, data_file: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Calculate conversion rate analytics from Fee-DailyTrends sheet.

        Args:
            data_file: Path to Excel file
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)

        Returns:
            Dictionary with conversion analytics and chart paths
        """
        try:
            # Read Fee-DailyTrends sheet
            file = pd.ExcelFile(data_file)
            df = pd.read_excel(file, sheet_name='Fee-DailyTrends')

            # Set proper headers
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

            # Convert date column
            df['Date'] = pd.to_datetime(df['Date'])

            # Filter by date range
            if start_date:
                df = df[df['Date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['Date'] <= pd.to_datetime(end_date)]

            # Convert numeric columns
            df['Conversion'] = pd.to_numeric(df['Conversion'], errors='coerce').fillna(0)
            df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
            df['Total Items Ordered'] = pd.to_numeric(df['Total Items Ordered'], errors='coerce').fillna(0)

            # Calculate metrics
            avg_conversion = df['Conversion'].mean()
            best_day = df.loc[df['Conversion'].idxmax()] if len(df) > 0 else None
            worst_day = df.loc[df['Conversion'].idxmin()] if len(df) > 0 else None

            # Calculate trend
            if len(df) >= 7:
                recent_avg = df.tail(7)['Conversion'].mean()
                previous_avg = df.iloc[-14:-7]['Conversion'].mean() if len(df) >= 14 else avg_conversion
                trend = "up" if recent_avg > previous_avg else "down"
            else:
                trend = "stable"

            # Generate charts
            chart_path = self._create_conversion_chart(df)

            return {
                'average_conversion': round(avg_conversion, 2),
                'best_day': {
                    'date': best_day['Date'].strftime('%Y-%m-%d') if best_day is not None else None,
                    'conversion': float(best_day['Conversion']) if best_day is not None else 0
                },
                'worst_day': {
                    'date': worst_day['Date'].strftime('%Y-%m-%d') if worst_day is not None else None,
                    'conversion': float(worst_day['Conversion']) if worst_day is not None else 0
                },
                'trend': trend,
                'chart_path': chart_path,
                'total_clicks': int(df['Clicks'].sum()),
                'total_orders': int(df['Total Items Ordered'].sum())
            }

        except Exception as e:
            logger.error(f"Error in conversion analytics: {e}")
            raise

    def _create_conversion_chart(self, df: pd.DataFrame) -> str:
        """Create conversion rate trend chart."""
        try:
            plt.figure(figsize=(12, 6))

            # Line chart for conversion over time
            plt.plot(df['Date'], df['Conversion'], marker='o', linewidth=2, markersize=4)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Conversion Rate (%)', fontsize=12)
            plt.title('Daily Conversion Rate Trend', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            chart_path = f"{self.images_folder}/conversion_trend.png"
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating conversion chart: {e}")
            plt.close()
            raise

    def get_device_analytics(self, data_file: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Analyze performance by device type from Fee-Earnings sheet.

        Args:
            data_file: Path to Excel file
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)

        Returns:
            Dictionary with device analytics and chart paths
        """
        try:
            # Read Fee-Earnings sheet
            file = pd.ExcelFile(data_file)
            df = pd.read_excel(file, sheet_name='Fee-Earnings')

            # Set proper headers
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

            # Convert date column
            df['Date Shipped'] = pd.to_datetime(df['Date Shipped'], errors='coerce')

            # Filter by date range
            if start_date:
                df = df[df['Date Shipped'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['Date Shipped'] <= pd.to_datetime(end_date)]

            # Convert numeric columns
            df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
            df['Items Shipped'] = pd.to_numeric(df['Items Shipped'], errors='coerce').fillna(0)
            df['Returns'] = pd.to_numeric(df['Returns'], errors='coerce').fillna(0)

            # Group by device type
            device_stats = df.groupby('Device Type Group').agg({
                'Revenue': 'sum',
                'Items Shipped': 'sum',
                'Returns': 'sum'
            }).reset_index()

            # Calculate metrics
            device_stats['Return_Rate'] = (device_stats['Returns'] /
                                          (device_stats['Items Shipped'] + device_stats['Returns']) * 100).fillna(0)

            # Generate charts
            chart_path = self._create_device_chart(device_stats)

            # Convert to dict for JSON serialization
            devices_data = device_stats.to_dict('records')
            for device in devices_data:
                device['Revenue'] = float(device['Revenue'])
                device['Items Shipped'] = int(device['Items Shipped'])
                device['Returns'] = int(device['Returns'])
                device['Return_Rate'] = round(float(device['Return_Rate']), 2)

            return {
                'devices': devices_data,
                'chart_path': chart_path,
                'total_revenue': float(device_stats['Revenue'].sum())
            }

        except Exception as e:
            logger.error(f"Error in device analytics: {e}")
            raise

    def _create_device_chart(self, device_stats: pd.DataFrame) -> str:
        """Create device performance chart."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Revenue pie chart
            ax1.pie(device_stats['Revenue'], labels=device_stats['Device Type Group'],
                   autopct='%1.1f%%', startangle=90)
            ax1.set_title('Revenue Distribution by Device', fontsize=14, fontweight='bold')

            # Orders bar chart
            ax2.bar(device_stats['Device Type Group'], device_stats['Items Shipped'])
            ax2.set_xlabel('Device Type', fontsize=12)
            ax2.set_ylabel('Items Shipped', fontsize=12)
            ax2.set_title('Orders by Device Type', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)

            plt.tight_layout()

            chart_path = f"{self.images_folder}/device_analysis.png"
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating device chart: {e}")
            plt.close()
            raise

    def get_link_type_analytics(self, data_file: str) -> Dict[str, Any]:
        """
        Analyze performance by link type from Fee-LinkType sheet.

        Args:
            data_file: Path to Excel file

        Returns:
            Dictionary with link type analytics and chart paths
        """
        try:
            # Read Fee-LinkType sheet
            file = pd.ExcelFile(data_file)
            df = pd.read_excel(file, sheet_name='Fee-LinkType')

            # Set proper headers
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

            # Convert numeric columns
            numeric_cols = ['Clicks', 'Items Ordered', 'Conversion', 'Ordered Revenue($)',
                          'Items Shipped', 'Ad Fees($)']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Calculate ROI
            df['ROI'] = ((df['Ordered Revenue($)'] - df['Ad Fees($)']) / df['Ad Fees($)'] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)

            # Generate charts
            chart_path = self._create_link_type_chart(df)

            # Convert to dict
            link_data = df.to_dict('records')
            for link in link_data:
                for key in link:
                    if isinstance(link[key], (int, float)) and key != 'Link Type':
                        link[key] = float(link[key])

            return {
                'link_types': link_data,
                'chart_path': chart_path,
                'best_performer': df.loc[df['Ordered Revenue($)'].idxmax()]['Link Type'] if len(df) > 0 else None
            }

        except Exception as e:
            logger.error(f"Error in link type analytics: {e}")
            raise

    def _create_link_type_chart(self, df: pd.DataFrame) -> str:
        """Create link type performance chart."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Revenue bar chart
            ax1.barh(df['Link Type'], df['Ordered Revenue($)'])
            ax1.set_xlabel('Revenue ($)', fontsize=12)
            ax1.set_title('Revenue by Link Type', fontsize=14, fontweight='bold')

            # Conversion comparison
            ax2.bar(df['Link Type'], df['Conversion'])
            ax2.set_ylabel('Conversion Rate (%)', fontsize=12)
            ax2.set_title('Conversion Rate by Link Type', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)

            plt.tight_layout()

            chart_path = f"{self.images_folder}/link_type_analysis.png"
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating link type chart: {e}")
            plt.close()
            raise

    def get_returns_analytics(self, data_file: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Enhanced returns analysis from Fee-Earnings sheet.

        Args:
            data_file: Path to Excel file
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)

        Returns:
            Dictionary with returns analytics and chart paths
        """
        try:
            # Read Fee-Earnings sheet
            file = pd.ExcelFile(data_file)
            df = pd.read_excel(file, sheet_name='Fee-Earnings')

            # Set proper headers
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

            # Convert date column
            df['Date Shipped'] = pd.to_datetime(df['Date Shipped'], errors='coerce')

            # Filter by date range
            if start_date:
                df = df[df['Date Shipped'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['Date Shipped'] <= pd.to_datetime(end_date)]

            # Convert numeric columns
            df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
            df['Items Shipped'] = pd.to_numeric(df['Items Shipped'], errors='coerce').fillna(0)
            df['Returns'] = pd.to_numeric(df['Returns'], errors='coerce').fillna(0)

            # Calculate return metrics
            total_shipped = df['Items Shipped'].sum()
            total_returns = df['Returns'].sum()
            return_rate = (total_returns / (total_shipped + total_returns) * 100) if (total_shipped + total_returns) > 0 else 0

            # Revenue lost to returns
            revenue_lost = df[df['Returns'] > 0]['Revenue'].abs().sum()

            # Returns by category
            category_returns = df.groupby('Category').agg({
                'Returns': 'sum',
                'Items Shipped': 'sum',
                'Revenue': lambda x: x[x < 0].abs().sum()
            }).reset_index()

            category_returns['Return_Rate'] = (
                category_returns['Returns'] /
                (category_returns['Items Shipped'] + category_returns['Returns']) * 100
            ).fillna(0)

            # Top products with returns
            product_returns = df[df['Returns'] > 0].groupby(['Name', 'ASIN']).agg({
                'Returns': 'sum',
                'Revenue': lambda x: x.abs().sum()
            }).reset_index().sort_values('Returns', ascending=False).head(10)

            # Generate charts
            chart_path = self._create_returns_chart(df, category_returns)

            return {
                'overall_return_rate': round(return_rate, 2),
                'total_returns': int(total_returns),
                'revenue_lost': float(revenue_lost),
                'top_returned_products': product_returns.to_dict('records'),
                'category_returns': category_returns.to_dict('records'),
                'chart_path': chart_path
            }

        except Exception as e:
            logger.error(f"Error in returns analytics: {e}")
            raise

    def _create_returns_chart(self, df: pd.DataFrame, category_returns: pd.DataFrame) -> str:
        """Create enhanced returns analysis chart."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Returns trend over time
            df_sorted = df.sort_values('Date Shipped')
            df_sorted['Cumulative_Returns'] = df_sorted['Returns'].cumsum()

            ax1.plot(df_sorted['Date Shipped'], df_sorted['Cumulative_Returns'], linewidth=2)
            ax1.set_xlabel('Date', fontsize=12)
            ax1.set_ylabel('Cumulative Returns', fontsize=12)
            ax1.set_title('Returns Trend Over Time', fontsize=14, fontweight='bold')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)

            # Returns by category
            top_categories = category_returns.nlargest(10, 'Returns')
            ax2.barh(top_categories['Category'], top_categories['Returns'])
            ax2.set_xlabel('Number of Returns', fontsize=12)
            ax2.set_title('Top 10 Categories by Returns', fontsize=14, fontweight='bold')

            plt.tight_layout()

            chart_path = f"{self.images_folder}/returns_analysis.png"
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating returns chart: {e}")
            plt.close()
            raise

    def get_seller_analytics(self, data_file: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Analyze performance by seller type from Fee-Earnings sheet.

        Args:
            data_file: Path to Excel file
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)

        Returns:
            Dictionary with seller analytics
        """
        try:
            # Read Fee-Earnings sheet
            file = pd.ExcelFile(data_file)
            df = pd.read_excel(file, sheet_name='Fee-Earnings')

            # Set proper headers
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

            # Convert date column
            df['Date Shipped'] = pd.to_datetime(df['Date Shipped'], errors='coerce')

            # Filter by date range
            if start_date:
                df = df[df['Date Shipped'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['Date Shipped'] <= pd.to_datetime(end_date)]

            # Convert numeric columns
            df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
            df['Items Shipped'] = pd.to_numeric(df['Items Shipped'], errors='coerce').fillna(0)
            df['Returns'] = pd.to_numeric(df['Returns'], errors='coerce').fillna(0)

            # Group by seller
            seller_stats = df.groupby('Seller').agg({
                'Revenue': 'sum',
                'Items Shipped': 'sum',
                'Returns': 'sum'
            }).reset_index()

            # Calculate metrics
            seller_stats['Return_Rate'] = (
                seller_stats['Returns'] /
                (seller_stats['Items Shipped'] + seller_stats['Returns']) * 100
            ).fillna(0)

            # Generate chart
            chart_path = self._create_seller_chart(seller_stats)

            # Convert to dict
            sellers_data = seller_stats.to_dict('records')
            for seller in sellers_data:
                seller['Revenue'] = float(seller['Revenue'])
                seller['Items Shipped'] = int(seller['Items Shipped'])
                seller['Returns'] = int(seller['Returns'])
                seller['Return_Rate'] = round(float(seller['Return_Rate']), 2)

            return {
                'sellers': sellers_data,
                'chart_path': chart_path
            }

        except Exception as e:
            logger.error(f"Error in seller analytics: {e}")
            raise

    def _create_seller_chart(self, seller_stats: pd.DataFrame) -> str:
        """Create seller performance chart."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Revenue pie chart
            ax1.pie(seller_stats['Revenue'], labels=seller_stats['Seller'],
                   autopct='%1.1f%%', startangle=90)
            ax1.set_title('Revenue by Seller Type', fontsize=14, fontweight='bold')

            # Return rate comparison
            ax2.bar(seller_stats['Seller'], seller_stats['Return_Rate'])
            ax2.set_ylabel('Return Rate (%)', fontsize=12)
            ax2.set_title('Return Rate by Seller', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)

            plt.tight_layout()

            chart_path = f"{self.images_folder}/seller_analysis.png"
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating seller chart: {e}")
            plt.close()
            raise
