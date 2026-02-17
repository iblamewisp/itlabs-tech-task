from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoryDTO:
    """Category data transfer object"""
    id: str
    name: str
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CategoryDTO':
        return cls(
            id=data['id'],
            name=data['name'],
            created_at=data.get('created_at')
        )