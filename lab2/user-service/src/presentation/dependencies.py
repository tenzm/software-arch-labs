from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..use_cases.user_use_cases import UserUseCases
from ..infrastructure.memory_repositories import InMemoryUserRepository, InMemoryUserProfileRepository
from ..infrastructure.auth import JWTService, JWTConfig
from ..domain.entities import User, UserRole
from ..domain.exceptions import UserNotFoundError, InvalidCredentialsError

# Глобальные экземпляры (в реальном приложении используйте DI контейнер)
user_repository = InMemoryUserRepository()
user_profile_repository = InMemoryUserProfileRepository()
user_use_cases = UserUseCases(user_repository, user_profile_repository)
jwt_config = JWTConfig()
jwt_service = JWTService(jwt_config)

# HTTP Bearer scheme для JWT
security = HTTPBearer()


def get_user_use_cases() -> UserUseCases:
    """Получить экземпляр UserUseCases"""
    return user_use_cases


def get_jwt_service() -> JWTService:
    """Получить экземпляр JWTService"""
    return jwt_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
) -> User:
    """Получить текущего аутентифицированного пользователя"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Декодируем токен
        payload = jwt_service.decode_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Получаем пользователя из базы данных
        user = await user_use_cases.get_user_by_id(user_id)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        return user
        
    except UserNotFoundError:
        raise credentials_exception
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Получить текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Получить текущего пользователя с правами администратора"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Опциональная аутентификация (для эндпоинтов, где аутентификация не обязательна)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
) -> Optional[User]:
    """Получить текущего пользователя (опционально)"""
    
    if credentials is None:
        return None
    
    try:
        payload = jwt_service.decode_token(credentials.credentials)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = await user_use_cases.get_user_by_id(user_id)
        return user if user.is_active else None
        
    except Exception:
        return None 