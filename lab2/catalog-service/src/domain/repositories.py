from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Service, Category


class ServiceRepository(ABC):
    
    @abstractmethod
    async def get_all(self) -> List[Service]:
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
    async def get_by_category(self, category: str) -> List[Service]:
        pass


class CategoryRepository(ABC):
    
    @abstractmethod
    async def get_all(self) -> List[Category]:
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        pass
    
    @abstractmethod
    async def create(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    async def update(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    async def delete(self, category_id: str) -> bool:
        pass 