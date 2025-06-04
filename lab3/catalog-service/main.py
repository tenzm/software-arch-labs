from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.controllers import router as catalog_router
from src.infrastructure.database import create_tables

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

# Подключение роутеров
app.include_router(catalog_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Catalog Service API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """События при запуске приложения"""
    print("Starting Catalog Service...")
    
    # Создаем таблицы (на случай если не инициализированы через init.sql)
    try:
        await create_tables()
        print("Database tables ensured")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    print("Catalog Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке приложения"""
    print("Shutting down Catalog Service...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 