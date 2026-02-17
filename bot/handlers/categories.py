from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.services.task_service import TaskService
from bot.formatters.category_formatter import CategoryFormatter
from bot.keyboards.category_kb import (
    get_categories_list_keyboard,
    get_category_tasks_keyboard
)
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "📁 Categories")
async def show_categories(message: Message, task_service: TaskService):
    """Show user's categories"""
    try:
        categories = await task_service.get_categories(
            telegram_id=message.from_user.id
        )

        logger.info(f"Categories fetched: {categories}, type: {type(categories)}")

        text = CategoryFormatter.format_category_list(categories)

        # Convert DTOs to dicts for keyboard
        categories_dict = [
            {'id': c.id, 'name': c.name}
            for c in categories
        ]

        await message.answer(
            text,
            reply_markup=get_categories_list_keyboard(categories_dict)
        )

    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}", exc_info=True)
        await message.answer("❌ Failed to load categories. Please try again.")


@router.callback_query(F.data.startswith("category:"))
async def show_category_tasks(callback: CallbackQuery, task_service: TaskService):
    """Show tasks in selected category or all tasks"""
    category_id = callback.data.split(":")[1]

    try:
        if category_id == "all":
            # Show all tasks without category filter
            result = await task_service.get_tasks(
                telegram_id=callback.from_user.id,
                page_size=100
            )
            tasks = result.items
            text = CategoryFormatter.format_all_tasks_view(tasks)
        else:
            # Show tasks in specific category
            categories = await task_service.get_categories(
                telegram_id=callback.from_user.id
            )

            # Find the category
            category = next((c for c in categories if c.id == category_id), None)

            if not category:
                await callback.answer("Category not found", show_alert=True)
                return

            # Get all tasks and filter by category
            result = await task_service.get_tasks(
                telegram_id=callback.from_user.id,
                page_size=100
            )
            tasks = [t for t in result.items if t.category_id == category_id]

            text = CategoryFormatter.format_category_tasks(category, tasks)

        # Convert DTOs to dicts for keyboard
        tasks_dict = [
            {
                'id': t.id,
                'title': t.title,
                'is_completed': t.is_completed
            }
            for t in tasks
        ]

        await callback.message.edit_text(
            text,
            reply_markup=get_category_tasks_keyboard(
                tasks_dict,
                category_id=category_id,
                page=1
            )
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Failed to show category tasks: {e}")
        await callback.answer("Failed to load tasks", show_alert=True)


@router.callback_query(F.data.startswith("category_tasks_page:"))
async def paginate_category_tasks(callback: CallbackQuery, task_service: TaskService):
    """Handle pagination for category tasks"""
    parts = callback.data.split(":")
    category_id = parts[1]
    page = int(parts[2])

    try:
        if category_id == "all":
            result = await task_service.get_tasks(
                telegram_id=callback.from_user.id,
                page_size=100
            )
            tasks = result.items
            text = CategoryFormatter.format_all_tasks_view(tasks)
        else:
            categories = await task_service.get_categories(
                telegram_id=callback.from_user.id
            )
            category = next((c for c in categories if c.id == category_id), None)

            if not category:
                await callback.answer("Category not found", show_alert=True)
                return

            result = await task_service.get_tasks(
                telegram_id=callback.from_user.id,
                page_size=100
            )
            tasks = [t for t in result.items if t.category_id == category_id]

            text = CategoryFormatter.format_category_tasks(category, tasks)

        tasks_dict = [
            {'id': t.id, 'title': t.title, 'is_completed': t.is_completed}
            for t in tasks
        ]

        await callback.message.edit_text(
            text,
            reply_markup=get_category_tasks_keyboard(
                tasks_dict,
                category_id=category_id,
                page=page
            )
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Pagination error: {e}")
        await callback.answer("Error loading page", show_alert=True)


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, task_service: TaskService):
    """Return to categories list"""
    try:
        categories = await task_service.get_categories(
            telegram_id=callback.from_user.id
        )

        text = CategoryFormatter.format_category_list(categories)

        categories_dict = [
            {'id': c.id, 'name': c.name}
            for c in categories
        ]

        await callback.message.edit_text(
            text,
            reply_markup=get_categories_list_keyboard(categories_dict)
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Failed to return to categories: {e}")
        await callback.answer("Error loading categories", show_alert=True)
