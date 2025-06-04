from datetime import datetime, timedelta
from typing import Optional
import jwt
from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    CLIENT = "client"
    SPECIALIST = "specialist"


@dataclass
class AuthenticatedUser:
    """Аутентифицированный пользователь"""
    id: str
    username: str
    email: str
    role: UserRole


@dataclass
class JWTConfig:
    """Конфигурация для JWT"""
    secret_key: str = "your-secret-key-here"  # В продакшене должен быть случайным
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class JWTService:
    """Сервис для работы с JWT токенами"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
    
    def decode_token(self, token: str) -> Optional[dict]:
        """Декодировать и валидировать токен"""
        try:
            payload = jwt.decode(
                token, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm]
            )
            
            # Проверяем тип токена
            if payload.get("type") != "access_token":
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def get_authenticated_user(self, token: str) -> Optional[AuthenticatedUser]:
        """Получить аутентифицированного пользователя из токена"""
        payload = self.decode_token(token)
        if not payload:
            return None
        
        try:
            return AuthenticatedUser(
                id=payload.get("sub"),
                username=payload.get("username"),
                email=payload.get("email"),
                role=UserRole(payload.get("role", "client"))
            )
        except (ValueError, TypeError):
            return None
    
    async def verify_token_with_user_service(self, token: str) -> Optional[AuthenticatedUser]:
        """Верифицировать токен через user-service (дополнительная проверка)"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.config.user_service_url}/api/v1/users/me",
                    headers=headers,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return AuthenticatedUser(
                        id=user_data["id"],
                        username=user_data["username"],
                        email=user_data["email"],
                        role=UserRole(user_data["role"])
                    )
        except Exception:
            # В случае ошибки полагаемся на локальную проверку токена
            pass
        
        return None 