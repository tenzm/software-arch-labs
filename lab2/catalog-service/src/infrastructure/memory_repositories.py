from typing import List, Optional, Dict
from datetime import datetime
from ..domain.entities import Service, Category, ServiceStatus
from ..domain.repositories import ServiceRepository, CategoryRepository


class InMemoryServiceRepository(ServiceRepository):
    """In-memory реализация репозитория услуг"""
    
    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Инициализация тестовых данных"""
        sample_services = [
            Service(
                title="Репетитор по математике",
                description="Подготовка к ЕГЭ и ОГЭ по математике",
                category="Образование",
                price_from=1000,
                price_to=2500,
                status=ServiceStatus.ACTIVE,
                tags=["математика", "репетитор", "ЕГЭ"]
            ),
            Service(
                title="Уборка квартир",
                description="Генеральная и поддерживающая уборка",
                category="Клининг",
                price_from=1500,
                price_to=5000,
                status=ServiceStatus.ACTIVE,
                tags=["уборка", "клининг", "квартира"]
            )
        ]
        
        for service in sample_services:
            self._services[service.id] = service
    
    async def get_all(self) -> List[Service]:
        """Получить все услуги"""
        return list(self._services.values())
    
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
    
    async def get_by_category(self, category: str) -> List[Service]:
        """Получить услуги по категории"""
        return [s for s in self._services.values() if s.category.lower() == category.lower()]


class InMemoryCategoryRepository(CategoryRepository):
    """In-memory реализация репозитория категорий"""
    
    def __init__(self):
        self._categories: Dict[str, Category] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Инициализация тестовых данных"""
        sample_categories = [
            Category(name="Образование", description="Репетиторство, курсы, обучение"),
            Category(name="Клининг", description="Уборка помещений"),
            Category(name="Ремонт", description="Строительные и отделочные работы"),
            Category(name="IT", description="Программирование и техническая поддержка")
        ]
        
        for category in sample_categories:
            self._categories[category.id] = category
    
    async def get_all(self) -> List[Category]:
        """Получить все категории"""
        return list(self._categories.values())
    
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        """Получить категорию по ID"""
        return self._categories.get(category_id)
    
    async def create(self, category: Category) -> Category:
        """Создать новую категорию"""
        category.created_at = datetime.utcnow()
        self._categories[category.id] = category
        return category
    
    async def update(self, category: Category) -> Category:
        """Обновить категорию"""
        self._categories[category.id] = category
        return category
    
    async def delete(self, category_id: str) -> bool:
        """Удалить категорию"""
        if category_id in self._categories:
            del self._categories[category_id]
            return True
        return False 