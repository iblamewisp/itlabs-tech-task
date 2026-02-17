from typing import List, Optional
import logging
from .base import IBackendAPI
from bot.dto import UserDTO, TaskDTO, CategoryDTO
from bot.dto.paginated import PaginatedResponse
from bot.clients.http_client import HTTPClient

logger = logging.getLogger(__name__)


class DjangoBackend(IBackendAPI):
    """Django REST API backend implementation"""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip('/')
        self._headers = {'X-Internal-Key': api_key} if api_key else {}

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None
    ) -> Optional[dict]:
        """Make request to Django API"""
        url = f"{self.base_url}/{endpoint}"
        return await HTTPClient.request(method, url, params=params, json=json, headers=self._headers or None)
    
    # User operations
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str
    ) -> UserDTO:
        """Get or create user"""
        try:
            users = await self._request(
                'GET',
                'users/',
                params={'telegram_id': telegram_id}
            )

            if users:
                # Handle Django REST pagination format
                if isinstance(users, dict) and 'results' in users:
                    users = users['results']

                if isinstance(users, list) and len(users) > 0:
                    return UserDTO.from_dict(users[0])
        except Exception:
            pass

        data = await self._request(
            'POST',
            'users/',
            json={
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name
            }
        )

        return UserDTO.from_dict(data)
    
    # Task operations
    
    async def get_tasks(
        self,
        telegram_id: int,
        is_completed: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[TaskDTO]:
        """Get user's tasks with pagination"""
        params = {
            'telegram_id': telegram_id,
            'page': page,
            'page_size': page_size
        }

        if is_completed is not None:
            params['is_completed'] = str(is_completed).lower()

        result = await self._request('GET', 'tasks/', params=params)

        if not result:
            return PaginatedResponse(items=[], total=0, page=page, page_size=page_size)

        # Handle Django REST pagination format {"count": N, "results": [...]}
        if isinstance(result, dict) and 'results' in result:
            tasks = [TaskDTO.from_dict(task) for task in result['results']]
            total = result.get('count', len(tasks))
            return PaginatedResponse(items=tasks, total=total, page=page, page_size=page_size)

        # Fallback for non-paginated response
        tasks = [TaskDTO.from_dict(task) for task in result]
        return PaginatedResponse(items=tasks, total=len(tasks), page=page, page_size=page_size)
    
    async def get_task(
        self,
        telegram_id: int,
        task_id: str
    ) -> Optional[TaskDTO]:
        """Get single task"""
        data = await self._request(
            'GET',
            f'tasks/{task_id}/',
            params={'telegram_id': telegram_id}
        )
        
        return TaskDTO.from_dict(data) if data else None
    
    async def create_task(
        self,
        telegram_id: int,
        title: str,
        description: str = "",
        category_id: Optional[str] = None,
        deadline: Optional[str] = None
    ) -> TaskDTO:
        """Create new task"""
        payload = {
            'title': title,
            'description': description
        }
        
        if category_id:
            payload['category'] = category_id
        
        if deadline:
            payload['deadline'] = deadline
        
        data = await self._request(
            'POST',
            'tasks/',
            params={'telegram_id': telegram_id},
            json=payload
        )
        
        return TaskDTO.from_dict(data)
    
    async def update_task(
        self,
        telegram_id: int,
        task_id: str,
        **kwargs
    ) -> TaskDTO:
        """Update task"""
        data = await self._request(
            'PATCH',
            f'tasks/{task_id}/',
            params={'telegram_id': telegram_id},
            json=kwargs
        )
        
        return TaskDTO.from_dict(data)
    
    async def delete_task(
        self,
        telegram_id: int,
        task_id: str
    ) -> None:
        """Delete task"""
        await self._request(
            'DELETE',
            f'tasks/{task_id}/',
            params={'telegram_id': telegram_id}
        )
    
    # Category operations
    
    async def get_categories(
        self,
        telegram_id: int
    ) -> List[CategoryDTO]:
        """Get user's categories"""
        result = await self._request(
            'GET',
            'categories/',
            params={'telegram_id': telegram_id}
        )

        if not result:
            return []

        # Handle Django REST pagination format {"count": N, "results": [...]}
        if isinstance(result, dict) and 'results' in result:
            result = result['results']

        # Handle case where result is a single dict instead of list
        if isinstance(result, dict):
            return [CategoryDTO.from_dict(result)]

        return [CategoryDTO.from_dict(cat) for cat in result]
    
    async def create_category(
        self,
        telegram_id: int,
        name: str
    ) -> CategoryDTO:
        """Create new category"""
        data = await self._request(
            'POST',
            'categories/',
            params={'telegram_id': telegram_id},
            json={'name': name}
        )
        
        return CategoryDTO.from_dict(data)