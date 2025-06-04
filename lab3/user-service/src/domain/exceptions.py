"""Доменные исключения"""


class DomainException(Exception):
    """Базовое доменное исключение"""
    pass


class UserNotFoundError(DomainException):
    """Пользователь не найден"""
    pass


class UserAlreadyExistsError(DomainException):
    """Пользователь уже существует"""
    pass


class InvalidCredentialsError(DomainException):
    """Неверные учетные данные"""
    pass


class AccessDeniedError(DomainException):
    """Доступ запрещен"""
    pass


class ValidationError(DomainException):
    """Ошибка валидации данных"""
    pass 