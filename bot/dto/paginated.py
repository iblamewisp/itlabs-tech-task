from dataclasses import dataclass
from typing import List, TypeVar, Generic

T = TypeVar('T')


@dataclass
class PaginatedResponse(Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        if self.total == 0:
            return 1
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1
