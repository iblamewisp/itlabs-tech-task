from datetime import datetime, timedelta, timezone
from typing import Optional
import re


class DeadlineParser:
    """Parse deadline from user text input"""

    @staticmethod
    def _get_now() -> datetime:
        """Get current time as timezone-aware datetime (UTC)"""
        return datetime.now(timezone.utc)

    @staticmethod
    def parse(text: str) -> Optional[datetime]:
        """
        Parse deadline from text - supports EN/RU natural language

        Examples: "tomorrow", "in 2 days", "18:00", "20.02 18:00"
        """
        text = text.strip().lower()
        now = DeadlineParser._get_now()

        # tomorrow
        if text in ['завтра', 'tomorrow']:
            return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)

        # day after tomorrow
        if text in ['послезавтра', 'day after tomorrow']:
            return (now + timedelta(days=2)).replace(hour=12, minute=0, second=0, microsecond=0)

        # "in X days" pattern
        match = re.match(r'(?:через|in)\s+(\d+)\s+(?:день|дня|дней|day|days)', text)
        if match:
            days = int(match.group(1))
            return (now + timedelta(days=days)).replace(hour=12, minute=0, second=0, microsecond=0)

        # "in X hours" pattern
        match = re.match(r'(?:через|in)\s+(\d+)\s+(?:час|часа|часов|hour|hours)', text)
        if match:
            hours = int(match.group(1))
            return now + timedelta(hours=hours)

        # Pattern: "DD.MM.YYYY HH:MM" or "DD.MM HH:MM"
        match = re.match(r'(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?\s+(\d{1,2}):(\d{2})', text)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3)) if match.group(3) else now.year
            hour = int(match.group(4))
            minute = int(match.group(5))

            try:
                # Create timezone-aware datetime in UTC
                return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
            except ValueError:
                return None

        # Pattern: "HH:MM" (today)
        match = re.match(r'(\d{1,2}):(\d{2})', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))

            try:
                deadline = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                # If time already passed today, use tomorrow
                if deadline < now:
                    deadline += timedelta(days=1)
                return deadline
            except ValueError:
                return None

        return None

    @staticmethod
    def format_deadline(deadline: datetime) -> str:
        """
        Format deadline for display

        Args:
            deadline: Deadline datetime (can be timezone-aware or naive)

        Returns:
            str: Formatted deadline string
        """
        now = DeadlineParser._get_now()

        # Ensure deadline is timezone-aware for comparison
        if deadline.tzinfo is None:
            # If naive, assume UTC
            deadline = deadline.replace(tzinfo=timezone.utc)

        delta = deadline - now

        # If within 24 hours, show relative time
        if 0 < delta.total_seconds() < 24 * 3600:
            hours = int(delta.total_seconds() / 3600)
            if hours == 0:
                minutes = int(delta.total_seconds() / 60)
                return f"in {minutes} minutes"
            return f"in {hours} hours"

        # If within 7 days, show day name
        if 0 < delta.days < 7:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = day_names[deadline.weekday()]
            return f"{day_name} at {deadline.strftime('%H:%M')}"

        # Otherwise show full date
        return deadline.strftime('%d.%m.%Y %H:%M')
