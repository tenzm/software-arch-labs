"""Доменные исключения"""


class DomainException(Exception):
    """Базовое доменное исключение"""
    pass


class UserNotFound(DomainException):
    """Пользователь не найден"""
    pass


class DuplicateUser(DomainException):
    """Пользователь уже существует"""
    pass


class InvalidCredentials(DomainException):
    """Неверные учетные данные"""
    pass


class AccessDenied(DomainException):
    """Доступ запрещен"""
    pass


class ValidationError(DomainException):
    """Ошибка валидации данных"""
    pass 