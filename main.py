import argparse
import json
import sys

from exceptions import CityNotFoundError, CurrencyNotFoundError, ExternalServiceError
from processing.service import build_city_summary

EXIT_OK = 0
EXIT_BAD_ARGUMENTS = 2
EXIT_NOT_FOUND = 3
EXIT_SERVICE_UNAVAILABLE = 4


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Сводка по городу: погода и курс валюты к рублю."
    )
    parser.add_argument(
        "--city", required=True, help="название города, например Moscow"
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="ISO-код валюты, по умолчанию USD",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="вывести сводку в формате JSON",
    )
    args = parser.parse_args(argv)
    if not args.city.strip():
        parser.error("--city не должен быть пустым")
    return args


def format_summary(summary: dict) -> str:
    weather = summary["weather"]
    rates = summary["rates"]
    warm = "да" if weather["warm_clothes"] else "нет"
    expensive = "да" if rates["expensive"] else "нет"
    return "\n".join(
        [
            f"Город: {summary['city']}",
            f"Погода: {weather['temp_c']}°C, {weather['description']}",
            f"Тёплая одежда: {warm}",
            f"{rates['currency']}→RUB: {rates['rate_to_rub']}",
            f"Дорогой курс: {expensive}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_city_summary(args.city.strip(), args.currency)
    except CityNotFoundError as exc:
        print(f"Город не найден: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except CurrencyNotFoundError as exc:
        print(f"Код валюты не найден: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except ExternalServiceError as exc:
        print(f"Внешний сервис недоступен: {exc}", file=sys.stderr)
        return EXIT_SERVICE_UNAVAILABLE

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(format_summary(summary))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
