from typing import Optional, List
from bot.backend.base import IBackendAPI
from bot.dto import TaskDTO, CategoryDTO
from bot.dto.paginated import PaginatedResponse
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for all task operations"""
    
    def __init__(self, backend: IBackendAPI):
        self.backend = backend
    
    async def get_tasks(
        self,
        telegram_id: int,
        is_completed: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[TaskDTO]:
        """Get user's tasks with pagination"""
        return await self.backend.get_tasks(telegram_id, is_completed, page, page_size)
    
    async def get_task(
        self,
        telegram_id: int,
        task_id: str
    ) -> Optional[TaskDTO]:
        """Get single task"""
        return await self.backend.get_task(telegram_id, task_id)
    
    async def create_task(
        self,
        telegram_id: int,
        title: str,
        description: str = "",
        category_id: Optional[str] = None,
        deadline: Optional[str] = None
    ) -> TaskDTO:
        """Create new task"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        return await self.backend.create_task(
            telegram_id=telegram_id,
            title=title.strip(),
            description=description.strip(),
            category_id=category_id,
            deadline=deadline
        )
    
    async def delete_task(
        self,
        telegram_id: int,
        task_id: str
    ) -> None:
        """Delete task"""
        await self.backend.delete_task(telegram_id, task_id)
    
    async def update_title(
        self,
        telegram_id: int,
        task_id: str,
        title: str
    ) -> TaskDTO:
        """Update task title"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        return await self.backend.update_task(
            telegram_id=telegram_id,
            task_id=task_id,
            title=title.strip()
        )
    
    async def update_description(
        self,
        telegram_id: int,
        task_id: str,
        description: Optional[str]
    ) -> TaskDTO:
        """Update task description"""
        return await self.backend.update_task(
            telegram_id=telegram_id,
            task_id=task_id,
            description=description or ""
        )
    
    async def update_category(
        self,
        telegram_id: int,
        task_id: str,
        category_id: Optional[str]
    ) -> TaskDTO:
        """Update task category"""
        return await self.backend.update_task(
            telegram_id=telegram_id,
            task_id=task_id,
            category=category_id
        )

    async def update_deadline(
        self,
        telegram_id: int,
        task_id: str,
        deadline: Optional[str],
    ) -> TaskDTO:
        """Update task deadline"""
        return await self.backend.update_task(
            telegram_id=telegram_id,
            task_id=task_id,
            deadline=deadline
        )

    async def toggle_completion(
        self,
        telegram_id: int,
        task_id: str,
        is_completed: bool = True
    ) -> TaskDTO:
        """Toggle task completion"""
        return await self.backend.update_task(
            telegram_id=telegram_id,
            task_id=task_id,
            is_completed=is_completed
        )
    
    async def get_categories(self, telegram_id: int) -> List[CategoryDTO]:
        """Get user's categories"""
        return await self.backend.get_categories(telegram_id)
    
    async def create_category(
        self,
        telegram_id: int,
        name: str
    ) -> CategoryDTO:
        """Create new category"""
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
        
        return await self.backend.create_category(
            telegram_id=telegram_id,
            name=name.strip()
        )