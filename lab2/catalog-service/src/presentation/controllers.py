from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from .models import (
    ServiceResponse, 
    ServiceCreateRequest, 
    ServiceUpdateRequest,
    ServicesListResponse,
    MessageResponse
)
from .dependencies import (
    get_catalog_service, 
    get_current_active_user, 
    get_admin_user
)
from ..infrastructure.auth import AuthenticatedUser
from ..use_cases.catalog_use_cases import CatalogService
from ..domain.entities import Service

router = APIRouter()


def create_service_response(service: Service) -> ServiceResponse:
    """Создать response модель из доменной сущности"""
    return ServiceResponse.from_domain(service)


@router.get("/services", response_model=ServicesListResponse, tags=["services"])
async def get_services(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить список услуг (требуется аутентификация)"""
    if category:
        services = await catalog_service.get_services_by_category(category)
    else:
        services = await catalog_service.get_all_services()
    
    return ServicesListResponse(
        services=[create_service_response(service) for service in services],
        total=len(services)
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