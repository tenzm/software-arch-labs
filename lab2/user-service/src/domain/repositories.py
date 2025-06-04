from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import User, UserProfile


class UserRepository(ABC):
    """Абстракция репозитория пользователей"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str) -> List[User]:
        """Поиск пользователей по имени"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        pass


class UserProfileRepository(ABC):
    """Абстракция репозитория профилей пользователей"""
    
    @abstractmethod
    async def create(self, profile: UserProfile) -> UserProfile:
        """Создать профиль пользователя"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Получить профиль по ID пользователя"""
        pass
    
    @abstractmethod
    async def update(self, profile: UserProfile) -> UserProfile:
        """Обновить профиль пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Удалить профиль пользователя"""
        pass 