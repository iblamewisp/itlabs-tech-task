# bot/dto/task.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskDTO:
    """Task data transfer object"""
    id: str
    title: str
    description: str
    is_completed: bool
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    deadline: Optional[str] = None
    next_reminder_time: Optional[str] = None
    reminder_level: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaskDTO':
        return cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            is_completed=data.get('is_completed', False),
            category_id=data.get('category'),
            category_name=data.get('category_name'),
            deadline=data.get('deadline'),
            next_reminder_time=data.get('next_reminder_time'),
            reminder_level=data.get('reminder_level'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )