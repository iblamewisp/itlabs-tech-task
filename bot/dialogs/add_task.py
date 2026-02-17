from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.services.task_service import TaskService
from bot.dialogs.states import AddTaskStates
from bot.keyboards.task_kb import get_category_keyboard
from bot.keyboards.deadline_kb import get_quick_deadline_keyboard, parse_quick_deadline
from bot.utils.deadline_parser import DeadlineParser
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "➕ Add Task")
async def start_add_task(message: Message, state: FSMContext):
    """Start task creation flow"""
    await message.answer(
        "📝 Let's create a new task!\n\n"
        "Please enter the task title:"
    )
    await state.set_state(AddTaskStates.waiting_for_title)


@router.message(AddTaskStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Process task title"""
    await state.update_data(title=message.text)

    await message.answer(
        "Great! Now enter a description (or send /skip):"
    )
    await state.set_state(AddTaskStates.waiting_for_description)


@router.message(AddTaskStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Process description and show deadline selection"""
    description = "" if message.text == "/skip" else message.text
    await state.update_data(description=description)

    # Show deadline selection
    await message.answer(
        "⏰ Set a deadline for this task:\n\n"
        "You can:\n"
        "• Choose a quick option below\n"
        "• Type custom (e.g., 'tomorrow', 'in 3 days', '20.02 18:00')\n"
        "• Skip to create without deadline",
        reply_markup=get_quick_deadline_keyboard()
    )

    await state.set_state(AddTaskStates.waiting_for_deadline)


@router.callback_query(AddTaskStates.waiting_for_deadline, F.data.startswith("deadline:"))
async def process_deadline_button(
    callback: CallbackQuery,
    state: FSMContext,
    task_service: TaskService
):
    """Process deadline button selection"""
    action = callback.data.split(":")[1]

    if action == "skip":
        # No deadline - proceed to category selection
        await state.update_data(deadline=None)
        await show_category_selection(callback.message, state, task_service, edit=True)
        await callback.answer()
        return

    elif action == "custom":
        # User wants to type custom deadline
        await callback.message.edit_text(
            "✏️ Type your deadline:\n\n"
            "Examples:\n"
            "• tomorrow\n"
            "• in 3 days\n"
            "• 20.02 18:00\n"
            "• 18:00\n\n"
            "Or send /skip to skip"
        )
        await callback.answer()
        return

    elif action == "quick":
        # Quick deadline selection
        quick_code = callback.data.split(":")[2]
        deadline = parse_quick_deadline(quick_code)
        await state.update_data(deadline=deadline.isoformat())

        deadline_text = DeadlineParser.format_deadline(deadline)
        await callback.answer(f"⏰ Deadline set: {deadline_text}", show_alert=False)

        # Proceed to category selection
        await show_category_selection(
            callback.message,
            state,
            task_service,
            telegram_id=callback.from_user.id,
            edit=True
        )


@router.message(AddTaskStates.waiting_for_deadline)
async def process_deadline_text(
    message: Message,
    state: FSMContext,
    task_service: TaskService
):
    """Process deadline text input"""
    if message.text == "/skip":
        await state.update_data(deadline=None)
    else:
        deadline = DeadlineParser.parse(message.text)

        if not deadline:
            await message.answer(
                "❌ Couldn't parse that deadline. Please try again:\n\n"
                "Examples: 'tomorrow', 'in 3 days', '20.02 18:00'"
            )
            return

        await state.update_data(deadline=deadline.isoformat())

        deadline_text = DeadlineParser.format_deadline(deadline)
        await message.answer(f"⏰ Deadline set: {deadline_text}")

    # Proceed to category selection
    await show_category_selection(
        message,
        state,
        task_service,
        telegram_id=message.from_user.id,
        edit=False
    )


async def show_category_selection(
    message: Message,
    state: FSMContext,
    task_service: TaskService,
    telegram_id: int,
    edit: bool = False
):
    """Show category selection or create task if no categories"""
    try:
        categories = await task_service.get_categories(telegram_id=telegram_id)

        if not categories:
            # No categories - create task immediately
            await create_task_final(message, state, task_service, telegram_id, None, edit)
            return

        # Show category selection
        categories_dict = [
            {'id': c.id, 'name': c.name}
            for c in categories
        ]

        text = "Almost done! Select a category:"

        if edit:
            await message.edit_text(text, reply_markup=get_category_keyboard(categories_dict))
        else:
            await message.answer(text, reply_markup=get_category_keyboard(categories_dict))

        await state.set_state(AddTaskStates.waiting_for_category)

    except Exception as e:
        logger.error(f"Failed to load categories: {e}", exc_info=True)
        error_text = "❌ Failed to load categories. Creating task without category..."

        if edit:
            await message.edit_text(error_text)
        else:
            await message.answer(error_text)

        # Create task without category
        await create_task_final(message, state, task_service, telegram_id, None, edit)


@router.callback_query(AddTaskStates.waiting_for_category, F.data.startswith("task_category:"))
async def process_category_selection(
    callback: CallbackQuery,
    state: FSMContext,
    task_service: TaskService
):
    """Process category selection and create task"""
    category_id = callback.data.split(":")[1]
    if category_id == "none":
        category_id = None

    await create_task_final(
        callback.message,
        state,
        task_service,
        telegram_id=callback.from_user.id,
        category_id=category_id,
        edit=True
    )
    await callback.answer()


async def create_task_final(
    message: Message,
    state: FSMContext,
    task_service: TaskService,
    telegram_id: int,
    category_id: str = None,
    edit: bool = False
):
    """Final step: create task with all data"""
    data = await state.get_data()

    try:
        task = await task_service.create_task(
            telegram_id=telegram_id,
            title=data['title'],
            description=data.get('description', ''),
            category_id=category_id,
            deadline=data.get('deadline')
        )

        # Format success message
        text = f"✅ Task created!\n\n<b>{task.title}</b>\n"

        if task.description:
            text += f"{task.description}\n"

        if task.category_name:
            text += f"\n📁 Category: {task.category_name}"

        if task.deadline:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(task.deadline)
            deadline_text = DeadlineParser.format_deadline(deadline_dt)
            text += f"\n⏰ Deadline: {deadline_text}"
            text += "\n🔔 Smart reminders enabled!"

        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)

        logger.info(f"Task created: {task.id}")

    except ValueError as e:
        error_text = f"❌ {e}"
        if edit:
            await message.edit_text(error_text)
        else:
            await message.answer(error_text)
    except Exception as e:
        logger.error(f"Failed to create task: {e}", exc_info=True)
        error_text = "❌ Failed to create task. Please try again."
        if edit:
            await message.edit_text(error_text)
        else:
            await message.answer(error_text)

    finally:
        await state.clear()
