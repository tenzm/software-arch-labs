from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from ..domain.entities import Service, ServiceStatus


class ServiceResponse(BaseModel):
    """Модель ответа для услуги"""
    id: str
    title: str
    description: str
    category: str
    price_from: float
    price_to: Optional[float] = None
    currency: str = "RUB"
    status: ServiceStatus
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True

    @classmethod
    def from_domain(cls, service: Service) -> 'ServiceResponse':
        """Создать DTO из доменной модели"""
        return cls(
            id=service.id,
            title=service.title,
            description=service.description,
            category=service.category,
            price_from=service.price_from,
            price_to=service.price_to,
            currency=service.currency,
            status=service.status,
            tags=service.tags,
            created_at=service.created_at,
            updated_at=service.updated_at
        )


class ServiceCreateRequest(BaseModel):
    """Модель запроса для создания услуги"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=100)
    price_from: float = Field(..., gt=0)
    price_to: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="RUB", pattern=r"^[A-Z]{3}$")
    status: Optional[ServiceStatus] = ServiceStatus.ACTIVE
    tags: List[str] = Field(default_factory=list)
    
    def to_domain(self) -> Service:
        """Конвертировать в доменную модель"""
        return Service(
            title=self.title,
            description=self.description,
            category=self.category,
            price_from=self.price_from,
            price_to=self.price_to,
            currency=self.currency,
            status=self.status,
            tags=self.tags
        )


class ServiceUpdateRequest(BaseModel):
    """Модель запроса для обновления услуги"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price_from: Optional[float] = Field(None, gt=0)
    price_to: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    status: Optional[ServiceStatus] = None
    tags: Optional[List[str]] = None

    def apply_to_domain(self, service: Service):
        """Применить изменения к доменной модели"""
        if self.title is not None:
            service.title = self.title
        if self.description is not None:
            service.description = self.description
        if self.category is not None:
            service.category = self.category
        if self.price_from is not None:
            service.price_from = self.price_from
        if self.price_to is not None:
            service.price_to = self.price_to
        if self.currency is not None:
            service.currency = self.currency
        if self.status is not None:
            service.status = self.status
        if self.tags is not None:
            service.tags = self.tags


class ServicesListResponse(BaseModel):
    """Модель ответа для списка услуг"""
    services: List[ServiceResponse]
    total: int
    
    @classmethod
    def from_services(cls, services: List[Service]) -> 'ServicesListResponse':
        """Создать DTO из списка доменных моделей"""
        return cls(
            services=[ServiceResponse.from_domain(service) for service in services],
            total=len(services)
        )


class MessageResponse(BaseModel):
    """Модель ответа с сообщением"""
    message: str 