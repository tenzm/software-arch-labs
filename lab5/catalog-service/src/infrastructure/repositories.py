from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database

from ..domain.entities import Service, ServiceCategory
from ..repository.interfaces import ServiceRepository, ServiceCategoryRepository
from .database import get_database


class MongoServiceRepository(ServiceRepository):
    """MongoDB реализация репозитория услуг"""
    
    def __init__(self, database: Database = None):
        self.database = database
        self.collection_name = "services"
    
    def _get_collection(self):
        """Получить коллекцию услуг"""
        if self.database is None:
            self.database = get_database()
        return self.database[self.collection_name]
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Service]:
        """Получить все услуги с пагинацией"""
        collection = self._get_collection()
        cursor = collection.find({}).skip(offset).limit(limit)
        services = []
        for doc in cursor:
            services.append(Service.from_dict(doc))
        return services
    
    async def get_by_id(self, service_id: str) -> Optional[Service]:
        """Получить услугу по ID"""
        collection = self._get_collection()
        doc = collection.find_one({"_id": ObjectId(service_id)})
        if doc:
            return Service.from_dict(doc)
        return None
    
    async def create(self, service: Service) -> Service:
        """Создать услугу"""
        collection = self._get_collection()
        service_dict = service.to_dict()
        result = collection.insert_one(service_dict)
        
        # Возвращаем созданный объект с ID
        created_doc = collection.find_one({"_id": result.inserted_id})
        return Service.from_dict(created_doc)
    
    async def update(self, service: Service) -> Service:
        """Обновить услугу"""
        collection = self._get_collection()
        service_dict = service.to_dict()
        service_dict["updated_at"] = datetime.utcnow()
        
        result = collection.update_one(
            {"_id": ObjectId(service.id)},
            {"$set": service_dict}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"Service with id {service.id} not found")
        
        # Возвращаем обновленный объект
        updated_doc = collection.find_one({"_id": ObjectId(service.id)})
        return Service.from_dict(updated_doc)
    
    async def delete(self, service_id: str) -> bool:
        """Удалить услугу"""
        collection = self._get_collection()
        result = collection.delete_one({"_id": ObjectId(service_id)})
        return result.deleted_count > 0
    
    async def get_by_category_id(self, category_id: str) -> List[Service]:
        """Получить услуги по ID категории"""
        collection = self._get_collection()
        cursor = collection.find({"category_id": category_id})
        services = []
        for doc in cursor:
            services.append(Service.from_dict(doc))
        return services
    
    async def search_by_name(self, name: str) -> List[Service]:
        """Поиск услуг по названию (полнотекстовый поиск)"""
        collection = self._get_collection()
        cursor = collection.find(
            {"$text": {"$search": name}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(50)
        
        services = []
        for doc in cursor:
            services.append(Service.from_dict(doc))
        return services
    
    async def get_by_price_range(self, min_price: float, max_price: float) -> List[Service]:
        """Получить услуги в диапазоне цен"""
        collection = self._get_collection()
        cursor = collection.find({
            "$and": [
                {"price_from": {"$gte": min_price}},
                {"price_to": {"$lte": max_price}},
                {"is_active": True}
            ]
        })
        
        services = []
        for doc in cursor:
            services.append(Service.from_dict(doc))
        return services


class MongoServiceCategoryRepository(ServiceCategoryRepository):
    """MongoDB реализация репозитория категорий услуг"""
    
    def __init__(self, database: Database = None):
        self.database = database
        self.collection_name = "categories"
    
    def _get_collection(self):
        """Получить коллекцию категорий"""
        if self.database is None:
            self.database = get_database()
        return self.database[self.collection_name]
    
    async def get_all(self) -> List[ServiceCategory]:
        """Получить все активные категории"""
        collection = self._get_collection()
        cursor = collection.find({"is_active": True})
        categories = []
        for doc in cursor:
            categories.append(ServiceCategory.from_dict(doc))
        return categories
    
    async def get_by_id(self, category_id: str) -> Optional[ServiceCategory]:
        """Получить категорию по ID"""
        collection = self._get_collection()
        doc = collection.find_one({"_id": ObjectId(category_id)})
        if doc:
            return ServiceCategory.from_dict(doc)
        return None
    
    async def create(self, category: ServiceCategory) -> ServiceCategory:
        """Создать категорию"""
        collection = self._get_collection()
        category_dict = category.to_dict()
        result = collection.insert_one(category_dict)
        
        # Возвращаем созданный объект с ID
        created_doc = collection.find_one({"_id": result.inserted_id})
        return ServiceCategory.from_dict(created_doc)
    
    async def update(self, category: ServiceCategory) -> ServiceCategory:
        """Обновить категорию"""
        collection = self._get_collection()
        category_dict = category.to_dict()
        category_dict["updated_at"] = datetime.utcnow()
        
        result = collection.update_one(
            {"_id": ObjectId(category.id)},
            {"$set": category_dict}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"Category with id {category.id} not found")
        
        # Возвращаем обновленный объект
        updated_doc = collection.find_one({"_id": ObjectId(category.id)})
        return ServiceCategory.from_dict(updated_doc)
    
    async def delete(self, category_id: str) -> bool:
        """Удалить категорию"""
        collection = self._get_collection()
        result = collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0
    
    async def get_by_name(self, name: str) -> Optional[ServiceCategory]:
        """Получить категорию по названию"""
        collection = self._get_collection()
        doc = collection.find_one({"name": name})
        if doc:
            return ServiceCategory.from_dict(doc)
        return None 