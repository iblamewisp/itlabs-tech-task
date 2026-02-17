from abc import ABC, abstractmethod
from typing import List, Optional
from bot.dto import UserDTO, TaskDTO, CategoryDTO
from bot.dto.paginated import PaginatedResponse


class IBackendAPI(ABC):
    """Abstract interface for backend API"""
    
    # User operations
    
    @abstractmethod
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str
    ) -> UserDTO:
        """Get or create user"""
        pass
    
    # Task operations
    
    @abstractmethod
    async def get_tasks(
        self,
        telegram_id: int,
        is_completed: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[TaskDTO]:
        """Get user's tasks with pagination"""
        pass
    
    @abstractmethod
    async def get_task(
        self,
        telegram_id: int,
        task_id: str
    ) -> Optional[TaskDTO]:
        """Get single task"""
        pass
    
    @abstractmethod
    async def create_task(
        self,
        telegram_id: int,
        title: str,
        description: str = "",
        category_id: Optional[str] = None,
        deadline: Optional[str] = None
    ) -> TaskDTO:
        """Create new task"""
        pass
    
    @abstractmethod
    async def update_task(
        self,
        telegram_id: int,
        task_id: str,
        **kwargs
    ) -> TaskDTO:
        """Update task"""
        pass
    
    @abstractmethod
    async def delete_task(
        self,
        telegram_id: int,
        task_id: str
    ) -> None:
        """Delete task"""
        pass
    
    # Category operations
    
    @abstractmethod
    async def get_categories(
        self,
        telegram_id: int
    ) -> List[CategoryDTO]:
        """Get user's categories"""
        pass
    
    @abstractmethod
    async def create_category(
        self,
        telegram_id: int,
        name: str
    ) -> CategoryDTO:
        """Create new category"""
        pass