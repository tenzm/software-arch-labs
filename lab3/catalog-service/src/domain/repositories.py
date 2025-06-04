from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Service, ServiceCategory


class ServiceRepository(ABC):
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Service]:
        pass
    
    @abstractmethod
    async def get_by_id(self, service_id: str) -> Optional[Service]:
        pass
    
    @abstractmethod
    async def create(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    async def update(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    async def delete(self, service_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_by_category_id(self, category_id: str) -> List[Service]:
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str) -> List[Service]:
        pass


class ServiceCategoryRepository(ABC):
    
    @abstractmethod
    async def get_all(self) -> List[ServiceCategory]:
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[ServiceCategory]:
        pass
    
    @abstractmethod
    async def create(self, category: ServiceCategory) -> ServiceCategory:
        pass
    
    @abstractmethod
    async def update(self, category: ServiceCategory) -> ServiceCategory:
        pass
    
    @abstractmethod
    async def delete(self, category_id: str) -> bool:
        pass 