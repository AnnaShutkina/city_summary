from clients.http import get, get_json_object
from exceptions import CityNotFoundError, ExternalServiceError

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

# MET Norway требует User-Agent с названием приложения и контактом.
USER_AGENT = (
    "city_summary/1.0 (student project; https://github.com/AnnaShutkina/city_summary)"
)

# Названия погоды MET Norway (symbol_code без суффикса _day/_night).
SYMBOL_DESCRIPTIONS = {
    "clearsky": "clear sky",
    "fair": "fair",
    "partlycloudy": "partly cloudy",
    "cloudy": "cloudy",
    "fog": "fog",
    "lightrain": "light rain",
    "rain": "rain",
    "heavyrain": "heavy rain",
    "lightrainshowers": "light rain showers",
    "rainshowers": "rain showers",
    "heavyrainshowers": "heavy rain showers",
    "lightsleet": "light sleet",
    "sleet": "sleet",
    "heavysleet": "heavy sleet",
    "lightsnow": "light snow",
    "snow": "snow",
    "heavysnow": "heavy snow",
    "lightsnowshowers": "light snow showers",
    "snowshowers": "snow showers",
    "heavysnowshowers": "heavy snow showers",
    "rainandthunder": "rain and thunder",
    "heavyrainandthunder": "heavy rain and thunder",
    "sleetandthunder": "sleet and thunder",
    "snowandthunder": "snow and thunder",
}
DAY_NIGHT_SUFFIXES = ("_day", "_night", "_polartwilight")


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _dig(data: object, *keys: str) -> object:
    """Достаёт вложенное значение; если на пути что-то не словарь, вернёт None."""
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _describe_symbol(symbol_code: str) -> str:
    name = symbol_code
    for suffix in DAY_NIGHT_SUFFIXES:
        name = name.removesuffix(suffix)
    return SYMBOL_DESCRIPTIONS.get(name, name)


def _find_coordinates(city: str) -> tuple[float, float]:
    """Геокодинг: название города -> (широта, долгота)."""
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    response = get(GEOCODING_URL, params=params)
    if response.status_code != 200:
        raise ExternalServiceError(f"Геокодинг: HTTP {response.status_code}")

    data = get_json_object(response, "Геокодинг")
    results = data.get("results")
    if not results:  # ключа нет или список пустой: такого города не нашли
        raise CityNotFoundError(city)
    if not isinstance(results, list) or not isinstance(results[0], dict):
        raise ExternalServiceError("Геокодинг: неожиданный формат поля results")

    latitude = results[0].get("latitude")
    longitude = results[0].get("longitude")
    if not _is_number(latitude) or not _is_number(longitude):
        raise ExternalServiceError("Геокодинг: в ответе нет координат")
    return float(latitude), float(longitude)


def get_weather(city: str) -> dict:
    """Текущая погода в городе: {"temp_c": float, "description": str}."""
    latitude, longitude = _find_coordinates(city)

    # MET Norway просит не больше 4 знаков после запятой.
    params = {"lat": round(latitude, 4), "lon": round(longitude, 4)}
    response = get(FORECAST_URL, params=params, headers={"User-Agent": USER_AGENT})
    if response.status_code != 200:
        raise ExternalServiceError(f"Прогноз погоды: HTTP {response.status_code}")

    data = get_json_object(response, "Прогноз погоды")
    timeseries = _dig(data, "properties", "timeseries")
    if not isinstance(timeseries, list) or not timeseries:
        raise ExternalServiceError("Прогноз погоды: в ответе нет списка timeseries")

    now = timeseries[0]  # первая запись: ближайший к текущему час
    temp_c = _dig(now, "data", "instant", "details", "air_temperature")
    if not _is_number(temp_c):
        raise ExternalServiceError("Прогноз погоды: нет температуры air_temperature")

    symbol = _dig(now, "data", "next_1_hours", "summary", "symbol_code")
    if not isinstance(symbol, str):
        symbol = _dig(now, "data", "next_6_hours", "summary", "symbol_code")
    description = _describe_symbol(symbol) if isinstance(symbol, str) else ""

    return {"temp_c": float(temp_c), "description": description}
