from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    """States for adding a task"""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_category = State()


class EditTaskStates(StatesGroup):
    """States for editing a task"""
    waiting_for_field = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_category = State()


class AddCategoryStates(StatesGroup):
    """States for adding a category"""
    waiting_for_name = State()