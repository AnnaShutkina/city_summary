import re

from clients.http import get, get_json_object
from exceptions import CurrencyNotFoundError, ExternalServiceError

RATE_URL = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"
CURRENCY_PATTERN = re.compile(r"[A-Z]{3}")


def get_rate(currency: str) -> float:
    """Курс валюты к рублю: сколько рублей стоит одна единица валюты."""
    code = currency.strip().upper()
    if not CURRENCY_PATTERN.fullmatch(code):
        raise CurrencyNotFoundError(code)

    response = get(RATE_URL.format(currency=code))
    if response.status_code in (404, 422):
        raise CurrencyNotFoundError(code)
    if response.status_code != 200:
        raise ExternalServiceError(f"Курсы валют: HTTP {response.status_code}")

    data = get_json_object(response, "Курсы валют")
    rate = data.get("rate")
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or rate <= 0:
        raise ExternalServiceError("Курсы валют: в ответе нет корректного поля rate")
    return float(rate)
