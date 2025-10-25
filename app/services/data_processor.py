"""
Data processing service.

This module handles all data processing operations including Excel parsing,
visualization generation, and data transformation.
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configure pandas to handle future behavior
pd.set_option('future.no_silent_downcasting', True)

logger = logging.getLogger(__name__)


class DataProcessor:
    """Service class for data processing operations."""

    def __init__(self, config):
        """
        Initialize DataProcessor.

        Args:
            config: Application configuration object
        """
        self.config = config
        # Handle both Flask config dict and config class
        self.images_folder = config.get('IMAGES_FOLDER') if hasattr(config, 'get') else config.IMAGES_FOLDER

    def parse_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        Parse Excel file and return all sheets as dataframes.

        Args:
            file_path (str): Path to Excel file

        Returns:
            dict: Dictionary of sheet_name -> dataframe
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = {}

            for sheet_name in excel_file.sheet_names:
                sheet = excel_file.parse(sheet_name)
                # Set first row as column headers
                sheet.columns = sheet.iloc[0]
                sheet = sheet[1:].reset_index(drop=True)
                # Normalize sheet name (replace hyphens with underscores)
                normalized_name = sheet_name.replace("-", "_")
                sheets[normalized_name] = sheet

            logger.info(f"Successfully parsed {len(sheets)} sheets from {file_path}")
            return sheets

        except Exception as e:
            logger.error(f"Error parsing Excel file {file_path}: {str(e)}")
            raise

    def process_data(self, file_path: str, from_date: str, to_date: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Process data and generate all visualizations.

        Args:
            file_path (str): Path to Excel file
            from_date (str): Start date (YYYY-MM-DD)
            to_date (str): End date (YYYY-MM-DD)

        Returns:
            tuple: (max_fee_products, max_quantity_products)
        """
        try:
            # Parse Excel file
            sheets = self.parse_excel_file(file_path)

            fee_earnings = sheets.get('Fee_Earnings')
            fee_daily_trends = sheets.get('Fee_DailyTrends')
            fee_orders = sheets.get('Fee_Orders')

            if fee_earnings is None or fee_daily_trends is None:
                raise ValueError("Required sheets not found in Excel file")

            # Save earnings to CSV for chat agent
            # Handle both Flask config dict and config class
            data_csv = self.config.get('DATA_CSV') if hasattr(self.config, 'get') else self.config.DATA_CSV
            fee_earnings.to_csv(data_csv, index=False)

            # Prepare merged data for main dashboard
            merged_data = self._prepare_merged_data(fee_earnings, fee_daily_trends)

            # Generate all visualizations
            self.generate_main_dashboard(merged_data, from_date, to_date)
            self.generate_pie_chart(fee_earnings, from_date, to_date)
            self.generate_bar_chart(fee_earnings, from_date, to_date)
            self.generate_returns_chart(fee_earnings, from_date, to_date)

            # Get top products
            max_fee = self._get_max_adfee_products(fee_earnings, from_date, to_date)
            max_quantity = self._get_max_quantity_products(fee_orders, from_date, to_date)

            logger.info("Data processing completed successfully")
            return max_fee, max_quantity

        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise

    def _prepare_merged_data(self, fee_earnings: pd.DataFrame, fee_daily_trends: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare merged data for dashboard visualization.

        Args:
            fee_earnings (pd.DataFrame): Fee earnings data
            fee_daily_trends (pd.DataFrame): Daily trends data

        Returns:
            pd.DataFrame: Merged dataframe
        """
        # Process Fee Earnings
        fee_earnings = fee_earnings[pd.to_datetime(
            fee_earnings['Date Shipped'],
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce'
        ).notna()].copy()
        fee_earnings['Date Shipped'] = pd.to_datetime(fee_earnings['Date Shipped']).dt.date

        # Process Daily Trends
        fee_daily_trends = fee_daily_trends[pd.to_datetime(
            fee_daily_trends['Date'],
            format='%Y-%m-%d',
            errors='coerce'
        ).notna()].copy()
        fee_daily_trends['Date'] = pd.to_datetime(fee_daily_trends['Date']).dt.date

        # Group data
        grouped_fees = fee_earnings.groupby('Date Shipped')['Ad Fees'].sum().reset_index()
        grouped_clicks = fee_daily_trends.groupby('Date')['Clicks'].sum().reset_index()
        grouped_orders = fee_daily_trends.groupby('Date')['Total Items Ordered'].sum().reset_index()

        # Create date range
        min_date = min(grouped_fees['Date Shipped'].min(), grouped_clicks['Date'].min())
        max_date = max(grouped_fees['Date Shipped'].max(), grouped_clicks['Date'].max())
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        date_list_df = pd.DataFrame({'Date Shipped': date_range.date})

        # Merge all data
        merged = pd.merge(date_list_df, grouped_fees, on='Date Shipped', how='left').fillna({'Ad Fees': 0}).infer_objects(copy=False)
        merged = pd.merge(merged, grouped_clicks, left_on='Date Shipped', right_on='Date', how='left').fillna({'Clicks': 0}).infer_objects(copy=False)
        merged = merged.drop(columns=['Date'], errors='ignore')
        merged = pd.merge(merged, grouped_orders, left_on='Date Shipped', right_on='Date', how='left').fillna({'Total Items Ordered': 0}).infer_objects(copy=False)
        merged = merged.drop(columns=['Date'], errors='ignore')

        # Convert Date Shipped to datetime for filtering
        merged['Date Shipped'] = pd.to_datetime(merged['Date Shipped'])

        return merged

    def generate_main_dashboard(self, merged_data: pd.DataFrame, from_date: str, to_date: str) -> bool:
        """
        Generate main dashboard chart (bar + line combo).

        Args:
            merged_data (pd.DataFrame): Merged data
            from_date (str): Start date
            to_date (str): End date

        Returns:
            bool: True if successful
        """
        try:
            from_date = pd.to_datetime(from_date)
            to_date = pd.to_datetime(to_date)

            filtered_data = merged_data[
                (merged_data['Date Shipped'] >= from_date) &
                (merged_data['Date Shipped'] <= to_date)
            ].copy()

            fig, ax1 = plt.subplots(figsize=(18, 9))

            # Format dates for x-axis
            formatted_dates = filtered_data['Date Shipped'].dt.strftime('%b %d')
            formatted_dates = pd.to_datetime(formatted_dates, format='%b %d')

            # Bar chart for Ad Fees
            bars = ax1.bar(filtered_data.index, filtered_data['Ad Fees'], color='#58e2c2', label='Ad Fees')
            ax1.set_xticks(filtered_data.index)
            ax1.set_xticklabels(formatted_dates, rotation=90, ha='right')
            ax1.set_title('Ad Fees vs. Date Shipped')
            ax1.set_xlabel('Date Shipped')
            ax1.set_ylabel('Ad Fees')

            # Annotate bars
            for bar, ad_fee in zip(bars, filtered_data['Ad Fees']):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2, height, f'{ad_fee:.2f}₹',
                        ha='center', va='bottom', color='black')

            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

            # Line for Clicks
            ax2 = ax1.twinx()
            ax2.plot(filtered_data.index, filtered_data['Clicks'], color='#d05254',
                    marker='o', linestyle='-', label='Clicks')
            ax2.set_ylabel('Clicks', color='#d05254')
            ax2.tick_params(axis='y', labelcolor='#d05254')

            # Annotate clicks
            for x, y in zip(filtered_data.index, filtered_data['Clicks']):
                ax2.text(x, y + 0.1, f'{y}', ha='left', va='bottom', color='#d05254')

            # Line for Orders
            ax3 = ax1.twinx()
            ax3.plot(filtered_data.index, filtered_data['Total Items Ordered'],
                    color='#f0b83a', marker='o', linestyle='-', label='Orders')
            ax3.set_ylabel('Orders', color='#f0b83a')
            ax3.tick_params(axis='y', labelcolor='#f0b83a')

            # Annotate orders
            for x, y in zip(filtered_data.index, filtered_data['Total Items Ordered']):
                ax3.text(x, y + 0.1, f'{y}', ha='left', va='bottom', color='#f0b83a')

            # Combined legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            lines3, labels3 = ax3.get_legend_handles_labels()
            ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper right')

            plt.tight_layout()
            plt.savefig(f"{self.images_folder}/dash.png", bbox_inches="tight")
            plt.close()

            logger.info("Main dashboard chart generated")
            return True

        except Exception as e:
            logger.error(f"Error generating main dashboard: {str(e)}")
            return False

    def generate_pie_chart(self, data: pd.DataFrame, from_date: str, to_date: str) -> bool:
        """
        Generate pie chart for category distribution.

        Args:
            data (pd.DataFrame): Fee earnings data
            from_date (str): Start date
            to_date (str): End date

        Returns:
            bool: True if successful
        """
        try:
            from_date = pd.to_datetime(from_date)
            to_date = pd.to_datetime(to_date)

            data = data.copy()
            data['Date Shipped'] = pd.to_datetime(data['Date Shipped'])
            data = data[(data['Date Shipped'] >= from_date) & (data['Date Shipped'] <= to_date)]

            # Count categories
            category_counts = {}
            for category in data['Category']:
                short_cat = str(category).split()[0]
                category_counts[short_cat] = category_counts.get(short_cat, 0) + 1

            categories = list(category_counts.keys())
            values = list(category_counts.values())

            # Create pie chart
            fig = plt.figure(figsize=(10, 10), dpi=125)
            gs = fig.add_gridspec(1, 1, left=0, bottom=0, right=0.884, top=0.994)
            ax = fig.add_subplot(gs[0, 0])

            ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=190,
                  labeldistance=1.05, textprops={"fontsize": 7})
            ax.legend(categories, title='Categories', loc='center left', bbox_to_anchor=(1, 0.6))
            ax.axis('equal')

            plt.savefig(f"{self.images_folder}/piepic.png", bbox_inches="tight")
            plt.close()

            logger.info("Pie chart generated")
            return True

        except Exception as e:
            logger.error(f"Error generating pie chart: {str(e)}")
            return False

    def generate_bar_chart(self, data: pd.DataFrame, from_date: str, to_date: str) -> bool:
        """
        Generate bar chart for category items.

        Args:
            data (pd.DataFrame): Fee earnings data
            from_date (str): Start date
            to_date (str): End date

        Returns:
            bool: True if successful
        """
        try:
            from_date = pd.to_datetime(from_date)
            to_date = pd.to_datetime(to_date)

            data = data.copy()
            data['Date Shipped'] = pd.to_datetime(data['Date Shipped'])
            data = data[(data['Date Shipped'] >= from_date) & (data['Date Shipped'] <= to_date)]

            # Count categories
            category_counts = {}
            for category in data['Category']:
                short_cat = str(category).split()[0]
                category_counts[short_cat] = category_counts.get(short_cat, 0) + 1

            df = pd.DataFrame({
                'Category': list(category_counts.keys()),
                'values': list(category_counts.values())
            })

            colors = plt.cm.viridis(np.linspace(0, 1, len(df)))

            plt.figure(figsize=(18, 9))
            bars = plt.bar(df['Category'], df['values'], color=colors)
            plt.xlabel('Category')
            plt.ylabel('No. of Items')
            plt.title('Category vs. No. of Items')
            plt.xticks(rotation=45, ha='right')

            # Add values on bars
            for bar, value in zip(bars, df['values']):
                plt.text(bar.get_x() + bar.get_width() / 2 - 0.15,
                        bar.get_height() + 0.2, value, fontsize=10)

            plt.tight_layout()
            plt.savefig(f"{self.images_folder}/barpic.png", bbox_inches="tight")
            plt.close()

            logger.info("Bar chart generated")
            return True

        except Exception as e:
            logger.error(f"Error generating bar chart: {str(e)}")
            return False

    def generate_returns_chart(self, data: pd.DataFrame, from_date: str, to_date: str) -> bool:
        """
        Generate returns chart by category.

        Args:
            data (pd.DataFrame): Fee earnings data
            from_date (str): Start date
            to_date (str): End date

        Returns:
            bool: True if successful
        """
        try:
            from_date = pd.to_datetime(from_date)
            to_date = pd.to_datetime(to_date)

            data = data.copy()
            data['Date Shipped'] = pd.to_datetime(data['Date Shipped'])
            data = data[(data['Date Shipped'] >= from_date) & (data['Date Shipped'] <= to_date)]
            data['Returns'] = data['Returns'].astype(int)

            returns_by_category = data.groupby('Category')['Returns'].sum()
            short_names = returns_by_category.index.str.split().str[0]

            plt.figure(figsize=(18, 9))
            bars = plt.bar(short_names, returns_by_category, color="red")
            plt.xlabel('Category')
            plt.ylabel('Number of Returns')
            plt.title('Number of Returned Products by Category')
            plt.xticks(rotation=45, ha='right')

            # Add count labels
            for bar, count in zip(bars, returns_by_category):
                plt.text(bar.get_x() + bar.get_width() / 2 - 0.15,
                        bar.get_height() + 0.05, count, fontsize=10)

            plt.legend(['Returns'], loc='upper right')
            plt.tight_layout()
            plt.savefig(f"{self.images_folder}/returns.png", bbox_inches="tight")
            plt.close()

            logger.info("Returns chart generated")
            return True

        except Exception as e:
            logger.error(f"Error generating returns chart: {str(e)}")
            return False

    def _get_max_adfee_products(self, data: pd.DataFrame, from_date: str, to_date: str) -> pd.DataFrame:
        """
        Get top 10 products by ad fees with positive revenue.

        Args:
            data (pd.DataFrame): Fee earnings data
            from_date (str): Start date
            to_date (str): End date

        Returns:
            pd.DataFrame: Top products
        """
        from_date = pd.to_datetime(from_date)
        to_date = pd.to_datetime(to_date)

        data = data.copy()
        data['Date Shipped'] = pd.to_datetime(data['Date Shipped'])
        data = data[(data['Date Shipped'] >= from_date) & (data['Date Shipped'] <= to_date)]

        selected_rows = pd.DataFrame()

        while len(selected_rows) < 10 and not data.empty:
            max_row = data[data['Ad Fees'] == data['Ad Fees'].max()]

            if max_row.empty:
                break

            if max_row['Revenue'].values[0] >= 0:
                selected_rows = pd.concat([selected_rows, max_row])
                data = data[data['ASIN'] != max_row['ASIN'].values[0]]
            else:
                break

        return selected_rows.iloc[:10]

    def _get_max_quantity_products(self, data: pd.DataFrame, from_date: str, to_date: str) -> pd.DataFrame:
        """
        Get products with maximum quantity.

        Args:
            data (pd.DataFrame): Fee orders data
            from_date (str): Start date
            to_date (str): End date

        Returns:
            pd.DataFrame: Max quantity products
        """
        from_date = pd.to_datetime(from_date)
        to_date = pd.to_datetime(to_date)

        data = data.copy()
        data = data[pd.to_datetime(data['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna()]
        data['Date'] = pd.to_datetime(data['Date'])
        data = data[(data['Date'] >= from_date) & (data['Date'] <= to_date)]

        max_quantity = data[data['Qty'] == data['Qty'].max()]
        return max_quantity
