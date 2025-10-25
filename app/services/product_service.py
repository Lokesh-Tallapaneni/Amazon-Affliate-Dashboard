"""
Product fetching service.

This module handles fetching products from Amazon API in background.
"""

import logging
import time
from typing import List

import pandas as pd

from .amazon_api import AmazonAPIService

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product fetching operations."""

    # Default keywords for product search
    DEFAULT_KEYWORDS = [
        "deals", "electronics", "mobiles", "today deals", "offers",
        # "kitchen ware", "sports", "shirts", "men shirts", "appliances",
        # "pants", "shoes", "toys", "laptops", "bags", "wallets",
        # "hand bags", "saree", "televisions", "ear buds",
        # "mobile accessories", "watches", "grocery", "household supplies"
    ]

    def __init__(self, config):
        """
        Initialize ProductService.

        Args:
            config: Application configuration object
        """
        self.config = config

    def fetch_products(
        self,
        api_key: str,
        secret_key: str,
        associate_tag: str,
        keywords: List[str] = None
    ) -> bool:
        """
        Fetch products from Amazon API for given keywords.

        This function is designed to run in a background process.

        Args:
            api_key (str): Amazon API key
            secret_key (str): Amazon secret key
            associate_tag (str): Amazon associate tag
            keywords (list): List of keywords to search (uses defaults if None)

        Returns:
            bool: True if successful
        """
        try:
            if keywords is None:
                keywords = self.DEFAULT_KEYWORDS

            # Initialize Amazon API service
            # Handle both Flask config dict and config class
            country = self.config.get('AMAZON_COUNTRY') if hasattr(self.config, 'get') else self.config.AMAZON_COUNTRY
            amazon_service = AmazonAPIService(
                api_key,
                secret_key,
                associate_tag,
                country=country
            )

            product_data_list = []

            # Search for each keyword
            for keyword in keywords:
                logger.info(f"Searching products for keyword: {keyword}")
                products = amazon_service.search_products(keyword)
                product_data_list.extend(products)

                # Throttle to respect API limits
                time.sleep(2)

            # Save to Excel
            df = pd.DataFrame(product_data_list)

            # Handle both Flask config dict and config class
            product_file = self.config.get('PRODUCT_DETAILS_FILE') if hasattr(self.config, 'get') else self.config.PRODUCT_DETAILS_FILE
            with pd.ExcelWriter(
                product_file,
                engine='xlsxwriter'
            ) as writer:
                df.to_excel(writer, sheet_name='Product_details', index=False)

            logger.info(f"Successfully fetched {len(product_data_list)} products")
            return True

        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            return False


def run_product_fetch(api_key: str, secret_key: str, associate_tag: str, config) -> None:
    """
    Function to run in multiprocessing.Process.

    Args:
        api_key (str): Amazon API key
        secret_key (str): Amazon secret key
        associate_tag (str): Amazon associate tag
        config: Application configuration
    """
    service = ProductService(config)
    service.fetch_products(api_key, secret_key, associate_tag)
