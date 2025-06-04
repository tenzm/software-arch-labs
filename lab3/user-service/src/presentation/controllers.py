from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from .models import (
    CreateUserRequest, LoginRequest, UpdateUserRequest, ChangePasswordRequest,
    UserResponse, TokenResponse, MessageResponse, ErrorResponse, PaginatedUsersResponse
)
from .dependencies import (
    get_user_use_cases, get_jwt_service, get_current_user, 
    get_current_active_user, get_admin_user
)
from ..use_cases.user_use_cases import UserUseCases
from ..infrastructure.auth import JWTService
from ..domain.entities import User, UserRole
from ..domain.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, 
    InvalidCredentialsError, ValidationError, AccessDeniedError
)

router = APIRouter()


def create_user_response(user: User) -> UserResponse:
    """Создать response модель из доменной сущности"""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["authentication"])
async def login(
    request: LoginRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    """Аутентификация пользователя и получение JWT токена"""
    try:
        user = await user_use_cases.authenticate_user(request.username, request.password)
        access_token = jwt_service.create_access_token(user)
        
        return TokenResponse(access_token=access_token)
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(
    request: CreateUserRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Создать нового пользователя"""
    try:
        user = await user_use_cases.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        return create_user_response(user)
        
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/users/me", response_model=UserResponse, tags=["users"])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Получить информацию о текущем пользователе"""
    return create_user_response(current_user)


@router.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def get_user_by_id(
    user_id: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_active_user)
):
    """Получить пользователя по ID"""
    try:
        # Пользователь может смотреть только свой профиль, админ - любой
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        user = await user_use_cases.get_user_by_id(user_id)
        return create_user_response(user)
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/users", response_model=PaginatedUsersResponse, tags=["users"])
async def get_users(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    name: str = Query(default=None, description="Search by name"),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_admin_user)  # Только админ может просматривать всех пользователей
):
    """Получить список пользователей (только для админа)"""
    try:
        if name:
            users = await user_use_cases.search_users_by_name(name)
            # Применяем пагинацию к результатам поиска
            paginated_users = users[offset:offset + limit]
            total = len(users)
        else:
            users = await user_use_cases.get_all_users(limit, offset)
            paginated_users = users
            # Для простоты считаем total как количество возвращенных записей
            # В реальном приложении нужно делать отдельный запрос для подсчета
            total = len(users)
        
        user_responses = [create_user_response(user) for user in paginated_users]
        
        return PaginatedUsersResponse(
            users=user_responses,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.put("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить информацию о пользователе"""
    try:
        # Пользователь может редактировать только себя, админ - любого
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        user = await user_use_cases.update_user(
            user_id=user_id,
            full_name=request.full_name,
            email=request.email,
            is_active=request.is_active
        )
        
        return create_user_response(user)
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/users/me/change-password", response_model=MessageResponse, tags=["users"])
async def change_password(
    request: ChangePasswordRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_active_user)
):
    """Изменить пароль текущего пользователя"""
    try:
        await user_use_cases.change_password(
            user_id=current_user.id,
            old_password=request.old_password,
            new_password=request.new_password
        )
        
        return MessageResponse(message="Password changed successfully")
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.delete("/users/{user_id}", response_model=MessageResponse, tags=["users"])
async def delete_user(
    user_id: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_admin_user)  # Только админ может удалять пользователей
):
    """Удалить пользователя (только для админа)"""
    try:
        # Админ не может удалить себя
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = await user_use_cases.delete_user(user_id)
        
        if success:
            return MessageResponse(message="User deleted successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) 