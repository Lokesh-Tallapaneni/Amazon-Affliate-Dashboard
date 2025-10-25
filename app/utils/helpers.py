"""
Helper utility functions.

This module provides helper functions for common operations like
file handling, date extraction, and data formatting.
"""

import os
import re
import logging
from datetime import datetime, timedelta
from typing import Tuple, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file extension is allowed.

    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed extensions

    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def extract_dates_from_excel(file_path: str, sheet_name: str = "Fee-Earnings") -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract start and end dates from Excel file header.

    Args:
        file_path (str): Path to Excel file
        sheet_name (str): Name of the sheet to read

    Returns:
        tuple: (start_date, end_date, one_month_ago_date) in YYYY-MM-DD format
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        header = df.columns[0]

        # Extract dates using regex
        date_pattern = r'\d{2}-\d{2}-\d{4}'
        dates = re.findall(date_pattern, header)

        if len(dates) < 2:
            logger.warning(f"Could not extract dates from header: {header}")
            return None, None, None

        # Convert dates to standard format
        formatted_dates = []
        for date_str in dates:
            date_obj = datetime.strptime(date_str, "%m-%d-%Y")
            formatted_dates.append(date_obj.strftime("%Y-%m-%d"))

        start_date = formatted_dates[0]
        end_date = formatted_dates[1]

        # Calculate one month ago from end date
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        one_month_ago = end_date_obj - timedelta(days=30)
        one_month_ago_str = one_month_ago.strftime("%Y-%m-%d")

        return start_date, end_date, one_month_ago_str

    except Exception as e:
        logger.error(f"Error extracting dates from Excel: {str(e)}")
        return None, None, None


def format_date(date_obj, format_str: str = "%Y-%m-%d") -> str:
    """
    Format date object to string.

    Args:
        date_obj: Date object (datetime or date)
        format_str (str): Output format string

    Returns:
        str: Formatted date string
    """
    if isinstance(date_obj, str):
        return date_obj

    try:
        return date_obj.strftime(format_str)
    except Exception as e:
        logger.error(f"Error formatting date: {str(e)}")
        return str(date_obj)


def cleanup_files(file_paths: List[str]) -> None:
    """
    Remove files from filesystem.

    Args:
        file_paths (list): List of file paths to remove
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not remove file {file_path}: {str(e)}")


def get_summary_data(file_path: str, sheet_name: str = "Fee-Tracking") -> pd.DataFrame:
    """
    Extract summary data from Excel file.

    Args:
        file_path (str): Path to Excel file
        sheet_name (str): Name of the sheet to read

    Returns:
        pd.DataFrame: Summary dataframe
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.columns = df.iloc[0]
        df = df[1:]
        return df
    except Exception as e:
        logger.error(f"Error reading summary data: {str(e)}")
        return pd.DataFrame()


def safe_file_save(file, directory: str, filename: str) -> Optional[str]:
    """
    Safely save uploaded file.

    Args:
        file: File object from request
        directory (str): Directory to save file
        filename (str): Desired filename

    Returns:
        str: Path to saved file, or None if failed
    """
    try:
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, filename)
        file.save(file_path)
        logger.info(f"File saved successfully: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return None
