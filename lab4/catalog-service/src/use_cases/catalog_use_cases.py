from typing import List, Optional
from ..repository.interfaces import ServiceRepository, ServiceCategoryRepository
from ..domain.entities import Service, ServiceCategory


class CatalogService:
    
    def __init__(self, service_repository: ServiceRepository, category_repository: ServiceCategoryRepository):
        self._service_repository = service_repository
        self._category_repository = category_repository
    
    # Services
    async def get_all_services(self, limit: int = 100, offset: int = 0) -> List[Service]:
        return await self._service_repository.get_all(limit, offset)
    
    async def get_service_by_id(self, service_id: str) -> Optional[Service]:
        return await self._service_repository.get_by_id(service_id)
    
    async def create_service(self, service: Service) -> Service:
        return await self._service_repository.create(service)
    
    async def update_service(self, service: Service) -> Service:
        return await self._service_repository.update(service)
    
    async def delete_service(self, service_id: str) -> bool:
        return await self._service_repository.delete(service_id)
    
    async def get_services_by_category_id(self, category_id: str) -> List[Service]:
        return await self._service_repository.get_by_category_id(category_id)
    
    async def search_services_by_name(self, name: str) -> List[Service]:
        return await self._service_repository.search_by_name(name)
    
    # Categories
    async def get_all_categories(self) -> List[ServiceCategory]:
        return await self._category_repository.get_all()
    
    async def get_category_by_id(self, category_id: str) -> Optional[ServiceCategory]:
        return await self._category_repository.get_by_id(category_id)
    
    async def create_category(self, category: ServiceCategory) -> ServiceCategory:
        return await self._category_repository.create(category)
    
    async def update_category(self, category: ServiceCategory) -> ServiceCategory:
        return await self._category_repository.update(category)
    
    async def delete_category(self, category_id: str) -> bool:
        return await self._category_repository.delete(category_id) 