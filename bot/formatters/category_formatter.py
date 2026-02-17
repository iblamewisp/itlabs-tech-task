from bot.dto import CategoryDTO, TaskDTO
from typing import List


class CategoryFormatter:
    """Formatter for category messages"""

    @staticmethod
    def format_category_list(categories: List[CategoryDTO]) -> str:
        """Format categories list message"""
        if not categories:
            return (
                "📁 <b>Your Categories</b>\n\n"
                "You don't have any categories yet.\n\n"
                "Categories help organize your tasks!"
            )

        text = "📁 <b>Your Categories</b>\n\n"
        text += f"You have {len(categories)} categor{'y' if len(categories) == 1 else 'ies'}:\n\n"

        return text

    @staticmethod
    def format_category_tasks(
        category: CategoryDTO,
        tasks: List[TaskDTO]
    ) -> str:
        """Format tasks in a specific category"""
        active = [t for t in tasks if not t.is_completed]
        completed = [t for t in tasks if t.is_completed]

        text = f"📁 <b>{category.name}</b>\n\n"

        if not tasks:
            text += "No tasks in this category yet."
        else:
            text += f"<b>Active: {len(active)}</b>\n"
            if completed:
                text += f"✅ Completed: {len(completed)}\n"

        return text

    @staticmethod
    def format_all_tasks_view(tasks: List[TaskDTO]) -> str:
        """Format all tasks view (without category filter)"""
        active = [t for t in tasks if not t.is_completed]
        completed = [t for t in tasks if t.is_completed]

        text = "📋 <b>All Tasks</b>\n\n"

        if not tasks:
            text += "You have no tasks yet."
        else:
            text += f"<b>Active: {len(active)}</b>\n"
            if completed:
                text += f"✅ Completed: {len(completed)}\n"

        return text

    @staticmethod
    def format_category_created(category: CategoryDTO) -> str:
        """Format category creation success message"""
        return f"✅ Category created: {category.name}"
