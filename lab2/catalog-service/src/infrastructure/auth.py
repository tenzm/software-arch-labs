from datetime import datetime
from typing import Optional, Dict, Any
import jwt
import httpx
from dataclasses import dataclass
from enum import Enum

class UserRole(Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    USER = "user"
    SPECIALIST = "specialist"

@dataclass
class JWTConfig:
    """Конфигурация для JWT"""
    secret_key: str = "your-secret-key-here"  # Должен совпадать с user-service
    algorithm: str = "HS256"
    user_service_url: str = "http://user-service:8000"  # URL user-service

@dataclass
class AuthenticatedUser:
    """Модель аутентифицированного пользователя"""
    id: str
    username: str
    email: str
    role: UserRole
    
    @classmethod
    def from_token_payload(cls, payload: dict) -> 'AuthenticatedUser':
        """Создать пользователя из payload токена"""
        return cls(
            id=payload.get("sub"),
            username=payload.get("username"), 
            email=payload.get("email"),
            role=UserRole(payload.get("role"))
        )

class JWTService:
    """Сервис для работы с JWT токенами в catalog-service"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
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
                
            # Проверяем, не истек ли токен
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def get_authenticated_user(self, token: str) -> Optional[AuthenticatedUser]:
        """Получить аутентифицированного пользователя из токена"""
        payload = self.decode_token(token)
        if payload:
            try:
                return AuthenticatedUser.from_token_payload(payload)
            except (KeyError, ValueError):
                return None
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