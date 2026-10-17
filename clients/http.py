import time
from typing import Any

import requests

from exceptions import ExternalServiceError

TIMEOUT_SECONDS = 10
MAX_RETRIES = 2  # повторы после первой попытки (всего попыток: 3)
RETRY_STATUSES = {500, 502, 503, 504}
BACKOFF_SECONDS = 1
MAX_RETRY_AFTER_SECONDS = 30


def _retry_after_seconds(response: requests.Response) -> float:
    """Числовой Retry-After из ответа 429; если его нет, обычная пауза."""
    value = response.headers.get("Retry-After", "")
    try:
        seconds = float(value)
    except ValueError:
        return BACKOFF_SECONDS
    return min(max(seconds, 0), MAX_RETRY_AFTER_SECONDS)


def get(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> requests.Response:
    """GET-запрос с timeout и повторами.

    Повторяем при Timeout, ConnectionError, 500/502/503/504 и 429.
    Остальные ответы (200, 404 и т. д.) возвращаем как есть.
    """
    attempts = MAX_RETRIES + 1
    last_error = "неизвестная ошибка"

    for attempt in range(1, attempts + 1):
        pause = BACKOFF_SECONDS
        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=TIMEOUT_SECONDS
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            last_error = f"{type(exc).__name__}"
        except requests.exceptions.RequestException as exc:
            raise ExternalServiceError(f"Ошибка запроса к {url}: {exc}") from exc
        else:
            if response.status_code == 429:
                last_error = "HTTP 429 (слишком много запросов)"
                pause = _retry_after_seconds(response)
            elif response.status_code in RETRY_STATUSES:
                last_error = f"HTTP {response.status_code}"
            else:
                return response

        if attempt < attempts:
            time.sleep(pause)

    raise ExternalServiceError(
        f"Сервис {url} недоступен после {attempts} попыток: {last_error}"
    )


def get_json_object(response: requests.Response, service: str) -> dict[str, Any]:
    """Достаёт из ответа JSON-объект (словарь) или бросает понятную ошибку."""
    try:
        data = response.json()
    except ValueError as exc:
        raise ExternalServiceError(f"{service}: ответ не является JSON") from exc
    if not isinstance(data, dict):
        raise ExternalServiceError(f"{service}: ожидался JSON-объект")
    return data
