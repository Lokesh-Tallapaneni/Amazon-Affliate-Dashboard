"""
Amazon API service.

This module handles interactions with Amazon Product Advertising API.
"""

import logging
from typing import Optional

from amazon_paapi import AmazonApi
from amazon_paapi.errors.exceptions import RequestError

logger = logging.getLogger(__name__)


class AmazonAPIService:
    """Service class for Amazon API operations."""

    def __init__(self, api_key: str, secret_key: str, associate_tag: str, country: str = 'IN'):
        """
        Initialize Amazon API service.

        Args:
            api_key (str): Amazon API key
            secret_key (str): Amazon secret key
            associate_tag (str): Amazon associate tag
            country (str): Country code (default: IN)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.country = country
        self._api = None

    def get_api_client(self) -> AmazonApi:
        """
        Get or create Amazon API client.

        Returns:
            AmazonApi: Amazon API client instance
        """
        if self._api is None:
            self._api = AmazonApi(
                self.api_key,
                self.secret_key,
                self.associate_tag,
                country=self.country,
                throttling=1
            )
        return self._api

    def verify_credentials(self) -> bool:
        """
        Verify Amazon API credentials by making a test request.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            api = self.get_api_client()
            # Test with a known ASIN
            items = api.get_items(["B07L6YYK6B"])

            # Check if we got a valid response
            for item in items:
                title = str(item.item_info.title.display_value)
                if title:
                    logger.info("Amazon API credentials verified successfully")
                    return True

            logger.warning("Amazon API test request returned no valid items")
            return False

        except RequestError as e:
            logger.error(f"Amazon API credentials verification failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying Amazon API credentials: {str(e)}")
            return False

    def search_products(self, keyword: str) -> list:
        """
        Search for products by keyword.

        Args:
            keyword (str): Search keyword

        Returns:
            list: List of product dictionaries
        """
        try:
            api = self.get_api_client()
            search_result = api.search_items(keywords=keyword)
            products = search_result._items

            product_list = []

            for item in products:
                product_data = self._extract_product_data(item)
                if product_data:
                    product_list.append(product_data)

            logger.info(f"Found {len(product_list)} products for keyword: {keyword}")
            return product_list

        except Exception as e:
            logger.error(f"Error searching products for keyword '{keyword}': {str(e)}")
            return []

    def _extract_product_data(self, item) -> Optional[dict]:
        """
        Extract product data from API item.

        Args:
            item: Amazon API item object

        Returns:
            dict: Product data dictionary
        """
        try:
            # Extract title
            try:
                title = str(item.item_info.title.display_value)
            except Exception:
                title = None

            # Extract current price
            try:
                current_price = int(float(item.offers.listings[0].price.amount))
            except Exception:
                current_price = None

            # Extract original price
            try:
                original_price = int(float(item.offers.listings[0].saving_basis.amount))
            except Exception:
                original_price = None

            # Extract primary image
            try:
                primary_image = str(item.images.primary.large.url)
            except Exception:
                primary_image = None

            # Extract product link
            try:
                product_link = item.detail_page_url
            except Exception:
                product_link = None

            return {
                'Product_Name': title,
                'Primary_Image': primary_image,
                'Original_Price': original_price,
                'Current_Price': current_price,
                'Product_Link': product_link
            }

        except Exception as e:
            logger.warning(f"Error extracting product data: {str(e)}")
            return None
