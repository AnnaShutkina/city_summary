WARM_CLOTHES_BELOW_C = 0
EXPENSIVE_RATE_ABOVE = 100
DEFAULT_DESCRIPTION = "no description"


def needs_warm_clothes(temp_c: float) -> bool:
    return temp_c < WARM_CLOTHES_BELOW_C


def is_expensive(rate: float) -> bool:
    return rate > EXPENSIVE_RATE_ABOVE


def normalize_description(description: str | None) -> str:
    """Пустое описание погоды заменяем значением по умолчанию."""
    cleaned = (description or "").strip()
    return cleaned or DEFAULT_DESCRIPTION


def preprocess_weather(weather: dict) -> dict:
    return {
        "temp_c": weather["temp_c"],
        "description": normalize_description(weather.get("description")),
        "warm_clothes": needs_warm_clothes(weather["temp_c"]),
    }


def preprocess_rate(currency: str, rate: float) -> dict:
    return {
        "currency": currency,
        "rate_to_rub": rate,
        "expensive": is_expensive(rate),
    }
