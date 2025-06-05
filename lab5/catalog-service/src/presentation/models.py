from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from ..domain.entities import Service, ServiceCategory


class ServiceCategoryResponse(BaseModel):
    """Модель ответа для категории услуг"""
    id: str
    name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_domain(cls, category: ServiceCategory) -> "ServiceCategoryResponse":
        """Создать response модель из доменной сущности"""
        return cls(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )


class ServiceResponse(BaseModel):
    """Модель ответа для услуги"""
    id: str
    category_id: str
    name: str
    description: str
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_domain(cls, service: Service) -> "ServiceResponse":
        """Создать response модель из доменной сущности"""
        return cls(
            id=service.id,
            category_id=service.category_id,
            name=service.name,
            description=service.description,
            price_from=service.price_from,
            price_to=service.price_to,
            duration_minutes=service.duration_minutes,
            is_active=service.is_active,
            created_at=service.created_at,
            updated_at=service.updated_at
        )


class ServiceCategoryCreateRequest(BaseModel):
    """Модель запроса для создания категории"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    is_active: bool = True

    def to_domain(self) -> ServiceCategory:
        """Преобразовать в доменную сущность"""
        return ServiceCategory(
            name=self.name,
            description=self.description,
            is_active=self.is_active
        )


class ServiceCreateRequest(BaseModel):
    """Модель запроса для создания услуги"""
    category_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    price_from: Optional[float] = Field(None, gt=0)
    price_to: Optional[float] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: bool = True

    def to_domain(self) -> Service:
        """Преобразовать в доменную сущность"""
        return Service(
            category_id=self.category_id,
            name=self.name,
            description=self.description,
            price_from=self.price_from,
            price_to=self.price_to,
            duration_minutes=self.duration_minutes,
            is_active=self.is_active
        )


class ServiceUpdateRequest(BaseModel):
    """Модель запроса для обновления услуги"""
    category_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price_from: Optional[float] = Field(None, gt=0)
    price_to: Optional[float] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    def apply_to_domain(self, service: Service) -> None:
        """Применить изменения к доменной сущности"""
        if self.category_id is not None:
            service.category_id = self.category_id
        if self.name is not None:
            service.name = self.name
        if self.description is not None:
            service.description = self.description
        if self.price_from is not None:
            service.price_from = self.price_from
        if self.price_to is not None:
            service.price_to = self.price_to
        if self.duration_minutes is not None:
            service.duration_minutes = self.duration_minutes
        if self.is_active is not None:
            service.is_active = self.is_active


class ServiceCategoryUpdateRequest(BaseModel):
    """Модель запроса для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_active: Optional[bool] = None

    def apply_to_domain(self, category: ServiceCategory) -> None:
        """Применить изменения к доменной сущности"""
        if self.name is not None:
            category.name = self.name
        if self.description is not None:
            category.description = self.description
        if self.is_active is not None:
            category.is_active = self.is_active


class ServicesListResponse(BaseModel):
    """Модель ответа для списка услуг"""
    services: List[ServiceResponse]
    total: int
    limit: int
    offset: int


class CategoriesListResponse(BaseModel):
    """Модель ответа для списка категорий"""
    categories: List[ServiceCategoryResponse]
    total: int


class MessageResponse(BaseModel):
    """Модель ответа с сообщением"""
    message: str 