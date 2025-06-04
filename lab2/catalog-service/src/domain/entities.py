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
class Service:
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    category: str = ""
    price_from: float = 0.0
    price_to: Optional[float] = None
    currency: str = "RUB"
    status: ServiceStatus = ServiceStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
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
class Category:
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    parent_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow() 