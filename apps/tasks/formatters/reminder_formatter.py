from apps.tasks.models import Task
from apps.tasks.services.reminder_calculator import ReminderCalculator
from django.utils import timezone
from datetime import datetime

class ReminderFormatter:
    """Format reminder messages for tasks (Single Responsibility)"""
    
    @staticmethod
    def format_reminder_message(task: Task) -> str:
        """
        Format complete reminder message for a task
        
        Args:
            task: Task instance with deadline
            
        Returns:
            str: Formatted reminder message ready to send
        """
        # Get urgency-based prefix
        message_prefix = ReminderCalculator.get_reminder_message_prefix(
            task.reminder_level
        )
        
        # Build message parts
        parts = []
        
        # 1. Prefix + Title
        parts.append(f"{message_prefix}: {task.title}")
        
        # 2. Description (if exists)
        if task.description:
            parts.append(f"\n{task.description}")
        
        # 3. Category (if exists)
        if task.category:
            parts.append(f"\n📁 Category: {task.category.name}")
        
        # 4. Time left
        time_left_text = ReminderFormatter._format_time_left(task.deadline)
        parts.append(f"\n{time_left_text}")
        
        # 5. Deadline
        deadline_text = ReminderFormatter._format_deadline(task.deadline)
        parts.append(f"\n{deadline_text}")
        
        return "".join(parts)
    
    @staticmethod
    def _format_time_left(deadline: datetime) -> str:
        """
        Format time left until deadline
        
        Args:
            deadline: Task deadline
            
        Returns:
            str: Formatted time left text (e.g., "⏱ 2 hours left")
        """
        time_left = deadline - timezone.now()
        total_seconds = time_left.total_seconds()
        
        if total_seconds < 0:
            # Overdue
            hours_overdue = abs(int(total_seconds / 3600))
            if hours_overdue < 24:
                return f"⏱ OVERDUE by {hours_overdue} hours"
            else:
                days_overdue = hours_overdue // 24
                return f"⏱ OVERDUE by {days_overdue} days"
        
        # Not overdue
        hours_left = int(total_seconds / 3600)
        
        if hours_left < 1:
            minutes_left = int(total_seconds / 60)
            return f"⏱ {minutes_left} minutes left"
        elif hours_left < 24:
            return f"⏱ {hours_left} hours left"
        else:
            days_left = hours_left // 24
            remaining_hours = hours_left % 24
            if remaining_hours > 0:
                return f"⏱ {days_left} days {remaining_hours} hours left"
            return f"⏱ {days_left} days left"
    
    @staticmethod
    def _format_deadline(deadline: datetime) -> str:
        """
        Format deadline timestamp
        
        Args:
            deadline: Task deadline
            
        Returns:
            str: Formatted deadline (e.g., "🎯 Deadline: 2026-02-20 14:30")
        """
        return f"🎯 Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}"
    
    @staticmethod
    def format_overdue_message(task: Task) -> str:
        """
        Format message for overdue task
        
        Args:
            task: Overdue task
            
        Returns:
            str: Formatted overdue message
        """
        parts = []
        
        # Overdue header
        parts.append(f"❗️ OVERDUE TASK: {task.title}")
        
        if task.description:
            parts.append(f"\n{task.description}")
        
        if task.category:
            parts.append(f"\n📁 Category: {task.category.name}")
        
        # How long overdue
        time_left_text = ReminderFormatter._format_time_left(task.deadline)
        parts.append(f"\n{time_left_text}")
        
        # Original deadline
        parts.append(f"\n🎯 Was due: {task.deadline.strftime('%Y-%m-%d %H:%M')}")
        
        # Call to action
        parts.append("\n\n⚡️ Please complete or reschedule this task!")
        
        return "".join(parts)
    
    @staticmethod
    def format_deadline_summary(task: Task) -> str:
        """
        Format short deadline summary (for lists)
        
        Args:
            task: Task instance
            
        Returns:
            str: Short summary (e.g., "⏰ Due in 2 hours")
        """
        if not task.deadline:
            return ""
        
        time_left = task.deadline - timezone.now()
        total_seconds = time_left.total_seconds()
        
        if total_seconds < 0:
            hours_overdue = abs(int(total_seconds / 3600))
            if hours_overdue < 24:
                return f"❗️ {hours_overdue}h overdue"
            days_overdue = hours_overdue // 24
            return f"❗️ {days_overdue}d overdue"
        
        hours_left = int(total_seconds / 3600)
        
        if hours_left < 1:
            minutes_left = int(total_seconds / 60)
            return f"🔴 {minutes_left}m left"
        elif hours_left < 24:
            return f"⏰ {hours_left}h left"
        else:
            days_left = hours_left // 24
            return f"⏰ {days_left}d left"