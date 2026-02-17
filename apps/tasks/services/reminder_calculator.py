from datetime import datetime, timedelta
from typing import Optional, Tuple


class ReminderCalculator:
    """Calculate smart reminder times based on deadline (pure logic, no Django)"""
    
    # Reminder intervals for each level
    INTERVALS = {
        'daily': timedelta(hours=24),        # 5+ days left
        'half_day': timedelta(hours=12),     # 2-5 days left
        'quarter_day': timedelta(hours=6),   # 1-2 days left
        'urgent': timedelta(hours=2),        # < 1 day left
        'final': timedelta(hours=2),         # < 2 hours left
    }
    
    @staticmethod
    def calculate_reminder_level(deadline: datetime, now: Optional[datetime] = None) -> str:
        """
        Determine reminder level based on time until deadline
        
        Args:
            deadline: Task deadline
            now: Current time (defaults to timezone.now())
            
        Returns:
            str: Reminder level ('daily', 'half_day', 'quarter_day', 'urgent', 'final', 'overdue')
        """
        if now is None:
            from django.utils import timezone
            now = timezone.now()
        
        time_left = deadline - now
        
        if time_left.total_seconds() < 0:
            return 'overdue'
        elif time_left.total_seconds() < 2 * 3600:  # < 2 hours
            return 'final'
        elif time_left.total_seconds() < 24 * 3600:  # < 1 day
            return 'urgent'
        elif time_left.total_seconds() < 2 * 24 * 3600:  # < 2 days
            return 'quarter_day'
        elif time_left.total_seconds() < 5 * 24 * 3600:  # < 5 days
            return 'half_day'
        else:  # >= 5 days
            return 'daily'
    
    @staticmethod
    def calculate_next_reminder(
        deadline: datetime,
        last_reminder: Optional[datetime] = None,
        now: Optional[datetime] = None
    ) -> Tuple[datetime, str]:
        """
        Calculate next reminder time and level

        Args:
            deadline: Task deadline
            last_reminder: When was the last reminder sent (None if never)
            now: Current time (defaults to timezone.now())

        Returns:
            Tuple[datetime, str]: (next_reminder_time, reminder_level)
        """
        if now is None:
            from django.utils import timezone
            now = timezone.now()

        # Determine current reminder level
        level = ReminderCalculator.calculate_reminder_level(deadline, now)

        # If overdue, don't schedule next reminder
        if level == 'overdue':
            return (deadline, level)

        time_until_deadline = (deadline - now).total_seconds()

        # Special handling for short deadlines (< 2 hours)
        if level == 'final' and last_reminder is None:
            # For urgent tasks < 2h, send immediate reminder (5 minutes from now)
            next_reminder = now + timedelta(minutes=5)
            # Then schedule follow-ups every 30 minutes until deadline
            return (next_reminder, level)

        # For subsequent reminders on final level tasks
        if level == 'final' and last_reminder is not None:
            # Send reminders every 30 minutes for urgent tasks
            next_reminder = last_reminder + timedelta(minutes=30)
            # Don't send if too close to deadline (< 10 minutes)
            if (deadline - next_reminder).total_seconds() < 600:
                return (deadline - timedelta(minutes=10), level)
            return (next_reminder, level)

        # Get interval for this level
        interval = ReminderCalculator.INTERVALS.get(level, timedelta(hours=24))

        # Calculate next reminder time
        if last_reminder is None:
            # First reminder: for urgent tasks, send sooner
            if level == 'urgent':
                # For tasks < 24h, send first reminder within 30 minutes
                next_reminder = now + timedelta(minutes=30)
            else:
                # For longer-term tasks, use standard interval
                next_reminder = now + interval
        else:
            # Subsequent reminder: add interval to last reminder
            next_reminder = last_reminder + interval

        # Ensure next reminder doesn't exceed deadline
        # Leave at least 10 minutes buffer before deadline
        if next_reminder >= deadline - timedelta(minutes=10):
            # If we're too close, schedule for 2 hours before (or halfway if < 2h left)
            time_left_hours = time_until_deadline / 3600
            if time_left_hours > 2:
                next_reminder = deadline - timedelta(hours=2)
            else:
                # For tasks with < 2h left, schedule halfway to deadline
                next_reminder = now + timedelta(seconds=time_until_deadline / 2)

        return (next_reminder, level)
    
    @staticmethod
    def get_reminder_message_prefix(level: str) -> str:
        """
        Get reminder message prefix based on level
        
        Args:
            level: Reminder level
            
        Returns:
            str: Message prefix (e.g., "📅 Reminder", "🚨 FINAL REMINDER")
        """
        messages = {
            'daily': "📅 Reminder",
            'half_day': "⏰ Reminder",
            'quarter_day': "⚠️ Reminder",
            'urgent': "🔴 URGENT",
            'final': "🚨 FINAL REMINDER",
            'overdue': "❗️ OVERDUE",
        }
        
        return messages.get(level, "🔔 Reminder")