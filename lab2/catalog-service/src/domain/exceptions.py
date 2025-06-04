"""Доменные исключения для каталога услуг"""


class CatalogDomainException(Exception):
    """Базовое исключение для доменного слоя каталога"""
    pass


class ServiceNotFoundException(CatalogDomainException):
    """Исключение когда услуга не найдена"""
    def __init__(self, service_id: str):
        self.service_id = service_id
        super().__init__(f"Service with id {service_id} not found")


class CategoryNotFoundException(CatalogDomainException):
    """Исключение когда категория не найдена"""
    def __init__(self, category_id: str):
        self.category_id = category_id
        super().__init__(f"Category with id {category_id} not found")


class ServiceValidationError(CatalogDomainException):
    """Исключение при ошибке валидации услуги"""
    pass


class CategoryValidationError(CatalogDomainException):
    """Исключение при ошибке валидации категории"""
    pass


class DuplicateServiceError(CatalogDomainException):
    """Исключение при попытке создать дублирующую услугу"""
    def __init__(self, title: str):
        self.title = title
        super().__init__(f"Service with title '{title}' already exists")


class InvalidPriceRangeError(ServiceValidationError):
    """Исключение при некорректном диапазоне цен"""
    def __init__(self, price_from: float, price_to: float):
        self.price_from = price_from
        self.price_to = price_to
        super().__init__(f"Invalid price range: from {price_from} to {price_to}") 