"""Зависимости для слоя представления"""

from functools import lru_cache
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.database import Database

from ..infrastructure.repositories import MongoServiceRepository, MongoServiceCategoryRepository
from ..infrastructure.database import get_database
from ..infrastructure.auth import JWTService, JWTConfig, AuthenticatedUser, UserRole
from ..use_cases.catalog_use_cases import CatalogService

# Singleton JWT service
_jwt_config = JWTConfig()
_jwt_service = JWTService(_jwt_config)

# HTTP Bearer scheme для JWT
security = HTTPBearer()

def get_catalog_service(
    database: Database = Depends(get_database)
) -> CatalogService:
    """Получить экземпляр CatalogService с MongoDB репозиториями"""
    service_repository = MongoServiceRepository(database)
    category_repository = MongoServiceCategoryRepository(database)
    return CatalogService(service_repository, category_repository)

def get_jwt_service() -> JWTService:
    """Получить экземпляр JWTService"""
    return _jwt_service

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> AuthenticatedUser:
    """Получить текущего аутентифицированного пользователя"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Проверяем токен локально
        user = jwt_service.get_authenticated_user(credentials.credentials)
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception:
        raise credentials_exception

async def get_current_active_user(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """Получить текущего активного пользователя"""
    # В данном случае все пользователи считаются активными
    # так как проверка активности происходит в user-service
    return current_user

async def get_admin_user(
    current_user: AuthenticatedUser = Depends(get_current_active_user)
) -> AuthenticatedUser:
    """Получить текущего пользователя с правами администратора"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Administrator role required."
        )
    return current_user 