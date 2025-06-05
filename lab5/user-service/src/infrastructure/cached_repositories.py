from typing import Optional, List
from ..domain.entities import User, UserProfile
from ..repository.interfaces import UserRepository, UserProfileRepository
from .redis_client import RedisClient
from .repositories import SQLAlchemyUserRepository, SQLAlchemyUserProfileRepository


class CachedUserRepository(UserRepository):
    """Кеширующий репозиторий пользователей с паттернами read-through и write-through"""
    
    def __init__(self, db_repository: SQLAlchemyUserRepository, redis_client: RedisClient):
        self.db_repository = db_repository
        self.redis_client = redis_client
        self.cache_ttl = 3600  # TTL для кеша - 1 час
    
    def _get_user_cache_key(self, identifier: str, field: str = "id") -> str:
        """Генерация ключа кеша для пользователя"""
        return f"user:{field}:{identifier}"
    
    def _get_users_list_cache_key(self, limit: int, offset: int) -> str:
        """Генерация ключа кеша для списка пользователей"""
        return f"users:list:{limit}:{offset}"
    
    def _get_search_cache_key(self, name: str) -> str:
        """Генерация ключа кеша для поиска"""
        return f"users:search:{name}"
    
    async def _user_to_dict(self, user: User) -> dict:
        """Преобразование User в словарь для кеширования"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    
    async def _dict_to_user(self, data: dict) -> User:
        """Преобразование словаря в User"""
        from datetime import datetime
        from ..domain.entities import UserRole
        
        return User(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            hashed_password=data["hashed_password"],
            role=UserRole(data["role"]),
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"]) if data["created_at"] else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else None,
        )
    
    async def _cache_user(self, user: User):
        """Кеширование пользователя по всем ключам"""
        user_dict = await self._user_to_dict(user)
        
        # Кешируем по ID, username и email
        await self.redis_client.set_json(
            self._get_user_cache_key(user.id, "id"), 
            user_dict, 
            self.cache_ttl
        )
        await self.redis_client.set_json(
            self._get_user_cache_key(user.username, "username"), 
            user_dict, 
            self.cache_ttl
        )
        await self.redis_client.set_json(
            self._get_user_cache_key(user.email, "email"), 
            user_dict, 
            self.cache_ttl
        )
    
    async def _invalidate_user_cache(self, user: User):
        """Инвалидация кеша пользователя"""
        await self.redis_client.delete(self._get_user_cache_key(user.id, "id"))
        await self.redis_client.delete(self._get_user_cache_key(user.username, "username"))
        await self.redis_client.delete(self._get_user_cache_key(user.email, "email"))
        
        # Также инвалидируем списки и поиск
        await self.redis_client.clear_pattern("users:list:*")
        await self.redis_client.clear_pattern("users:search:*")
    
    async def create(self, user: User) -> User:
        """Создать пользователя (write-through)"""
        # Сначала записываем в БД
        created_user = await self.db_repository.create(user)
        
        # Затем кешируем результат
        await self._cache_user(created_user)
        
        # Инвалидируем списки и поиски
        await self.redis_client.clear_pattern("users:list:*")
        await self.redis_client.clear_pattern("users:search:*")
        
        return created_user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID (read-through)"""
        cache_key = self._get_user_cache_key(user_id, "id")
        
        # Сначала проверяем кеш
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data:
            return await self._dict_to_user(cached_data)
        
        # Если в кеше нет, получаем из БД
        user = await self.db_repository.get_by_id(user_id)
        if user:
            # Кешируем полученного пользователя
            await self._cache_user(user)
        
        return user
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username (read-through)"""
        cache_key = self._get_user_cache_key(username, "username")
        
        # Сначала проверяем кеш
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data:
            return await self._dict_to_user(cached_data)
        
        # Если в кеше нет, получаем из БД
        user = await self.db_repository.get_by_username(username)
        if user:
            # Кешируем полученного пользователя
            await self._cache_user(user)
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email (read-through)"""
        cache_key = self._get_user_cache_key(email, "email")
        
        # Сначала проверяем кеш
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data:
            return await self._dict_to_user(cached_data)
        
        # Если в кеше нет, получаем из БД
        user = await self.db_repository.get_by_email(email)
        if user:
            # Кешируем полученного пользователя
            await self._cache_user(user)
        
        return user
    
    async def search_by_name(self, name: str) -> List[User]:
        """Поиск пользователей по имени (read-through)"""
        cache_key = self._get_search_cache_key(name)
        
        # Проверяем кеш
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data:
            users = []
            for user_data in cached_data:
                users.append(await self._dict_to_user(user_data))
            return users
        
        # Если в кеше нет, получаем из БД
        users = await self.db_repository.search_by_name(name)
        
        # Кешируем результат поиска
        if users:
            users_data = []
            for user in users:
                users_data.append(await self._user_to_dict(user))
            await self.redis_client.set_json(cache_key, users_data, self.cache_ttl)
        
        return users
    
    async def update(self, user: User) -> User:
        """Обновить пользователя (write-through)"""
        # Сначала получаем старые данные для инвалидации кеша
        old_user = await self.db_repository.get_by_id(user.id)
        
        # Обновляем в БД
        updated_user = await self.db_repository.update(user)
        
        # Инвалидируем старый кеш
        if old_user:
            await self._invalidate_user_cache(old_user)
        
        # Кешируем новые данные
        await self._cache_user(updated_user)
        
        return updated_user
    
    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя (write-through)"""
        # Сначала получаем пользователя для инвалидации кеша
        user = await self.db_repository.get_by_id(user_id)
        
        # Удаляем из БД
        result = await self.db_repository.delete(user_id)
        
        # Инвалидируем кеш
        if user and result:
            await self._invalidate_user_cache(user)
        
        return result
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить всех пользователей с пагинацией (read-through)"""
        cache_key = self._get_users_list_cache_key(limit, offset)
        
        # Проверяем кеш
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data:
            users = []
            for user_data in cached_data:
                users.append(await self._dict_to_user(user_data))
            return users
        
        # Если в кеше нет, получаем из БД
        users = await self.db_repository.get_all(limit, offset)
        
        # Кешируем результат
        if users:
            users_data = []
            for user in users:
                users_data.append(await self._user_to_dict(user))
            await self.redis_client.set_json(cache_key, users_data, self.cache_ttl)
        
        return users


