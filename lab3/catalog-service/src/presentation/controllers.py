from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from .models import (
    ServiceResponse, 
    ServiceCreateRequest, 
    ServiceUpdateRequest,
    ServicesListResponse,
    ServiceCategoryResponse,
    ServiceCategoryCreateRequest,
    CategoriesListResponse,
    MessageResponse
)
from .dependencies import (
    get_catalog_service, 
    get_current_active_user, 
    get_admin_user
)
from ..infrastructure.auth import AuthenticatedUser
from ..use_cases.catalog_use_cases import CatalogService
from ..domain.entities import Service, ServiceCategory

router = APIRouter()


def create_service_response(service: Service) -> ServiceResponse:
    """Создать response модель из доменной сущности"""
    return ServiceResponse.from_domain(service)


def create_category_response(category: ServiceCategory) -> ServiceCategoryResponse:
    """Создать response модель для категории из доменной сущности"""
    return ServiceCategoryResponse.from_domain(category)


@router.get("/services", response_model=ServicesListResponse, tags=["services"])
async def get_services(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить список услуг (требуется аутентификация)"""
    if category:
        services = await catalog_service.get_services_by_category_id(category)
    else:
        services = await catalog_service.get_all_services(limit=limit, offset=offset)
    
    return ServicesListResponse(
        services=[create_service_response(service) for service in services],
        total=len(services),
        limit=limit,
        offset=offset
    )


@router.get("/services/{service_id}", response_model=ServiceResponse, tags=["services"])
async def get_service(
    service_id: str,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить услугу по ID (требуется аутентификация)"""
    service = await catalog_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Service not found"
        )
    
    return create_service_response(service)


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED, tags=["services"])
async def create_service(
    service_request: ServiceCreateRequest,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может создавать
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Создать новую услугу (требуются права администратора)"""
    try:
        service = service_request.to_domain()
        created_service = await catalog_service.create_service(service)
        return create_service_response(created_service)
    except Exception as e:
        error_message = str(e)
        if "ForeignKeyViolationError" in error_message and "category_id" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category_id: {service_request.category_id}. Use GET /api/v1/categories to see available categories."
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.put("/services/{service_id}", response_model=ServiceResponse, tags=["services"])
async def update_service(
    service_id: str, 
    service_request: ServiceUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может обновлять
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Обновить услугу (требуются права администратора)"""
    try:
        existing_service = await catalog_service.get_service_by_id(service_id)
        if not existing_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Service not found"
            )
        
        service_request.apply_to_domain(existing_service)
        updated_service = await catalog_service.update_service(existing_service)
        return create_service_response(updated_service)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.delete("/services/{service_id}", response_model=MessageResponse, tags=["services"])
async def delete_service(
    service_id: str,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может удалять
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Удалить услугу (требуются права администратора)"""
    success = await catalog_service.delete_service(service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Service not found"
        )
    
    return MessageResponse(message="Service deleted successfully")


@router.get("/categories", response_model=CategoriesListResponse, tags=["categories"])
async def get_categories(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить список категорий (требуется аутентификация)"""
    categories = await catalog_service.get_all_categories()
    
    return CategoriesListResponse(
        categories=[create_category_response(category) for category in categories],
        total=len(categories)
    )


@router.post("/categories", response_model=ServiceCategoryResponse, status_code=status.HTTP_201_CREATED, tags=["categories"])
async def create_category(
    category_request: ServiceCategoryCreateRequest,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может создавать
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Создать новую категорию (требуются права администратора)"""
    try:
        category = category_request.to_domain()
        created_category = await catalog_service.create_category(category)
        return create_category_response(created_category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) 