"""Rate limiting for Google API requests."""

import time
from typing import Optional
from collections import deque
from threading import Lock


class RateLimiter:
    """Rate limiter for Google API quota management.

    Google APIs have quotas:
    - Gmail API: 1,000,000,000 units/day
    - Per user: 250 units/second
    - messages.list: 5 units per call
    - messages.get: 5 units per call
    """

    def __init__(
        self,
        quota_per_second: int = 250,
        burst_size: Optional[int] = None,
    ):
        """Initialize RateLimiter.

        Args:
            quota_per_second: Maximum quota units per second (default: 250 for Gmail)
            burst_size: Optional burst allowance. If None, defaults to quota_per_second
        """
        self.quota_per_second = quota_per_second
        self.burst_size = burst_size or quota_per_second
        self.current_quota = self.burst_size
        self.last_reset = time.time()
        
        # Track request timestamps for smoothing
        self.request_times: deque = deque()
        self.lock = Lock()

    def wait_if_needed(self, quota_cost: int = 1) -> None:
        """Wait if necessary to stay within rate limits.

        Args:
            quota_cost: Quota units required for this request (default: 1)
        """
        with self.lock:
            now = time.time()
            
            # Reset quota if enough time has passed
            elapsed = now - self.last_reset
            if elapsed >= 1.0:
                self.current_quota = min(
                    self.burst_size,
                    self.current_quota + int(elapsed * self.quota_per_second)
                )
                self.last_reset = now
                
                # Clean old request times (older than 1 second)
                while self.request_times and self.request_times[0] < now - 1.0:
                    self.request_times.popleft()
            
            # Check if we have enough quota
            if self.current_quota < quota_cost:
                # Calculate wait time
                needed = quota_cost - self.current_quota
                wait_seconds = needed / self.quota_per_second
                
                # Add small buffer
                wait_seconds += 0.1
                
                time.sleep(wait_seconds)
                
                # Update quota after waiting
                self.current_quota = self.burst_size
            
            # Deduct quota
            self.current_quota -= quota_cost
            self.request_times.append(now)

    def reset_quota(self) -> None:
        """Reset quota to maximum (for testing or manual reset)."""
        with self.lock:
            self.current_quota = self.burst_size
            self.last_reset = time.time()
            self.request_times.clear()

    def get_current_quota(self) -> int:
        """Get current available quota.

        Returns:
            Available quota units
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_reset
            
            if elapsed >= 1.0:
                self.current_quota = min(
                    self.burst_size,
                    self.current_quota + int(elapsed * self.quota_per_second)
                )
                self.last_reset = now
            
            return self.current_quota

