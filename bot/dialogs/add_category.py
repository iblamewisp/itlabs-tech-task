from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.services.task_service import TaskService
from bot.dialogs.states import AddCategoryStates
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "add_category")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    """Start category creation flow"""
    await callback.message.edit_text(
        "📁 Let's create a new category!\n\n"
        "Please enter the category name:"
    )
    await state.set_state(AddCategoryStates.waiting_for_name)
    await callback.answer()


@router.message(AddCategoryStates.waiting_for_name)
async def process_category_name(
    message: Message,
    state: FSMContext,
    task_service: TaskService
):
    """Process category name and create category"""
    name = message.text.strip()

    if not name:
        await message.answer("❌ Category name cannot be empty. Please try again:")
        return

    if len(name) > 50:
        await message.answer("❌ Category name is too long (max 50 chars). Please try again:")
        return

    try:
        category = await task_service.create_category(
            telegram_id=message.from_user.id,
            name=name
        )

        await message.answer(
            f"✅ Category created!\n\n"
            f"📁 <b>{category.name}</b>\n\n"
            f"You can now assign tasks to this category."
        )

        logger.info(f"Category created: {category.id} by user {message.from_user.id}")

    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception as e:
        logger.error(f"Failed to create category: {e}", exc_info=True)
        await message.answer("❌ Failed to create category. Please try again.")

    finally:
        await state.clear()
