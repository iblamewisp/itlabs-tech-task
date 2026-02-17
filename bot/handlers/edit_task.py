from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.services.task_service import TaskService
from bot.formatters.task_formatter import TaskFormatter
from bot.dialogs.states import EditTaskStates
from bot.keyboards.edit_kb import get_edit_field_keyboard
from bot.keyboards.task_kb import get_category_keyboard
from bot.keyboards.deadline_kb import get_quick_deadline_keyboard, parse_quick_deadline
from bot.utils.deadline_parser import DeadlineParser
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("edit:"))
async def start_edit_task(
    callback: CallbackQuery,
    state: FSMContext,
    task_service: TaskService
):
    """Start task editing flow"""
    task_id = callback.data.split(":")[1]
    
    try:
        task = await task_service.get_task(
            telegram_id=callback.from_user.id,
            task_id=task_id
        )
        
        if not task:
            await callback.answer("Task not found", show_alert=True)
            return

        # Store only task_id (JSON serializable), not the entire TaskDTO object
        await state.update_data(task_id=task_id)
        await state.set_state(EditTaskStates.waiting_for_field)

        text = TaskFormatter.format_edit_menu(task)
        
        await callback.message.edit_text(
            text,
            reply_markup=get_edit_field_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Failed to start edit for task {task_id}: {e}")
        await callback.answer("Failed to start editing", show_alert=True)


@router.callback_query(EditTaskStates.waiting_for_field, F.data == "edit_field:title")
async def edit_title_prompt(callback: CallbackQuery, state: FSMContext, task_service: TaskService):
    """Prompt for new title"""
    data = await state.get_data()
    task_id = data['task_id']

    # Fetch task again (it wasn't stored in state)
    task = await task_service.get_task(
        telegram_id=callback.from_user.id,
        task_id=task_id
    )

    text = TaskFormatter.format_current_title(task)

    await callback.message.edit_text(text)
    await state.set_state(EditTaskStates.waiting_for_title)
    await callback.answer()


@router.message(EditTaskStates.waiting_for_title)
async def process_new_title(
    message: Message,
    state: FSMContext,
    task_service: TaskService
):
    """Update task title"""
    data = await state.get_data()
    task_id = data['task_id']
    
    try:
        updated_task = await task_service.update_title(
            telegram_id=message.from_user.id,
            task_id=task_id,
            title=message.text
        )
        
        text = TaskFormatter.format_title_updated(updated_task)
        await message.answer(text)
        
        logger.info(f"Task {task_id} title updated")
        
    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception as e:
        logger.error(f"Failed to update title: {e}")
        await message.answer("❌ Failed to update title. Please try again.")
    
    finally:
        await state.clear()


@router.callback_query(EditTaskStates.waiting_for_field, F.data == "edit_field:description")
async def edit_description_prompt(callback: CallbackQuery, state: FSMContext, task_service: TaskService):
    """Prompt for new description"""
    data = await state.get_data()
    task_id = data['task_id']

    # Fetch task again (it wasn't stored in state)
    task = await task_service.get_task(
        telegram_id=callback.from_user.id,
        task_id=task_id
    )

    text = TaskFormatter.format_current_description(task)

    await callback.message.edit_text(text)
    await state.set_state(EditTaskStates.waiting_for_description)
    await callback.answer()


@router.message(EditTaskStates.waiting_for_description)
async def process_new_description(
    message: Message,
    state: FSMContext,
    task_service: TaskService
):
    """Update task description"""
    data = await state.get_data()
    task_id = data['task_id']
    
    description = "" if message.text == "/skip" else message.text
    
    try:
        updated_task = await task_service.update_description(
            telegram_id=message.from_user.id,
            task_id=task_id,
            description=description
        )
        
        text = TaskFormatter.format_description_updated(updated_task)
        await message.answer(text)
        
        logger.info(f"Task {task_id} description updated")
        
    except Exception as e:
        logger.error(f"Failed to update description: {e}")
        await message.answer("❌ Failed to update description. Please try again.")
    
    finally:
        await state.clear()


@router.callback_query(EditTaskStates.waiting_for_field, F.data == "edit_field:deadline")
async def edit_deadline_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for new deadline"""
    await callback.message.edit_text(
        "⏰ Set a new deadline:\n\n"
        "You can:\n"
        "• Choose a quick option below\n"
        "• Type custom (e.g., 'tomorrow', 'in 3 days', '20.02 18:00')\n"
        "• Remove deadline",
        reply_markup=get_quick_deadline_keyboard()
    )
    await state.set_state(EditTaskStates.waiting_for_deadline)
    await callback.answer()


@router.callback_query(EditTaskStates.waiting_for_deadline, F.data.startswith("deadline:"))
async def process_deadline_change_button(
    callback: CallbackQuery,
    state: FSMContext,
    task_service: TaskService
):
    """Process deadline button selection"""
    data = await state.get_data()
    task_id = data['task_id']
    action = callback.data.split(":")[1]

    try:
        if action == "skip":
            # Remove deadline
            deadline = None
            deadline_text = "removed"
        elif action == "custom":
            # User wants to type custom deadline
            await callback.message.edit_text(
                "✏️ Type your new deadline:\n\n"
                "Examples:\n"
                "• tomorrow\n"
                "• in 3 days\n"
                "• 20.02 18:00\n"
                "• 18:00"
            )
            await callback.answer()
            return
        elif action == "quick":
            # Quick deadline selection
            quick_code = callback.data.split(":")[2]
            deadline = parse_quick_deadline(quick_code)
            deadline_text = DeadlineParser.format_deadline(deadline)
            deadline = deadline.isoformat()

        # Update task deadline
        updated_task = await task_service.update_deadline(
            telegram_id=callback.from_user.id,
            task_id=task_id,
            deadline=deadline,
        )

        text = TaskFormatter.format_deadline_updated(updated_task)
        await callback.message.edit_text(text)
        await callback.answer(f"⏰ Deadline {deadline_text}", show_alert=False)

        logger.info(f"Task {task_id} deadline updated")

    except Exception as e:
        logger.error(f"Failed to update deadline: {e}")
        await callback.answer("Failed to update deadline", show_alert=True)

    finally:
        await state.clear()


@router.message(EditTaskStates.waiting_for_deadline)
async def process_deadline_change_text(
    message: Message,
    state: FSMContext,
    task_service: TaskService
):
    """Update task deadline from text input"""
    data = await state.get_data()
    task_id = data['task_id']

    deadline = DeadlineParser.parse(message.text)

    if not deadline:
        await message.answer(
            "❌ Couldn't parse that deadline. Please try again:\n\n"
            "Examples: 'tomorrow', 'in 3 days', '20.02 18:00'"
        )
        return

    try:
        updated_task = await task_service.update_deadline(
            telegram_id=message.from_user.id,
            task_id=task_id,
            deadline=deadline.isoformat()
        )

        text = TaskFormatter.format_deadline_updated(updated_task)
        await message.answer(text)

        logger.info(f"Task {task_id} deadline updated")

    except Exception as e:
        logger.error(f"Failed to update deadline: {e}")
        await message.answer("❌ Failed to update deadline. Please try again.")

    finally:
        await state.clear()


@router.callback_query(EditTaskStates.waiting_for_field, F.data == "edit_field:category")
async def edit_category_prompt(
    callback: CallbackQuery,
    state: FSMContext,
    task_service: TaskService
):
    """Show category selection"""
    try:
        categories = await task_service.get_categories(
            telegram_id=callback.from_user.id
        )
        
        categories_dict = [
            {'id': c.id, 'name': c.name}
            for c in categories
        ]
        
        await callback.message.edit_text(
            "Select a new category:",
            reply_markup=get_category_keyboard(categories_dict)
        )
        
        await state.set_state(EditTaskStates.waiting_for_category)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Failed to load categories: {e}")
        await callback.answer("Failed to load categories", show_alert=True)


@router.callback_query(EditTaskStates.waiting_for_category, F.data.startswith("task_category:"))
async def process_category_change(
    callback: CallbackQuery,
    state: FSMContext,
    task_service: TaskService
):
    """Update task category"""
    data = await state.get_data()
    task_id = data['task_id']
    
    category_id = callback.data.split(":")[1]
    if category_id == "none":
        category_id = None
    
    try:
        updated_task = await task_service.update_category(
            telegram_id=callback.from_user.id,
            task_id=task_id,
            category_id=category_id
        )
        
        text = TaskFormatter.format_category_updated(updated_task)
        
        await callback.message.edit_text(text)
        
        logger.info(f"Task {task_id} category updated")
        
    except Exception as e:
        logger.error(f"Failed to update category: {e}")
        await callback.answer("Failed to update category", show_alert=True)
    
    finally:
        await state.clear()


# ═══════════════════════════════════════════════════════
# Cancel Editing
# ═══════════════════════════════════════════════════════

@router.callback_query(EditTaskStates.waiting_for_field, F.data == "edit_cancel")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    """Cancel editing"""
    await state.clear()
    await callback.message.edit_text("❌ Editing cancelled")
    await callback.answer()