from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_categories_list_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for categories list

    Args:
        categories: List of category dicts with 'id' and 'name'
    """
    buttons = []

    # "All Tasks" button at the top
    buttons.append([
        InlineKeyboardButton(
            text="📋 All Tasks",
            callback_data="category:all"
        )
    ])

    # Category buttons
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {category['name']}",
                callback_data=f"category:{category['id']}"
            )
        ])

    # Add Category button
    buttons.append([
        InlineKeyboardButton(
            text="➕ Add Category",
            callback_data="add_category"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_category_tasks_keyboard(
    tasks: List[Dict[str, Any]],
    category_id: str,
    page: int = 1,
    page_size: int = 10
) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for tasks in a category with pagination

    Args:
        tasks: Full list of tasks in the category
        category_id: Category ID or 'all' for all tasks
        page: Current page (1-indexed)
        page_size: Tasks per page
    """
    buttons = []

    # Filter active tasks
    active_tasks = [t for t in tasks if not t['is_completed']]
    total_tasks = len(active_tasks)
    total_pages = (total_tasks + page_size - 1) // page_size if total_tasks > 0 else 1

    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    current_page_tasks = active_tasks[start_idx:end_idx]

    # Task buttons
    for task in current_page_tasks:
        status = "✅" if task['is_completed'] else "⏳"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {task['title'][:30]}",
                callback_data=f"task:{task['id']}"
            )
        ])

    # Pagination buttons (only if > page_size tasks)
    if total_pages > 1:
        pagination_row = []

        # Previous button
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton(
                    text="◀️ Prev",
                    callback_data=f"category_tasks_page:{category_id}:{page - 1}"
                )
            )

        # Page indicator
        pagination_row.append(
            InlineKeyboardButton(
                text=f"📄 {page}/{total_pages}",
                callback_data="noop"
            )
        )

        # Next button
        if page < total_pages:
            pagination_row.append(
                InlineKeyboardButton(
                    text="Next ▶️",
                    callback_data=f"category_tasks_page:{category_id}:{page + 1}"
                )
            )

        buttons.append(pagination_row)

    # Back to categories button
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Back to Categories",
            callback_data="back_to_categories"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
