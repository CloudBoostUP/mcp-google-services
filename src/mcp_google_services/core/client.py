"""Base Google API client with rate limiting and error handling."""

from typing import Any, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .rate_limiter import RateLimiter


class GoogleAPIClient:
    """Base class for Google API clients with rate limiting."""

    def __init__(
        self,
        credentials: Credentials,
        api_name: str,
        api_version: str,
        rate_limiter: Optional[RateLimiter] = None,
        quota_cost: int = 1,
    ):
        """Initialize GoogleAPIClient.

        Args:
            credentials: OAuth 2.0 credentials
            api_name: Name of the Google API (e.g., 'gmail', 'drive')
            api_version: API version (e.g., 'v1')
            rate_limiter: Optional rate limiter. If None, creates default.
            quota_cost: Quota cost per request (default: 1)
        """
        self.credentials = credentials
        self.api_name = api_name
        self.api_version = api_version
        self.quota_cost = quota_cost
        self.rate_limiter = rate_limiter or RateLimiter()
        
        self.service = build(api_name, api_version, credentials=credentials)

    def _execute_request(
        self,
        request_method,
        *args,
        **kwargs
    ) -> Any:
        """Execute API request with rate limiting and error handling.

        Args:
            request_method: API request method to execute
            *args: Positional arguments for request
            **kwargs: Keyword arguments for request

        Returns:
            API response

        Raises:
            HttpError: If API request fails
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed(self.quota_cost)
        
        try:
            request = request_method(*args, **kwargs)
            return request.execute()
        except HttpError as error:
            # Handle specific error cases
            if error.resp.status == 429:
                # Rate limit exceeded - wait and retry
                self.rate_limiter.wait_if_needed(self.quota_cost * 2)
                request = request_method(*args, **kwargs)
                return request.execute()
            elif error.resp.status == 401:
                # Unauthorized - credentials may need refresh
                raise HttpError(
                    error.resp,
                    error.content,
                    "Authentication failed. Please re-authenticate."
                )
            else:
                raise

    def get_service(self):
        """Get the underlying API service object.

        Returns:
            Google API service object
        """
        return self.service

