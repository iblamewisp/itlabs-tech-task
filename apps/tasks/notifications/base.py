from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    """Abstract notification channel"""
    
    @abstractmethod
    def send(self, recipient_id: int, message: str) -> bool:
        """Send notification"""
        pass