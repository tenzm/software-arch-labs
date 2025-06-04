from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from bson import ObjectId


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
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для MongoDB"""
        data = asdict(self)
        if self.id and ObjectId.is_valid(self.id):
            data['_id'] = ObjectId(self.id)
            del data['id']
        elif data.get('id'):
            del data['id']
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceCategory':
        """Создание объекта из словаря MongoDB"""
        if '_id' in data:
            data['id'] = str(data['_id'])
            del data['_id']
        
        # Конвертация datetime если они пришли как строки
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        return cls(**data)


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
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для MongoDB"""
        data = asdict(self)
        if self.id and ObjectId.is_valid(self.id):
            data['_id'] = ObjectId(self.id)
            del data['id']
        elif data.get('id'):
            del data['id']
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Service':
        """Создание объекта из словаря MongoDB"""
        if '_id' in data:
            data['id'] = str(data['_id'])
            del data['_id']
        
        # Удаляем поле score, которое добавляется при полнотекстовом поиске
        if 'score' in data:
            del data['score']
        
        # Конвертация datetime если они пришли как строки
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        return cls(**data) 