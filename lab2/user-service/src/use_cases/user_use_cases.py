from typing import Optional, List
import uuid
from datetime import datetime
import bcrypt

from ..domain.entities import User, UserRole, UserProfile
from ..domain.repositories import UserRepository, UserProfileRepository
from ..domain.exceptions import (
    UserNotFoundError, 
    UserAlreadyExistsError, 
    InvalidCredentialsError,
    ValidationError
)


class UserUseCases:
    """Use Cases для управления пользователями"""
    
    def __init__(
        self, 
        user_repository: UserRepository,
        user_profile_repository: UserProfileRepository
    ):
        self._user_repository = user_repository
        self._user_profile_repository = user_profile_repository
    
    async def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        full_name: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """Создать нового пользователя"""
        # Проверяем, что пользователь не существует
        existing_user = await self._user_repository.get_by_username(username)
        if existing_user:
            raise UserAlreadyExistsError(f"User with username '{username}' already exists")
        
        existing_email = await self._user_repository.get_by_email(email)
        if existing_email:
            raise UserAlreadyExistsError(f"User with email '{email}' already exists")
        
        # Валидация
        if not username or not email or not password:
            raise ValidationError("Username, email and password are required")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Хэширование пароля
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Создание пользователя
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self._user_repository.create(user)
    
    async def authenticate_user(self, username: str, password: str) -> User:
        """Аутентификация пользователя"""
        user = await self._user_repository.get_by_username(username)
        if not user:
            raise InvalidCredentialsError("Invalid username or password")
        
        if not user.is_active:
            raise InvalidCredentialsError("User account is deactivated")
        
        # Проверка пароля
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            raise InvalidCredentialsError("Invalid username or password")
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> User:
        """Получить пользователя по ID"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{user_id}' not found")
        
        return user
    
    async def get_user_by_username(self, username: str) -> User:
        """Получить пользователя по имени пользователя"""
        user = await self._user_repository.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"User with username '{username}' not found")
        
        return user
    
    async def search_users_by_name(self, name: str) -> List[User]:
        """Поиск пользователей по имени"""
        if not name or len(name.strip()) < 2:
            raise ValidationError("Search name must be at least 2 characters long")
        
        return await self._user_repository.search_by_name(name.strip())
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValidationError("Offset must be non-negative")
        
        return await self._user_repository.get_all(limit, offset)
    
    async def update_user(
        self, 
        user_id: str, 
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> User:
        """Обновить информацию о пользователе"""
        user = await self.get_user_by_id(user_id)
        
        # Проверка email на уникальность
        if email and email != user.email:
            existing_email = await self._user_repository.get_by_email(email)
            if existing_email:
                raise UserAlreadyExistsError(f"User with email '{email}' already exists")
            user.email = email
        
        if full_name is not None:
            user.full_name = full_name
        
        if is_active is not None:
            user.is_active = is_active
        
        user.updated_at = datetime.utcnow()
        
        return await self._user_repository.update(user)
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Изменить пароль пользователя"""
        user = await self.get_user_by_id(user_id)
        
        # Проверка старого пароля
        if not bcrypt.checkpw(old_password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            raise InvalidCredentialsError("Invalid current password")
        
        if len(new_password) < 6:
            raise ValidationError("New password must be at least 6 characters long")
        
        # Хэширование нового пароля
        user.hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.updated_at = datetime.utcnow()
        
        await self._user_repository.update(user)
        return True
    
    async def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя"""
        user = await self.get_user_by_id(user_id)
        
        # Удаляем профиль пользователя, если он есть
        await self._user_profile_repository.delete(user_id)
        
        return await self._user_repository.delete(user_id) 