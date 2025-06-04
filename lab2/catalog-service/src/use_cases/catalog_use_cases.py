from typing import List, Optional
from ..domain.entities import Service, Category
from ..domain.repositories import ServiceRepository, CategoryRepository


class CatalogService:
    
    def __init__(self, service_repository: ServiceRepository, category_repository: CategoryRepository):
        self._service_repository = service_repository
        self._category_repository = category_repository
    
    # Services
    async def get_all_services(self) -> List[Service]:
        return await self._service_repository.get_all()
    
    async def get_service_by_id(self, service_id: str) -> Optional[Service]:
        return await self._service_repository.get_by_id(service_id)
    
    async def create_service(self, service: Service) -> Service:
        return await self._service_repository.create(service)
    
    async def update_service(self, service: Service) -> Service:
        return await self._service_repository.update(service)
    
    async def delete_service(self, service_id: str) -> bool:
        return await self._service_repository.delete(service_id)
    
    async def get_services_by_category(self, category: str) -> List[Service]:
        return await self._service_repository.get_by_category(category)
    
    # Categories
    async def get_all_categories(self) -> List[Category]:
        return await self._category_repository.get_all()
    
    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        return await self._category_repository.get_by_id(category_id)
    
    async def create_category(self, category: Category) -> Category:
        return await self._category_repository.create(category)
    
    async def update_category(self, category: Category) -> Category:
        return await self._category_repository.update(category)
    
    async def delete_category(self, category_id: str) -> bool:
        return await self._category_repository.delete(category_id) 