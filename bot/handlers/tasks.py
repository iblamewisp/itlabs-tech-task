from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.services.task_service import TaskService
from bot.formatters.task_formatter import TaskFormatter
from bot.keyboards.task_kb import (
    get_tasks_keyboard,
    get_task_detail_keyboard
)
import logging

logger = logging.getLogger(__name__)
router = Router()


async def _show_tasks_internal(
    telegram_id: int,
    task_service: TaskService,
    message_or_callback,
    page: int = 1,
    edit: bool = False
):
    """Internal helper to show tasks"""
    try:
        paginated = await task_service.get_tasks(telegram_id=telegram_id, page=page)

        text = TaskFormatter.format_task_list(paginated.items)

        if not paginated.items:
            if edit:
                await message_or_callback.edit_text(text)
            else:
                await message_or_callback.answer(text)
            return

        # Convert DTOs to dicts for keyboard
        tasks_dict = [
            {
                'id': t.id,
                'title': t.title,
                'is_completed': t.is_completed
            }
            for t in paginated.items
        ]

        if edit:
            await message_or_callback.edit_text(
                text,
                reply_markup=get_tasks_keyboard(
                    tasks_dict,
                    current_page=page,
                    total_pages=paginated.total_pages
                )
            )
        else:
            await message_or_callback.answer(
                text,
                reply_markup=get_tasks_keyboard(
                    tasks_dict,
                    current_page=page,
                    total_pages=paginated.total_pages
                )
            )

    except Exception as e:
        logger.error(f"Failed to fetch tasks: {e}")
        error_text = "❌ Failed to load tasks. Please try again."
        if edit:
            await message_or_callback.edit_text(error_text)
        else:
            await message_or_callback.answer(error_text)


@router.message(F.text == "📋 My Tasks")
@router.message(Command("tasks"))
async def show_tasks(message: Message, task_service: TaskService, page: int = 1):
    """Show user's tasks with pagination"""
    await _show_tasks_internal(
        telegram_id=message.from_user.id,
        task_service=task_service,
        message_or_callback=message,
        page=page,
        edit=False
    )


@router.callback_query(F.data.startswith("tasks_page:"))
async def paginate_tasks(callback: CallbackQuery, task_service: TaskService):
    """Handle pagination"""
    page = int(callback.data.split(":")[1])

    await _show_tasks_internal(
        telegram_id=callback.from_user.id,
        task_service=task_service,
        message_or_callback=callback.message,
        page=page,
        edit=True
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task:"))
async def task_detail(callback: CallbackQuery, task_service: TaskService):
    """Show task details"""
    task_id = callback.data.split(":")[1]
    
    try:
        task = await task_service.get_task(
            telegram_id=callback.from_user.id,
            task_id=task_id
        )
        
        if not task:
            await callback.answer("Task not found", show_alert=True)
            return

        text = TaskFormatter.format_task_detail(task)
        
        # Convert DTO to dict for keyboard
        task_dict = {
            'id': task.id,
            'is_completed': task.is_completed
        }
        
        await callback.message.edit_text(
            text,
            reply_markup=get_task_detail_keyboard(task_dict)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Failed to fetch task {task_id}: {e}")
        await callback.answer("Failed to load task", show_alert=True)


@router.callback_query(F.data.startswith("complete:"))
async def complete_task(callback: CallbackQuery, task_service: TaskService):
    """Mark task as completed"""
    task_id = callback.data.split(":")[1]
    
    try:
        updated_task = await task_service.toggle_completion(
            telegram_id=callback.from_user.id,
            task_id=task_id,
            is_completed=True
        )
        await callback.answer(
            TaskFormatter.format_task_completed(updated_task),
            show_alert=True
        )

        # Return to task list
        await _show_tasks_internal(
            telegram_id=callback.from_user.id,
            task_service=task_service,
            message_or_callback=callback.message,
            edit=True
        )
        
    except Exception as e:
        logger.error(f"Failed to complete task {task_id}: {e}")
        await callback.answer("Failed to update task", show_alert=True)


@router.callback_query(F.data.startswith("delete:"))
async def delete_task(callback: CallbackQuery, task_service: TaskService):
    """Delete task"""
    task_id = callback.data.split(":")[1]
    
    try:
        # Get task before deletion to show title in message
        task = await task_service.get_task(
            telegram_id=callback.from_user.id,
            task_id=task_id
        )
        
        if not task:
            await callback.answer("Task not found", show_alert=True)
            return
        
        await task_service.delete_task(
            telegram_id=callback.from_user.id,
            task_id=task_id
        )

        await callback.answer(
            TaskFormatter.format_task_deleted(task.title),
            show_alert=True
        )

        # Return to task list
        await _show_tasks_internal(
            telegram_id=callback.from_user.id,
            task_service=task_service,
            message_or_callback=callback.message,
            edit=True
        )
        
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        await callback.answer("Failed to delete task", show_alert=True)


@router.callback_query(F.data == "back_to_tasks")
async def back_to_tasks(callback: CallbackQuery, task_service: TaskService):
    """Return to tasks list"""
    await _show_tasks_internal(
        telegram_id=callback.from_user.id,
        task_service=task_service,
        message_or_callback=callback.message,
        edit=True
    )
    await callback.answer()


@router.callback_query(F.data == "show_completed")
async def show_completed_tasks(callback: CallbackQuery, task_service: TaskService):
    """Show completed tasks"""
    try:
        result = await task_service.get_tasks(
            telegram_id=callback.from_user.id,
            is_completed=True,
            page_size=100
        )
        tasks = result.items

        text = TaskFormatter.format_completed_list(tasks)

        if not tasks:
            await callback.answer("No completed tasks", show_alert=True)
            return
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Failed to fetch completed tasks: {e}")
        await callback.answer("Error loading tasks", show_alert=True)


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    """No-op callback for page indicator"""
    await callback.answer()