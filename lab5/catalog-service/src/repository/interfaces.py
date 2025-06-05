from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.entities import Service, ServiceCategory


class ServiceRepository(ABC):
    """Интерфейс репозитория для управления услугами"""
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Service]:
        """Получить все услуги с пагинацией"""
        pass
    
    @abstractmethod
    async def get_by_id(self, service_id: str) -> Optional[Service]:
        """Получить услугу по ID"""
        pass
    
    @abstractmethod
    async def create(self, service: Service) -> Service:
        """Создать новую услугу"""
        pass
    
    @abstractmethod
    async def update(self, service: Service) -> Service:
        """Обновить существующую услугу"""
        pass
    
    @abstractmethod
    async def delete(self, service_id: str) -> bool:
        """Удалить услугу"""
        pass
    
    @abstractmethod
    async def get_by_category_id(self, category_id: str) -> List[Service]:
        """Получить услуги по ID категории"""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str) -> List[Service]:
        """Поиск услуг по названию"""
        pass


class ServiceCategoryRepository(ABC):
    """Интерфейс репозитория для управления категориями услуг"""
    
    @abstractmethod
    async def get_all(self) -> List[ServiceCategory]:
        """Получить все категории"""
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[ServiceCategory]:
        """Получить категорию по ID"""
        pass
    
    @abstractmethod
    async def create(self, category: ServiceCategory) -> ServiceCategory:
        """Создать новую категорию"""
        pass
    
    @abstractmethod
    async def update(self, category: ServiceCategory) -> ServiceCategory:
        """Обновить существующую категорию"""
        pass
    
    @abstractmethod
    async def delete(self, category_id: str) -> bool:
        """Удалить категорию"""
        pass 