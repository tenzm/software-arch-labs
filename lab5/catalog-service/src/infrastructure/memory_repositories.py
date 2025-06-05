from typing import List, Optional, Dict
from datetime import datetime
from ..domain.entities import Service, ServiceCategory
from ..repository.interfaces import ServiceRepository, ServiceCategoryRepository


class InMemoryServiceRepository(ServiceRepository):
    """In-memory реализация репозитория услуг"""
    
    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Инициализация тестовых данных"""
        sample_services = [
            Service(
                name="Репетитор по математике",
                description="Подготовка к ЕГЭ и ОГЭ по математике",
                category_id="education-category-id",
                price_from=1000.0,
                price_to=2500.0,
                duration_minutes=60,
                is_active=True
            ),
            Service(
                name="Уборка квартир",
                description="Генеральная и поддерживающая уборка",
                category_id="cleaning-category-id",
                price_from=1500.0,
                price_to=5000.0,
                duration_minutes=120,
                is_active=True
            )
        ]
        
        for service in sample_services:
            self._services[service.id] = service
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Service]:
        """Получить все услуги с пагинацией"""
        services = list(self._services.values())
        return services[offset:offset + limit]
    
    async def get_by_id(self, service_id: str) -> Optional[Service]:
        """Получить услугу по ID"""
        return self._services.get(service_id)
    
    async def create(self, service: Service) -> Service:
        """Создать новую услугу"""
        service.created_at = datetime.utcnow()
        service.updated_at = datetime.utcnow()
        self._services[service.id] = service
        return service
    
    async def update(self, service: Service) -> Service:
        """Обновить услугу"""
        service.updated_at = datetime.utcnow()
        self._services[service.id] = service
        return service
    
    async def delete(self, service_id: str) -> bool:
        """Удалить услугу"""
        if service_id in self._services:
            del self._services[service_id]
            return True
        return False
    
    async def get_by_category_id(self, category_id: str) -> List[Service]:
        """Получить услуги по ID категории"""
        return [s for s in self._services.values() if s.category_id == category_id]
    
    async def search_by_name(self, name: str) -> List[Service]:
        """Поиск услуг по названию"""
        return [s for s in self._services.values() if name.lower() in s.name.lower()]


class InMemoryCategoryRepository(ServiceCategoryRepository):
    """In-memory реализация репозитория категорий"""
    
    def __init__(self):
        self._categories: Dict[str, ServiceCategory] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Инициализация тестовых данных"""
        sample_categories = [
            ServiceCategory(name="Образование", description="Репетиторство, курсы, обучение"),
            ServiceCategory(name="Клининг", description="Уборка помещений"),
            ServiceCategory(name="Ремонт", description="Строительные и отделочные работы"),
            ServiceCategory(name="IT", description="Программирование и техническая поддержка")
        ]
        
        for category in sample_categories:
            self._categories[category.id] = category
    
    async def get_all(self) -> List[ServiceCategory]:
        """Получить все категории"""
        return list(self._categories.values())
    
    async def get_by_id(self, category_id: str) -> Optional[ServiceCategory]:
        """Получить категорию по ID"""
        return self._categories.get(category_id)
    
    async def create(self, category: ServiceCategory) -> ServiceCategory:
        """Создать новую категорию"""
        category.created_at = datetime.utcnow()
        self._categories[category.id] = category
        return category
    
    async def update(self, category: ServiceCategory) -> ServiceCategory:
        """Обновить категорию"""
        self._categories[category.id] = category
        return category
    
    async def delete(self, category_id: str) -> bool:
        """Удалить категорию"""
        if category_id in self._categories:
            del self._categories[category_id]
            return True
        return False 