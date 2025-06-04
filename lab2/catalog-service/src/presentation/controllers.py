from fastapi import HTTPException
from typing import List, Optional

from ..domain.entities import Service, Category
from ..use_cases.catalog_use_cases import CatalogService
from .models import (
    ServiceResponse, 
    ServiceCreateRequest, 
    ServiceUpdateRequest,
    CategoryResponse,
    CategoryCreateRequest,
    ServicesListResponse,
    CategoriesListResponse
)


# Контроллеры для работы с услугами
async def get_services_controller(
    catalog_service: CatalogService,
    category: Optional[str] = None
) -> ServicesListResponse:
    if category:
        services = await catalog_service.get_services_by_category(category)
    else:
        services = await catalog_service.get_all_services()
    
    return ServicesListResponse(
        services=[ServiceResponse.from_domain(service) for service in services],
        total=len(services)
    )


async def get_service_controller(
    service_id: str,
    catalog_service: CatalogService
) -> ServiceResponse:
    service = await catalog_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return ServiceResponse.from_domain(service)


async def create_service_controller(
    service_request: ServiceCreateRequest,
    catalog_service: CatalogService
) -> ServiceResponse:
    service = service_request.to_domain()
    created_service = await catalog_service.create_service(service)
    return ServiceResponse.from_domain(created_service)


async def update_service_controller(
    service_id: str,
    service_request: ServiceUpdateRequest, 
    catalog_service: CatalogService
) -> ServiceResponse:
    existing_service = await catalog_service.get_service_by_id(service_id)
    if not existing_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_request.apply_to_domain(existing_service)
    updated_service = await catalog_service.update_service(existing_service)
    return ServiceResponse.from_domain(updated_service)


async def delete_service_controller(
    service_id: str,
    catalog_service: CatalogService
):
    success = await catalog_service.delete_service(service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return {"message": "Service deleted successfully"}



# Контроллеры для работы с категориями


async def get_categories_controller(
    catalog_service: CatalogService
) -> CategoriesListResponse:
    categories = await catalog_service.get_all_categories()
    return CategoriesListResponse(
        categories=[CategoryResponse.from_domain(category) for category in categories],
        total=len(categories)
    )


async def get_category_controller(
    category_id: str,
    catalog_service: CatalogService
) -> CategoryResponse:
    category = await catalog_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategoryResponse.from_domain(category)


async def create_category_controller(
    category_request: CategoryCreateRequest,
    catalog_service: CatalogService
) -> CategoryResponse:
    category = category_request.to_domain()
    created_category = await catalog_service.create_category(category)
    return CategoryResponse.from_domain(created_category)


async def delete_category_controller(
    category_id: str,
    catalog_service: CatalogService
):
    success = await catalog_service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"} 