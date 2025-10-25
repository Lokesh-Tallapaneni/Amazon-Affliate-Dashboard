"""
JWT authentication service.

This module handles JWT token generation, validation, and blacklisting
for secure user authentication.
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class JWTService:
    """Service class for JWT operations."""

    # In-memory token blacklist (for logout functionality)
    # In production, use Redis or database
    _blacklist = set()

    def __init__(self, config):
        """
        Initialize JWT service.

        Args:
            config: Application configuration object (dict or class)
        """
        self.config = config
        # Handle both dict and object config
        self.secret_key = self._get_config_value('JWT_SECRET_KEY')
        self.algorithm = self._get_config_value('JWT_ALGORITHM')
        self.access_token_expires = self._get_config_value('JWT_ACCESS_TOKEN_EXPIRES')
        self.refresh_token_expires = self._get_config_value('JWT_REFRESH_TOKEN_EXPIRES')

    def _get_config_value(self, key):
        """
        Get configuration value supporting both dict and object access.

        Args:
            key: Configuration key

        Returns:
            Configuration value
        """
        # Try dict-style access first (Flask app.config)
        if hasattr(self.config, 'get'):
            return self.config.get(key)
        # Fall back to attribute access (Config class)
        return getattr(self.config, key)

    def generate_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate access and refresh tokens for a user.

        Args:
            user_data: Dictionary containing user information
                       (api_key, secret_key, associate_tag, etc.)

        Returns:
            Dictionary with 'access_token' and 'refresh_token'
        """
        try:
            # Create access token payload
            access_payload = {
                'type': 'access',
                'user_id': user_data.get('api_key', '')[:10],  # Use first 10 chars as user ID
                'api_key': user_data.get('api_key', ''),
                'secret_key': user_data.get('secret_key', ''),
                'associate_tag': user_data.get('associate_tag', ''),
                'product_fetch_pid': user_data.get('product_fetch_pid'),
                'exp': datetime.utcnow() + self.access_token_expires,
                'iat': datetime.utcnow()
            }

            # Create refresh token payload
            refresh_payload = {
                'type': 'refresh',
                'user_id': user_data.get('api_key', '')[:10],
                'exp': datetime.utcnow() + self.refresh_token_expires,
                'iat': datetime.utcnow()
            }

            # Generate tokens
            access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)

            logger.info(f"Generated tokens for user: {access_payload['user_id']}")

            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        except Exception as e:
            logger.error(f"Error generating tokens: {str(e)}")
            raise

    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string
            token_type: Type of token ('access' or 'refresh')

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            # Check if token is blacklisted
            if token in self._blacklist:
                logger.warning("Attempted to use blacklisted token")
                return None

            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Verify token type
            if payload.get('type') != token_type:
                logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
                return None

            # Check expiration
            if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
                logger.warning("Token has expired")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a new access token using a refresh token.

        Args:
            refresh_token: Valid refresh token
            user_data: User data to include in new access token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token, token_type='refresh')
            if not payload:
                return None

            # Generate new access token
            tokens = self.generate_tokens(user_data)
            return tokens['access_token']

        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            return None

    def blacklist_token(self, token: str) -> bool:
        """
        Add a token to the blacklist (for logout).

        Args:
            token: JWT token to blacklist

        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify token is valid before blacklisting
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration when blacklisting
            )

            # Add to blacklist
            self._blacklist.add(token)
            logger.info(f"Token blacklisted for user: {payload.get('user_id')}")
            return True

        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return False

    @classmethod
    def clear_blacklist(cls):
        """
        Clear the token blacklist.

        This should be called periodically to remove expired tokens.
        """
        cls._blacklist.clear()
        logger.info("Token blacklist cleared")

    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user data from token payload.

        Args:
            payload: Decoded JWT payload

        Returns:
            Dictionary with user data
        """
        return {
            'api_key': payload.get('api_key', ''),
            'secret_key': payload.get('secret_key', ''),
            'associate_tag': payload.get('associate_tag', ''),
            'product_fetch_pid': payload.get('product_fetch_pid'),
            'user_id': payload.get('user_id', '')
        }
