import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

from src.presentation.controllers import router as user_router
from src.infrastructure.database import get_async_session, create_tables
from src.infrastructure.repositories import SQLAlchemyUserRepository
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
    async for session in get_async_session():
        try:
            user_repository = SQLAlchemyUserRepository(session)
            
            # Проверяем, существует ли уже админ
            existing_admin = await user_repository.get_by_username("admin")
            if existing_admin:
                print("Admin user already exists")
                return
            
            # Создаем администратора с захешированным паролем
            from src.domain.entities import User
            
            hashed_password = bcrypt.hashpw("secret".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin_user = User(
                username="admin",
                email="admin@profi.ru",
                hashed_password=hashed_password,
                full_name="Администратор",
                role=UserRole.ADMIN
            )
            
            created_admin = await user_repository.create(admin_user)
            print(f"Created admin user with ID: {created_admin.id}")
            
        except Exception as e:
            print(f"Failed to create admin user: {e}")
            await session.rollback()
        finally:
            break  # Выходим из генератора после первой итерации


@app.on_event("startup")
async def startup_event():
    """События при запуске приложения"""
    print("Starting User Service...")
    
    # Создаем таблицы (на случай если не инициализированы через init.sql)
    try:
        await create_tables()
        print("Database tables ensured")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    # Создаем админа
    await create_admin_user()
    print("User Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке приложения"""
    print("Shutting down User Service...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 