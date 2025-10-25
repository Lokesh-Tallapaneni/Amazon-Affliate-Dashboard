"""
Input validation utilities.

This module provides validation functions for file uploads, dates,
and other user inputs to ensure data integrity and security.
"""

import os
from datetime import datetime
from typing import Optional


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension.

    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed extensions

    Returns:
        bool: True if extension is allowed, False otherwise
    """
    if not filename:
        return False

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_date_format(date_string: str, date_format: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    Validate and parse date string.

    Args:
        date_string (str): Date string to validate
        date_format (str): Expected date format

    Returns:
        datetime: Parsed datetime object if valid, None otherwise
    """
    try:
        return datetime.strptime(date_string, date_format)
    except (ValueError, TypeError):
        return None


def validate_api_credentials(api_key: str, secret_key: str, associate_tag: str) -> bool:
    """
    Validate Amazon API credentials format.

    Args:
        api_key (str): Amazon API key
        secret_key (str): Amazon secret key
        associate_tag (str): Amazon associate tag

    Returns:
        bool: True if all credentials are present, False otherwise
    """
    return all([api_key, secret_key, associate_tag]) and \
           all([len(str(cred).strip()) > 0 for cred in [api_key, secret_key, associate_tag]])


def validate_file_path(file_path: str) -> bool:
    """
    Validate that file path exists and is readable.

    Args:
        file_path (str): Path to file

    Returns:
        bool: True if file exists and is readable, False otherwise
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)
