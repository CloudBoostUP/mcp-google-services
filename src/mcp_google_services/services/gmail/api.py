"""Gmail API client for email operations."""

from typing import List, Optional, Dict, Any
from google.oauth2.credentials import Credentials

from ...core.client import GoogleAPIClient
from ...core.rate_limiter import RateLimiter


class GmailAPI(GoogleAPIClient):
    """Gmail API client for email backup and management."""

    # Gmail API quota costs
    LIST_QUOTA_COST = 5
    GET_QUOTA_COST = 5
    BATCH_GET_QUOTA_COST = 5

    def __init__(
        self,
        credentials: Credentials,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        """Initialize GmailAPI.

        Args:
            credentials: OAuth 2.0 credentials
            rate_limiter: Optional rate limiter. If None, creates default.
        """
        super().__init__(
            credentials=credentials,
            api_name="gmail",
            api_version="v1",
            rate_limiter=rate_limiter,
            quota_cost=self.LIST_QUOTA_COST,
        )
        self.messages_service = self.service.users().messages()
        self.labels_service = self.service.users().labels()

    def list_messages(
        self,
        user_id: str = "me",
        query: Optional[str] = None,
        max_results: int = 100,
        page_token: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """List messages matching the query.

        Args:
            user_id: User's email address or 'me' (default: 'me')
            query: Gmail search query (e.g., 'from:example@gmail.com', 'has:attachment')
            max_results: Maximum number of messages to return (default: 100, max: 500)
            page_token: Token for pagination (optional)
            label_ids: Only return messages with these label IDs (optional)

        Returns:
            Dictionary with 'messages' list and 'nextPageToken' if more results available

        Example:
            >>> api = GmailAPI(credentials)
            >>> result = api.list_messages(query='from:sender@example.com', max_results=50)
            >>> messages = result.get('messages', [])
        """
        request_params: Dict[str, Any] = {
            "userId": user_id,
            "maxResults": min(max_results, 500),  # Gmail API limit
        }
        
        if query:
            request_params["q"] = query
        if page_token:
            request_params["pageToken"] = page_token
        if label_ids:
            request_params["labelIds"] = label_ids
        
        def request_method(*args, **kwargs):
            return self.messages_service.list(*args, **kwargs)
        
        # Use list quota cost
        original_quota_cost = self.quota_cost
        self.quota_cost = self.LIST_QUOTA_COST
        
        try:
            response = self._execute_request(
                request_method,
                **request_params
            )
            return response
        finally:
            self.quota_cost = original_quota_cost

    def get_message(
        self,
        user_id: str = "me",
        message_id: str = None,
        format: str = "full",
    ) -> Dict[str, Any]:
        """Get a full message by ID.

        Args:
            user_id: User's email address or 'me' (default: 'me')
            message_id: The ID of the message to retrieve
            format: Message format. Options: 'full', 'metadata', 'minimal', 'raw' (default: 'full')

        Returns:
            Full message object with headers, body, etc.

        Raises:
            ValueError: If message_id is not provided

        Example:
            >>> api = GmailAPI(credentials)
            >>> message = api.get_message(message_id='12345')
        """
        if not message_id:
            raise ValueError("message_id is required")
        
        def request_method(*args, **kwargs):
            return self.messages_service.get(*args, **kwargs)
        
        # Use get quota cost
        original_quota_cost = self.quota_cost
        self.quota_cost = self.GET_QUOTA_COST
        
        try:
            response = self._execute_request(
                request_method,
                userId=user_id,
                id=message_id,
                format=format,
            )
            return response
        finally:
            self.quota_cost = original_quota_cost

    def batch_get_messages(
        self,
        user_id: str = "me",
        message_ids: List[str] = None,
        format: str = "full",
    ) -> List[Dict[str, Any]]:
        """Get multiple messages by IDs (batch operation).

        Args:
            user_id: User's email address or 'me' (default: 'me')
            message_ids: List of message IDs to retrieve
            format: Message format. Options: 'full', 'metadata', 'minimal', 'raw' (default: 'full')

        Returns:
            List of message objects

        Raises:
            ValueError: If message_ids is empty or None

        Example:
            >>> api = GmailAPI(credentials)
            >>> messages = api.batch_get_messages(message_ids=['12345', '67890'])
        """
        if not message_ids:
            raise ValueError("message_ids list is required and cannot be empty")
        
        # Gmail API batchGet supports up to 1000 messages
        # But we'll process in chunks to be safe
        chunk_size = 100
        all_messages = []
        
        for i in range(0, len(message_ids), chunk_size):
            chunk = message_ids[i:i + chunk_size]
            
            def request_method(*args, **kwargs):
                return self.messages_service.batchGet(*args, **kwargs)
            
            # Use batch get quota cost (counts as one request but processes multiple)
            original_quota_cost = self.quota_cost
            self.quota_cost = self.BATCH_GET_QUOTA_COST
            
            try:
                response = self._execute_request(
                    request_method,
                    userId=user_id,
                    ids=chunk,
                    format=format,
                )
                
                if "messages" in response:
                    all_messages.extend(response["messages"])
            finally:
                self.quota_cost = original_quota_cost
        
        return all_messages

    def list_labels(
        self,
        user_id: str = "me",
    ) -> List[Dict[str, Any]]:
        """List all labels for the user.

        Args:
            user_id: User's email address or 'me' (default: 'me')

        Returns:
            List of label objects

        Example:
            >>> api = GmailAPI(credentials)
            >>> labels = api.list_labels()
            >>> label_names = [label['name'] for label in labels]
        """
        def request_method(*args, **kwargs):
            return self.labels_service.list(*args, **kwargs)
        
        # Labels list is cheaper (1 unit)
        original_quota_cost = self.quota_cost
        self.quota_cost = 1
        
        try:
            response = self._execute_request(
                request_method,
                userId=user_id,
            )
            return response.get("labels", [])
        finally:
            self.quota_cost = original_quota_cost

    def get_label(
        self,
        user_id: str = "me",
        label_id: str = None,
    ) -> Dict[str, Any]:
        """Get a specific label by ID.

        Args:
            user_id: User's email address or 'me' (default: 'me')
            label_id: The ID of the label to retrieve

        Returns:
            Label object

        Raises:
            ValueError: If label_id is not provided
        """
        if not label_id:
            raise ValueError("label_id is required")
        
        def request_method(*args, **kwargs):
            return self.labels_service.get(*args, **kwargs)
        
        original_quota_cost = self.quota_cost
        self.quota_cost = 1
        
        try:
            response = self._execute_request(
                request_method,
                userId=user_id,
                id=label_id,
            )
            return response
        finally:
            self.quota_cost = original_quota_cost

