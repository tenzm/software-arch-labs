from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..domain.entities import Service, ServiceCategory
from ..domain.repositories import ServiceRepository, ServiceCategoryRepository
from .models import ServiceModel, ServiceCategoryModel


class SQLAlchemyServiceRepository(ServiceRepository):
    """SQLAlchemy реализация репозитория услуг"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Service]:
        """Получить все услуги с пагинацией"""
        stmt = select(ServiceModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        db_services = result.scalars().all()
        
        return [self._model_to_entity(db_service) for db_service in db_services]
    
    async def get_by_id(self, service_id: str) -> Optional[Service]:
        """Получить услугу по ID"""
        stmt = select(ServiceModel).where(ServiceModel.id == UUID(service_id))
        result = await self.session.execute(stmt)
        db_service = result.scalar_one_or_none()
        
        if db_service:
            return self._model_to_entity(db_service)
        return None
    
    async def create(self, service: Service) -> Service:
        """Создать услугу"""
        db_service = ServiceModel(
            category_id=UUID(service.category_id),
            name=service.name,
            description=service.description,
            price_from=service.price_from,
            price_to=service.price_to,
            duration_minutes=service.duration_minutes,
            is_active=service.is_active
        )
        
        self.session.add(db_service)
        await self.session.commit()
        await self.session.refresh(db_service)
        
        return self._model_to_entity(db_service)
    
    async def update(self, service: Service) -> Service:
        """Обновить услугу"""
        stmt = select(ServiceModel).where(ServiceModel.id == UUID(service.id))
        result = await self.session.execute(stmt)
        db_service = result.scalar_one_or_none()
        
        if not db_service:
            raise ValueError(f"Service with id {service.id} not found")
        
        # Обновляем поля
        db_service.category_id = UUID(service.category_id)
        db_service.name = service.name
        db_service.description = service.description
        db_service.price_from = service.price_from
        db_service.price_to = service.price_to
        db_service.duration_minutes = service.duration_minutes
        db_service.is_active = service.is_active
        
        await self.session.commit()
        await self.session.refresh(db_service)
        
        return self._model_to_entity(db_service)
    
    async def delete(self, service_id: str) -> bool:
        """Удалить услугу"""
        stmt = select(ServiceModel).where(ServiceModel.id == UUID(service_id))
        result = await self.session.execute(stmt)
        db_service = result.scalar_one_or_none()
        
        if not db_service:
            return False
        
        await self.session.delete(db_service)
        await self.session.commit()
        return True
    
    async def get_by_category_id(self, category_id: str) -> List[Service]:
        """Получить услуги по ID категории"""
        stmt = select(ServiceModel).where(ServiceModel.category_id == UUID(category_id))
        result = await self.session.execute(stmt)
        db_services = result.scalars().all()
        
        return [self._model_to_entity(db_service) for db_service in db_services]
    
    async def search_by_name(self, name: str) -> List[Service]:
        """Поиск услуг по названию"""
        stmt = select(ServiceModel).where(
            or_(
                ServiceModel.name.ilike(f"%{name}%"),
                ServiceModel.description.ilike(f"%{name}%")
            )
        ).limit(50)
        
        result = await self.session.execute(stmt)
        db_services = result.scalars().all()
        
        return [self._model_to_entity(db_service) for db_service in db_services]
    
    def _model_to_entity(self, db_service: ServiceModel) -> Service:
        """Преобразование модели SQLAlchemy в доменную сущность"""
        return Service(
            id=str(db_service.id),
            category_id=str(db_service.category_id),
            name=db_service.name,
            description=db_service.description,
            price_from=db_service.price_from,
            price_to=db_service.price_to,
            duration_minutes=db_service.duration_minutes,
            is_active=db_service.is_active,
            created_at=db_service.created_at,
            updated_at=db_service.updated_at
        )


class SQLAlchemyServiceCategoryRepository(ServiceCategoryRepository):
    """SQLAlchemy реализация репозитория категорий услуг"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self) -> List[ServiceCategory]:
        """Получить все категории"""
        stmt = select(ServiceCategoryModel).where(ServiceCategoryModel.is_active == True)
        result = await self.session.execute(stmt)
        db_categories = result.scalars().all()
        
        return [self._model_to_entity(db_category) for db_category in db_categories]
    
    async def get_by_id(self, category_id: str) -> Optional[ServiceCategory]:
        """Получить категорию по ID"""
        stmt = select(ServiceCategoryModel).where(ServiceCategoryModel.id == UUID(category_id))
        result = await self.session.execute(stmt)
        db_category = result.scalar_one_or_none()
        
        if db_category:
            return self._model_to_entity(db_category)
        return None
    
    async def create(self, category: ServiceCategory) -> ServiceCategory:
        """Создать категорию"""
        db_category = ServiceCategoryModel(
            name=category.name,
            description=category.description,
            is_active=category.is_active
        )
        
        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        
        return self._model_to_entity(db_category)
    
    async def update(self, category: ServiceCategory) -> ServiceCategory:
        """Обновить категорию"""
        stmt = select(ServiceCategoryModel).where(ServiceCategoryModel.id == UUID(category.id))
        result = await self.session.execute(stmt)
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            raise ValueError(f"Category with id {category.id} not found")
        
        # Обновляем поля
        db_category.name = category.name
        db_category.description = category.description
        db_category.is_active = category.is_active
        
        await self.session.commit()
        await self.session.refresh(db_category)
        
        return self._model_to_entity(db_category)
    
    async def delete(self, category_id: str) -> bool:
        """Удалить категорию"""
        stmt = select(ServiceCategoryModel).where(ServiceCategoryModel.id == UUID(category_id))
        result = await self.session.execute(stmt)
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            return False
        
        await self.session.delete(db_category)
        await self.session.commit()
        return True
    
    def _model_to_entity(self, db_category: ServiceCategoryModel) -> ServiceCategory:
        """Преобразование модели SQLAlchemy в доменную сущность"""
        return ServiceCategory(
            id=str(db_category.id),
            name=db_category.name,
            description=db_category.description,
            is_active=db_category.is_active,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at
        ) 