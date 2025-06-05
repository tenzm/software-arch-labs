import os
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:profi_mongo_pass@localhost:27017/catalog_db?authSource=admin")

class MongoDB:
    client: Optional[MongoClient] = None
    database: Optional[Database] = None

mongodb = MongoDB()


def connect_to_mongo():
    """Создание подключения к MongoDB"""
    mongodb.client = MongoClient(MONGODB_URL)
    mongodb.database = mongodb.client.get_database("catalog_db")
    
    # Создание индексов
    create_indexes()
    
    print(f"Connected to MongoDB at {MONGODB_URL}")


def close_mongo_connection():
    """Закрытие подключения к MongoDB"""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")


def get_database() -> Database:
    """Получение экземпляра базы данных"""
    if mongodb.database is None:
        connect_to_mongo()
    return mongodb.database


def create_indexes():
    """Создание индексов для коллекций"""
    if mongodb.database is None:
        return
    
    # Индексы для коллекции categories
    categories_collection = mongodb.database.categories
    categories_collection.create_index("name")
    categories_collection.create_index("is_active")
    categories_collection.create_index([("name", 1), ("is_active", 1)])
    
    # Индексы для коллекции services
    services_collection = mongodb.database.services
    services_collection.create_index("name")
    services_collection.create_index("category_id")
    services_collection.create_index("is_active")
    services_collection.create_index("price_from")
    services_collection.create_index("price_to")
    services_collection.create_index([("category_id", 1), ("is_active", 1)])
    services_collection.create_index([("name", "text"), ("description", "text")])
    
    print("Created database indexes")


def create_tables():
    """Создание коллекций и индексов (совместимость с существующим кодом)"""
    connect_to_mongo() 