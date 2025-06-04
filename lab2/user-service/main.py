import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.controllers import router as user_router
from src.presentation.dependencies import get_user_use_cases
from src.domain.entities import UserRole

# Создание приложения FastAPI
app = FastAPI(
    title="User Service API",
    description="Сервис управления пользователями для платформы Profi.ru",
    version="1.0.0"
)

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(user_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "User Service API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}


async def create_admin_user():
    """Создать администратора при запуске приложения"""
    user_use_cases = get_user_use_cases()
    
    try:
        # Проверяем, существует ли уже админ
        await user_use_cases.get_user_by_username("admin")
        print("Admin user already exists")
    except:
        # Создаем администратора
        try:
            admin_user = await user_use_cases.create_user(
                username="admin",
                email="admin@profi.ru",
                password="secret",
                full_name="Administrator",
                role=UserRole.ADMIN
            )
            print(f"Created admin user with ID: {admin_user.id}")
        except Exception as e:
            print(f"Failed to create admin user: {e}")


@app.on_event("startup")
async def startup_event():
    """События при запуске приложения"""
    print("Starting User Service...")
    await create_admin_user()
    print("User Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке приложения"""
    print("Shutting down User Service...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 