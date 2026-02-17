from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = [
        [
            KeyboardButton(text="📋 My Tasks"),
            KeyboardButton(text="➕ Add Task")
        ],
        [
            KeyboardButton(text="📁 Categories"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Choose an action..."
    )