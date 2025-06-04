from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from src.presentation.controllers import (
    get_services_controller,
    get_service_controller,
    create_service_controller,
    update_service_controller,
    delete_service_controller,
    get_categories_controller,
    get_category_controller,
    create_category_controller,
    delete_category_controller
)
from src.presentation.models import (
    ServiceResponse,
    ServiceCreateRequest,
    ServiceUpdateRequest,
    CategoryResponse,
    CategoryCreateRequest,
    ServicesListResponse,
    CategoriesListResponse
)
from src.presentation.dependencies import (
    get_catalog_service, 
    get_current_active_user, 
    get_admin_user
)
from src.infrastructure.auth import AuthenticatedUser
from src.use_cases.catalog_use_cases import CatalogService

# Создание приложения FastAPI
app = FastAPI(
    title="Catalog Service API",
    description="Сервис управления каталогом услуг для платформы Profi.ru",
    version="1.0.0"
)

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Catalog Service API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}



# API для работы с услугами


@app.get("/api/v1/services", response_model=ServicesListResponse)
async def get_services(
    category: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить список услуг (требуется аутентификация)"""
    return await get_services_controller(catalog_service, category)


@app.get("/api/v1/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить услугу по ID (требуется аутентификация)"""
    return await get_service_controller(service_id, catalog_service)


@app.post("/api/v1/services", response_model=ServiceResponse, status_code=201)
async def create_service(
    service_request: ServiceCreateRequest,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может создавать
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Создать новую услугу (требуются права администратора)"""
    return await create_service_controller(service_request, catalog_service)


@app.put("/api/v1/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str, 
    service_request: ServiceUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может обновлять
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Обновить услугу (требуются права администратора)"""
    return await update_service_controller(service_id, service_request, catalog_service)


@app.delete("/api/v1/services/{service_id}")
async def delete_service(
    service_id: str,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может удалять
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Удалить услугу (требуются права администратора)"""
    return await delete_service_controller(service_id, catalog_service)



# API для работы с категориями


@app.get("/api/v1/categories", response_model=CategoriesListResponse)
async def get_categories(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить список категорий (требуется аутентификация)"""
    return await get_categories_controller(catalog_service)


@app.get("/api/v1/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Получить категорию по ID (требуется аутентификация)"""
    return await get_category_controller(category_id, catalog_service)


@app.post("/api/v1/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_request: CategoryCreateRequest,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может создавать
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Создать новую категорию (требуются права администратора)"""
    return await create_category_controller(category_request, catalog_service)


@app.delete("/api/v1/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: AuthenticatedUser = Depends(get_admin_user),  # Только админ может удалять
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Удалить категорию (требуются права администратора)"""
    return await delete_category_controller(category_id, catalog_service)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 