#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми пользователями.
Используется для тестирования производительности кеша.
"""

import asyncio
import sys
import os
import bcrypt
from uuid import uuid4

# Добавляем src в path для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.database import get_async_session, create_tables
from src.infrastructure.repositories import SQLAlchemyUserRepository
from src.domain.entities import User, UserRole


async def populate_users(count: int = 1000):
    """Заполнить базу данных тестовыми пользователями"""
    print(f"Populating database with {count} test users...")
    
    # Создаем таблицы если их нет
    await create_tables()
    
    async for session in get_async_session():
        try:
            user_repository = SQLAlchemyUserRepository(session)
            
            # Создаем хешированный пароль один раз для всех пользователей
            hashed_password = bcrypt.hashpw("testpass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            created_count = 0
            for i in range(count):
                try:
                    user = User(
                        username=f"testuser{i}",
                        email=f"testuser{i}@example.com",
                        full_name=f"Test User {i}",
                        hashed_password=hashed_password,
                        role=UserRole.CLIENT,
                        is_active=True
                    )
                    
                    # Проверяем, не существует ли уже такой пользователь
                    existing_user = await user_repository.get_by_username(user.username)
                    if existing_user:
                        print(f"User {user.username} already exists, skipping...")
                        continue
                    
                    created_user = await user_repository.create(user)
                    created_count += 1
                    
                    if created_count % 100 == 0:
                        print(f"Created {created_count} users...")
                        
                except Exception as e:
                    print(f"Error creating user {i}: {e}")
                    continue
            
            print(f"Successfully created {created_count} test users")
            
        except Exception as e:
            print(f"Database error: {e}")
            await session.rollback()
        finally:
            break  # Выходим из генератора после первой итерации


async def main():
    """Главная функция"""
    count = 1000
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Usage: python populate_db.py [count]")
            sys.exit(1)
    
    await populate_users(count)


if __name__ == "__main__":
    asyncio.run(main()) 