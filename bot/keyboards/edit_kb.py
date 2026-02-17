from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_edit_field_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing which field to edit"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✏️ Edit Title",
                callback_data="edit_field:title"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Edit Description",
                callback_data="edit_field:description"
            )
        ],
        [
            InlineKeyboardButton(
                text="⏰ Change Deadline",
                callback_data="edit_field:deadline"
            )
        ],
        [
            InlineKeyboardButton(
                text="📁 Change Category",
                callback_data="edit_field:category"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="edit_cancel"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
