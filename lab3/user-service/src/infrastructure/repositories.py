from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import User, UserProfile, UserRole
from ..domain.repositories import UserRepository, UserProfileRepository
from .models import UserModel, UserProfileModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy реализация репозитория пользователей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password_hash=user.hashed_password,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active
        )
        
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return self._model_to_entity(db_user)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        stmt = select(UserModel).where(UserModel.id == UUID(user_id))
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return self._model_to_entity(db_user)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return self._model_to_entity(db_user)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return self._model_to_entity(db_user)
        return None
    
    async def search_by_name(self, name: str) -> List[User]:
        """Поиск пользователей по имени"""
        stmt = select(UserModel).where(
            or_(
                UserModel.username.ilike(f"%{name}%"),
                UserModel.full_name.ilike(f"%{name}%")
            )
        ).limit(50)  # Ограничиваем результаты поиска
        
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        
        return [self._model_to_entity(db_user) for db_user in db_users]
    
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        stmt = select(UserModel).where(UserModel.id == UUID(user.id))
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with id {user.id} not found")
        
        # Обновляем поля
        db_user.username = user.username
        db_user.email = user.email
        db_user.password_hash = user.hashed_password
        db_user.full_name = user.full_name
        db_user.role = user.role.value
        db_user.is_active = user.is_active
        
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return self._model_to_entity(db_user)
    
    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя"""
        stmt = select(UserModel).where(UserModel.id == UUID(user_id))
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return False
        
        await self.session.delete(db_user)
        await self.session.commit()
        return True
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        stmt = select(UserModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        
        return [self._model_to_entity(db_user) for db_user in db_users]
    
    def _model_to_entity(self, db_user: UserModel) -> User:
        """Преобразование модели SQLAlchemy в доменную сущность"""
        return User(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            hashed_password=db_user.password_hash,
            role=UserRole(db_user.role),
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )


class SQLAlchemyUserProfileRepository(UserProfileRepository):
    """SQLAlchemy реализация репозитория профилей пользователей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, profile: UserProfile) -> UserProfile:
        """Создать профиль пользователя"""
        db_profile = UserProfileModel(
            user_id=UUID(profile.user_id),
            phone=profile.phone,
            address=profile.address,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            skills=profile.skills,
            rating=profile.rating,
            reviews_count=profile.reviews_count
        )
        
        self.session.add(db_profile)
        await self.session.commit()
        await self.session.refresh(db_profile)
        
        return self._model_to_entity(db_profile)
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Получить профиль по ID пользователя"""
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == UUID(user_id))
        result = await self.session.execute(stmt)
        db_profile = result.scalar_one_or_none()
        
        if db_profile:
            return self._model_to_entity(db_profile)
        return None
    
    async def update(self, profile: UserProfile) -> UserProfile:
        """Обновить профиль пользователя"""
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == UUID(profile.user_id))
        result = await self.session.execute(stmt)
        db_profile = result.scalar_one_or_none()
        
        if not db_profile:
            raise ValueError(f"Profile for user {profile.user_id} not found")
        
        # Обновляем поля
        db_profile.phone = profile.phone
        db_profile.address = profile.address
        db_profile.bio = profile.bio
        db_profile.avatar_url = profile.avatar_url
        db_profile.skills = profile.skills
        db_profile.rating = profile.rating
        db_profile.reviews_count = profile.reviews_count
        
        await self.session.commit()
        await self.session.refresh(db_profile)
        
        return self._model_to_entity(db_profile)
    
    async def delete(self, user_id: str) -> bool:
        """Удалить профиль пользователя"""
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == UUID(user_id))
        result = await self.session.execute(stmt)
        db_profile = result.scalar_one_or_none()
        
        if not db_profile:
            return False
        
        await self.session.delete(db_profile)
        await self.session.commit()
        return True
    
    def _model_to_entity(self, db_profile: UserProfileModel) -> UserProfile:
        """Преобразование модели SQLAlchemy в доменную сущность"""
        return UserProfile(
            user_id=str(db_profile.user_id),
            phone=db_profile.phone,
            address=db_profile.address,
            bio=db_profile.bio,
            avatar_url=db_profile.avatar_url,
            skills=db_profile.skills or [],
            rating=db_profile.rating,
            reviews_count=db_profile.reviews_count
        ) 