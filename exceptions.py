class CitySummaryError(Exception):
    """Базовое исключение приложения."""


class CityNotFoundError(CitySummaryError):
    """Город не найден."""


class CurrencyNotFoundError(CitySummaryError):
    """Код валюты не найден."""


class ExternalServiceError(CitySummaryError):
    """Внешний сервис недоступен или вернул неожиданный ответ."""
