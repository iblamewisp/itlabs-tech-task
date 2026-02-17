from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, timezone


def get_quick_deadline_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for quick deadline selection

    Provides quick options for common deadlines
    """
    buttons = [
        # Row 1: Quick time options
        [
            InlineKeyboardButton(
                text="⏰ 1 hour",
                callback_data="deadline:quick:1h"
            ),
            InlineKeyboardButton(
                text="⏰ 3 hours",
                callback_data="deadline:quick:3h"
            ),
            InlineKeyboardButton(
                text="⏰ 6 hours",
                callback_data="deadline:quick:6h"
            ),
        ],
        # Row 2: Days
        [
            InlineKeyboardButton(
                text="📅 Tomorrow",
                callback_data="deadline:quick:1d"
            ),
            InlineKeyboardButton(
                text="📅 In 3 days",
                callback_data="deadline:quick:3d"
            ),
        ],
        # Row 3: Week
        [
            InlineKeyboardButton(
                text="📆 In 1 week",
                callback_data="deadline:quick:1w"
            ),
            InlineKeyboardButton(
                text="📆 In 2 weeks",
                callback_data="deadline:quick:2w"
            ),
        ],
        # Row 4: No deadline / Custom
        [
            InlineKeyboardButton(
                text="✏️ Custom (type date)",
                callback_data="deadline:custom"
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ No deadline",
                callback_data="deadline:skip"
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def parse_quick_deadline(quick_code: str) -> datetime:
    """
    Parse quick deadline code to datetime

    Args:
        quick_code: Quick code like "1h", "3d", "1w"

    Returns:
        datetime: Calculated deadline (timezone-aware UTC)
    """
    now = datetime.now(timezone.utc)

    if quick_code.endswith('h'):
        # Hours
        hours = int(quick_code[:-1])
        return now + timedelta(hours=hours)

    elif quick_code.endswith('d'):
        # Days (at 12:00)
        days = int(quick_code[:-1])
        return (now + timedelta(days=days)).replace(hour=12, minute=0, second=0, microsecond=0)

    elif quick_code.endswith('w'):
        # Weeks (at 12:00)
        weeks = int(quick_code[:-1])
        return (now + timedelta(weeks=weeks)).replace(hour=12, minute=0, second=0, microsecond=0)

    return now
