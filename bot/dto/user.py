from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDTO:
    """User data transfer object"""
    id: str
    telegram_id: int
    username: str
    first_name: str
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserDTO':
        return cls(
            id=data['id'],
            telegram_id=data['telegram_id'],
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> dict:
        return {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name
        }