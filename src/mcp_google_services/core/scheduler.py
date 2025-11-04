"""Scheduler for automated backup operations."""

from typing import Optional
from datetime import datetime
import croniter
from ..utils.config import Config


class Scheduler:
    """Simple scheduler for backup operations."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize Scheduler.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.enabled = self.config.get("schedule.enabled", False)

    def is_time_to_run(self, cron_expression: str, last_run: Optional[datetime] = None) -> bool:
        """Check if it's time to run based on cron expression.

        Args:
            cron_expression: Cron expression (e.g., "0 2 * * *" for daily at 2 AM)
            last_run: Last run datetime (optional)

        Returns:
            True if it's time to run, False otherwise
        """
        if not self.enabled:
            return False
        
        if last_run is None:
            # If never run, check if current time matches
            cron = croniter.croniter(cron_expression, datetime.now())
            next_run = cron.get_prev(datetime)
            # Run if next run was very recent (within last minute)
            return (datetime.now() - next_run).total_seconds() < 60
        
        cron = croniter.croniter(cron_expression, last_run)
        next_run = cron.get_next(datetime)
        
        return datetime.now() >= next_run

    def get_next_run_time(self, cron_expression: str, last_run: Optional[datetime] = None) -> datetime:
        """Get next scheduled run time.

        Args:
            cron_expression: Cron expression
            last_run: Last run datetime (optional)

        Returns:
            Next scheduled run datetime
        """
        if last_run is None:
            last_run = datetime.now()
        
        cron = croniter.croniter(cron_expression, last_run)
        return cron.get_next(datetime)

