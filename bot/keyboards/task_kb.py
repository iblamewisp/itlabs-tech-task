from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_tasks_keyboard(
    tasks: List[Dict[str, Any]],
    current_page: int = 1,
    total_pages: int = 1
) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for tasks list with pagination

    Args:
        tasks: Current page tasks (already filtered and paginated by backend)
        current_page: Current page number from backend
        total_pages: Total pages from backend
    """
    buttons = []

    # Task buttons - backend already filtered active tasks
    for task in tasks:
        status = "✅" if task['is_completed'] else "⏳"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {task['title'][:30]}",
                callback_data=f"task:{task['id']}"
            )
        ])

    # Pagination buttons (only if multiple pages)
    if total_pages > 1:
        pagination_row = []

        # Previous button
        if current_page > 1:
            pagination_row.append(
                InlineKeyboardButton(
                    text="◀️ Prev",
                    callback_data=f"tasks_page:{current_page - 1}"
                )
            )

        # Page indicator
        pagination_row.append(
            InlineKeyboardButton(
                text=f"📄 {current_page}/{total_pages}",
                callback_data="noop"
            )
        )

        # Next button
        if current_page < total_pages:
            pagination_row.append(
                InlineKeyboardButton(
                    text="Next ▶️",
                    callback_data=f"tasks_page:{current_page + 1}"
                )
            )

        buttons.append(pagination_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(task: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Get inline keyboard for task detail"""
    buttons = []
    
    if not task['is_completed']:
        buttons.append([
            InlineKeyboardButton(
                text="✅ Mark as Complete",
                callback_data=f"complete:{task['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="✏️ Edit",
            callback_data=f"edit:{task['id']}"
        ),
        InlineKeyboardButton(
            text="🗑 Delete",
            callback_data=f"delete:{task['id']}"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Back to Tasks",
            callback_data="back_to_tasks"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_category_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for category selection
    
    Args:
        categories: List of category dicts with 'id' and 'name'
    """
    buttons = []
    
    # Category buttons
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {category['name']}",
                callback_data=f"task_category:{category['id']}"
            )
        ])

    # No category option
    buttons.append([
        InlineKeyboardButton(
            text="❌ No Category",
            callback_data="task_category:none"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)