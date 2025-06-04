from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    SPECIALIST = "specialist"


@dataclass
class User:
    """Доменная сущность пользователя"""
    id: Optional[str] = None
    username: str = ""
    email: str = ""
    full_name: str = ""
    hashed_password: str = ""
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class UserProfile:
    """Профиль пользователя с дополнительной информацией"""
    user_id: str
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    rating: float = 0.0
    reviews_count: int = 0 