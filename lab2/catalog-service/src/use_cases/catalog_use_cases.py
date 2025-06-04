from typing import List, Optional
from ..domain.entities import Service
from ..domain.repositories import ServiceRepository


class CatalogService:
    
    def __init__(self, service_repository: ServiceRepository):
        self._service_repository = service_repository
    
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