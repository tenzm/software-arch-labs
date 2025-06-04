from datetime import datetime, timedelta
from typing import Optional
import jwt
from dataclasses import dataclass

from ..domain.entities import User


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
    
    def create_access_token(self, user: User) -> str:
        """Создать access token для пользователя"""
        expires_delta = timedelta(minutes=self.config.access_token_expire_minutes)
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user.id,  # subject (user id)
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access_token"
        }
        
        token = jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        return token
    
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
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """Получить ID пользователя из токена"""
        payload = self.decode_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    def get_username_from_token(self, token: str) -> Optional[str]:
        """Получить username из токена"""
        payload = self.decode_token(token)
        if payload:
            return payload.get("username")
        return None 