class CachedUserProfileRepository(UserProfileRepository):
    """Кеширующий репозиторий профилей пользователей"""
    
    def __init__(self, db_repository: SQLAlchemyUserProfileRepository, redis_client: RedisClient):
        self.db_repository = db_repository
        self.redis_client = redis_client
        self.cache_ttl = 3600  # TTL для кеша - 1 час
    
    def _get_profile_cache_key(self, user_id: str) -> str:
        """Генерация ключа кеша для профиля"""
        return f"profile:user:{user_id}"
    
    async def _profile_to_dict(self, profile: UserProfile) -> dict:
        """Преобразование UserProfile в словарь"""
        return {
            "user_id": profile.user_id,
            "phone": profile.phone,
            "address": profile.address,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "skills": profile.skills,
            "rating": profile.rating,
            "reviews_count": profile.reviews_count,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }
    
    async def _dict_to_profile(self, data: dict) -> UserProfile:
        """Преобразование словаря в UserProfile"""
        from datetime import datetime
        
        return UserProfile(
            user_id=data["user_id"],
            phone=data["phone"],
            address=data["address"],
            bio=data["bio"],
            avatar_url=data["avatar_url"],
            skills=data["skills"],
            rating=data["rating"],
            reviews_count=data["reviews_count"],
            created_at=datetime.fromisoformat(data["created_at"]) if data["created_at"] else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else None,
        )
    
    async def create(self, profile: UserProfile) -> UserProfile:
        """Создать профиль (write-through)"""
        created_profile = await self.db_repository.create(profile)
        
        # Кешируем созданный профиль
        cache_key = self._get_profile_cache_key(created_profile.user_id)
        profile_dict = await self._profile_to_dict(created_profile)
        await self.redis_client.set_json(cache_key, profile_dict, self.cache_ttl)
        
        return created_profile
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Получить профиль по ID пользователя (read-through)"""
        cache_key = self._get_profile_cache_key(user_id)
        
        # Проверяем кеш
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data:
            return await self._dict_to_profile(cached_data)
        
        # Если в кеше нет, получаем из БД
        profile = await self.db_repository.get_by_user_id(user_id)
        if profile:
            # Кешируем профиль
            profile_dict = await self._profile_to_dict(profile)
            await self.redis_client.set_json(cache_key, profile_dict, self.cache_ttl)
        
        return profile
    
    async def update(self, profile: UserProfile) -> UserProfile:
        """Обновить профиль (write-through)"""
        updated_profile = await self.db_repository.update(profile)
        
        # Обновляем кеш
        cache_key = self._get_profile_cache_key(updated_profile.user_id)
        profile_dict = await self._profile_to_dict(updated_profile)
        await self.redis_client.set_json(cache_key, profile_dict, self.cache_ttl)
        
        return updated_profile
    
    async def delete(self, user_id: str) -> bool:
        """Удалить профиль (write-through)"""
        result = await self.db_repository.delete(user_id)
        
        # Удаляем из кеша
        if result:
            cache_key = self._get_profile_cache_key(user_id)
            await self.redis_client.delete(cache_key)
        
        return result 