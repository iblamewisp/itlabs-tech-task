from bot.dto import TaskDTO
from typing import List


class TaskFormatter:
    """Formatter for task messages"""
    
    @staticmethod
    def format_task_list(tasks: List[TaskDTO]) -> str:
        """Format tasks list message"""
        if not tasks:
            return "📭 You have no tasks yet.\n\nUse 'Add Task' to create your first task!"
        
        active = [t for t in tasks if not t.is_completed]
        completed = [t for t in tasks if t.is_completed]
        
        text = "📋 <b>Your Tasks</b>\n\n"
        text += f"<b>Active: {len(active)}</b>\n"
        
        if completed:
            text += f"✅ Completed: {len(completed)}\n"
        
        return text
    
    @staticmethod
    def format_task_detail(task: TaskDTO) -> str:
        """Format detailed task view"""
        from bot.utils.deadline_parser import DeadlineParser
        from datetime import datetime

        text = f"📋 <b>{task.title}</b>\n\n"

        if task.description:
            text += f"{task.description}\n\n"

        if task.category_name:
            text += f"📁 Category: {task.category_name}\n"

        if task.deadline:
            deadline_dt = datetime.fromisoformat(task.deadline)
            deadline_text = DeadlineParser.format_deadline(deadline_dt)
            text += f"⏰ Deadline: {deadline_text}\n"

            if task.next_reminder_time:
                reminder_dt = datetime.fromisoformat(task.next_reminder_time)
                reminder_text = DeadlineParser.format_deadline(reminder_dt)
                text += f"🔔 Next reminder: {reminder_text}\n"

        status = "✅ Completed" if task.is_completed else "⏳ Active"
        text += f"\nStatus: {status}"

        if task.created_at:
            created_dt = datetime.fromisoformat(task.created_at)
            text += f"\n🗓 Created: {created_dt.strftime('%d.%m.%Y %H:%M')}"

        return text
    
    @staticmethod
    def format_completed_list(tasks: List[TaskDTO]) -> str:
        """Format completed tasks list"""
        if not tasks:
            return "No completed tasks"
        
        text = f"✅ <b>Completed Tasks ({len(tasks)})</b>\n\n"
        
        for task in tasks[:20]:  # Show first 20
            text += f"▫️ {task.title}\n"
        
        return text
      
    @staticmethod
    def format_edit_menu(task: TaskDTO) -> str:
        """Format edit menu message"""
        return (
            f"<b>Editing: {task.title}</b>\n\n"
            f"What do you want to edit?"
        )
    
    @staticmethod
    def format_current_title(task: TaskDTO) -> str:
        """Format current title prompt"""
        return (
            f"<b>Current title:</b> {task.title}\n\n"
            f"Send me the new title:"
        )
    
    @staticmethod
    def format_current_description(task: TaskDTO) -> str:
        """Format current description prompt"""
        current_desc = task.description or "None"
        return (
            f"<b>Current description:</b>\n{current_desc}\n\n"
            f"Send me the new description (or /skip to clear):"
        )
    
    @staticmethod
    def format_title_updated(task: TaskDTO) -> str:
        """Format title updated message"""
        return (
            f"✅ Title updated!\n\n"
            f"<b>{task.title}</b>"
        )
    
    @staticmethod
    def format_description_updated(task: TaskDTO) -> str:
        """Format description updated message"""
        return (
            f"✅ Description updated!\n\n"
            f"<b>{task.title}</b>\n"
            f"{task.description or 'No description'}"
        )
    
    @staticmethod
    def format_category_updated(task: TaskDTO) -> str:
        """Format category updated message"""
        return (
            f"✅ Category updated!\n\n"
            f"<b>{task.title}</b>\n"
        )

    @staticmethod
    def format_deadline_updated(task: TaskDTO) -> str:
        """Format deadline updated message"""
        from bot.utils.deadline_parser import DeadlineParser
        from datetime import datetime

        text = f"✅ Deadline updated!\n\n<b>{task.title}</b>\n"

        if task.deadline:
            deadline_dt = datetime.fromisoformat(task.deadline)
            deadline_text = DeadlineParser.format_deadline(deadline_dt)
            text += f"⏰ Deadline: {deadline_text}\n"
            text += "🔔 Smart reminders enabled!"
        else:
            text += "⏰ Deadline removed\n"
            text += "Reminders disabled"

        return text

    @staticmethod
    def format_task_created(task: TaskDTO) -> str:
        """Format task created success message"""
        return (
            f"✅ Task created!\n\n"
            f"<b>{task.title}</b>\n"
            f"{task.description or ''}"
        )

    @staticmethod
    def format_task_completed(task: TaskDTO) -> str:
        """Format task completion message"""
        return f"✅ Task completed: {task.title}"
    
    @staticmethod
    def format_task_deleted(task_title: str) -> str:
        """Format task deletion message"""
        return f"🗑 Task deleted: {task_title}"