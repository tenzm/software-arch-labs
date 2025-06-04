from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


@dataclass
class ServiceCategory:
    """Категория услуг"""
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Service:
    """Услуга"""
    id: Optional[str] = None
    category_id: str = ""
    name: str = ""
    description: str = ""
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.created_at = datetime.utcnow() 