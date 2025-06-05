from typing import Optional, List, Dict
import copy
from datetime import datetime
from uuid import uuid4

from ..domain.entities import User, UserProfile, UserRole
from ..repository.interfaces import UserRepository, UserProfileRepository


class InMemoryUserRepository(UserRepository):
    """Реализация репозитория пользователей в памяти"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._username_index: Dict[str, str] = {}  # username -> user_id
        self._email_index: Dict[str, str] = {}     # email -> user_id
    
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        if user.id in self._users:
            raise ValueError(f"User with id {user.id} already exists")
        
        user_copy = copy.deepcopy(user)
        self._users[user.id] = user_copy
        self._username_index[user.username] = user.id
        self._email_index[user.email] = user.id
        
        return copy.deepcopy(user_copy)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        user = self._users.get(user_id)
        return copy.deepcopy(user) if user else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        user_id = self._username_index.get(username)
        if user_id:
            user = self._users.get(user_id)
            return copy.deepcopy(user) if user else None
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        user_id = self._email_index.get(email)
        if user_id:
            user = self._users.get(user_id)
            return copy.deepcopy(user) if user else None
        return None
    
    async def search_by_name(self, name: str) -> List[User]:
        """Поиск пользователей по имени"""
        name_lower = name.lower()
        results = []
        
        for user in self._users.values():
            if (name_lower in user.full_name.lower() or 
                name_lower in user.username.lower()):
                results.append(copy.deepcopy(user))
        
        return results
    
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        if user.id not in self._users:
            raise ValueError(f"User with id {user.id} not found")
        
        old_user = self._users[user.id]
        
        # Обновляем индексы, если изменились username или email
        if old_user.username != user.username:
            del self._username_index[old_user.username]
            self._username_index[user.username] = user.id
        
        if old_user.email != user.email:
            del self._email_index[old_user.email]
            self._email_index[user.email] = user.id
        
        user_copy = copy.deepcopy(user)
        self._users[user.id] = user_copy
        
        return copy.deepcopy(user_copy)
    
    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя"""
        user = self._users.get(user_id)
        if not user:
            return False
        
        # Удаляем из индексов
        del self._username_index[user.username]
        del self._email_index[user.email]
        del self._users[user_id]
        
        return True
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        users = list(self._users.values())
        users.sort(key=lambda u: u.created_at)  # Сортировка по дате создания
        
        start = offset
        end = offset + limit
        
        return [copy.deepcopy(user) for user in users[start:end]]


class InMemoryUserProfileRepository(UserProfileRepository):
    """Реализация репозитория профилей пользователей в памяти"""
    
    def __init__(self):
        self._profiles: Dict[str, UserProfile] = {}  # user_id -> UserProfile
    
    async def create(self, profile: UserProfile) -> UserProfile:
        """Создать профиль пользователя"""
        if profile.user_id in self._profiles:
            raise ValueError(f"Profile for user {profile.user_id} already exists")
        
        profile_copy = copy.deepcopy(profile)
        self._profiles[profile.user_id] = profile_copy
        
        return copy.deepcopy(profile_copy)
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Получить профиль по ID пользователя"""
        profile = self._profiles.get(user_id)
        return copy.deepcopy(profile) if profile else None
    
    async def update(self, profile: UserProfile) -> UserProfile:
        """Обновить профиль пользователя"""
        if profile.user_id not in self._profiles:
            raise ValueError(f"Profile for user {profile.user_id} not found")
        
        profile_copy = copy.deepcopy(profile)
        self._profiles[profile.user_id] = profile_copy
        
        return copy.deepcopy(profile_copy)
    
    async def delete(self, user_id: str) -> bool:
        """Удалить профиль пользователя"""
        if user_id in self._profiles:
            del self._profiles[user_id]
            return True
        return False 