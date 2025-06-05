from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.controllers import router as catalog_router
from src.infrastructure.database import connect_to_mongo, close_mongo_connection, get_database
from src.infrastructure.repositories import MongoServiceCategoryRepository, MongoServiceRepository
from src.domain.entities import ServiceCategory, Service

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


def seed_data():
    """Наполнение БД тестовыми данными"""
    try:
        database = get_database()
        
        # Инициализация репозиториев
        category_repo = MongoServiceCategoryRepository(database)
        service_repo = MongoServiceRepository(database)
        
        # Проверяем, есть ли уже данные
        # Создаем синхронную функцию для проверки данных
        categories_collection = database.categories
        existing_count = categories_collection.count_documents({})
        if existing_count > 0:
            print("Test data already exists, skipping seed")
            return
        
        # Создаем категории
        categories_data = [
            {
                "name": "Ремонт и строительство",
                "description": "Услуги по ремонту квартир, домов и офисов"
            },
            {
                "name": "Красота и здоровье",
                "description": "Услуги косметологов, массажистов, стилистов"
            },
            {
                "name": "Уборка и клининг",
                "description": "Генеральная уборка, мытье окон, химчистка"
            },
            {
                "name": "Репетиторы",
                "description": "Обучение и подготовка к экзаменам"
            },
            {
                "name": "IT и программирование",
                "description": "Создание сайтов, мобильных приложений, настройка ПК"
            }
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category = ServiceCategory(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            # Создаем категорию напрямую через коллекцию
            category_dict = category.to_dict()
            result = categories_collection.insert_one(category_dict)
            created_doc = categories_collection.find_one({"_id": result.inserted_id})
            created_category = ServiceCategory.from_dict(created_doc)
            created_categories.append(created_category)
            print(f"Created category: {created_category.name}")
        
        # Создаем услуги
        services_data = [
            # Ремонт и строительство
            {
                "name": "Поклейка обоев",
                "description": "Профессиональная поклейка обоев любой сложности",
                "price_from": 300.0,
                "price_to": 800.0,
                "duration_minutes": 240,
                "category": "Ремонт и строительство"
            },
            {
                "name": "Укладка плитки",
                "description": "Укладка керамической плитки в ванной и на кухне",
                "price_from": 1000.0,
                "price_to": 2500.0,
                "duration_minutes": 480,
                "category": "Ремонт и строительство"
            },
            # Красота и здоровье
            {
                "name": "Массаж лица",
                "description": "Расслабляющий и омолаживающий массаж лица",
                "price_from": 1500.0,
                "price_to": 3000.0,
                "duration_minutes": 60,
                "category": "Красота и здоровье"
            },
            {
                "name": "Стрижка и укладка",
                "description": "Модная стрижка и профессиональная укладка волос",
                "price_from": 800.0,
                "price_to": 3500.0,
                "duration_minutes": 120,
                "category": "Красота и здоровье"
            },
            # Уборка
            {
                "name": "Генеральная уборка",
                "description": "Полная уборка квартиры с использованием профессиональных средств",
                "price_from": 2000.0,
                "price_to": 8000.0,
                "duration_minutes": 300,
                "category": "Уборка и клининг"
            },
            # Репетиторы
            {
                "name": "Математика для школьников",
                "description": "Индивидуальные занятия по математике, подготовка к ЕГЭ",
                "price_from": 800.0,
                "price_to": 2000.0,
                "duration_minutes": 60,
                "category": "Репетиторы"
            },
            # IT
            {
                "name": "Создание сайта",
                "description": "Разработка корпоративного сайта или интернет-магазина",
                "price_from": 15000.0,
                "price_to": 100000.0,
                "duration_minutes": 2880,  # 48 часов
                "category": "IT и программирование"
            }
        ]
        
        # Создаем словарь категорий для быстрого поиска
        category_map = {cat.name: cat.id for cat in created_categories}
        
        services_collection = database.services
        for service_data in services_data:
            category_id = category_map[service_data["category"]]
            service = Service(
                category_id=category_id,
                name=service_data["name"],
                description=service_data["description"],
                price_from=service_data["price_from"],
                price_to=service_data["price_to"],
                duration_minutes=service_data["duration_minutes"]
            )
            # Создаем услугу напрямую через коллекцию
            service_dict = service.to_dict()
            result = services_collection.insert_one(service_dict)
            created_doc = services_collection.find_one({"_id": result.inserted_id})
            created_service = Service.from_dict(created_doc)
            print(f"Created service: {created_service.name}")
        
        print("Test data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")


@app.on_event("startup")
async def startup_event():
    """События при запуске приложения"""
    print("Starting Catalog Service...")
    
    # Подключаемся к MongoDB
    try:
        connect_to_mongo()
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    
    # Наполняем тестовыми данными
    seed_data()
    
    print("Catalog Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке приложения"""
    print("Shutting down Catalog Service...")
    close_mongo_connection()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 