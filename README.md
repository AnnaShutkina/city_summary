# City Summary

CLI-утилита «Сводка по городу». Получает из внешних API текущую погоду в выбранном городе и курс валюты к рублю, применяет простые правила и печатает сводку в консоль.

Внешние сервисы:

- погода: [MET Norway](https://api.met.no/) (прогноз) и геокодинг [Open-Meteo](https://open-meteo.com/en/docs/geocoding-api) для поиска города (ключи не нужны);
- курс валюты: [Frankfurter](https://frankfurter.dev/).

## Требования

- Python 3.12
- Git

## Установка

```bash
git clone https://github.com/AnnaShutkina/city_summary.git
cd city_summary
python -m venv .venv
```

Активация окружения:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS / Linux: `source .venv/bin/activate`

Установка зависимостей:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py --city Moscow
```

Другая валюта (по умолчанию USD):

```bash
python main.py --city Moscow --currency EUR
```

Вывод в формате JSON:

```bash
python main.py --city Moscow --json
```

Пример вывода:

```text
Город: Moscow
Погода: -3.2°C, clear sky
Тёплая одежда: да
USD→RUB: 92.15
Дорогой курс: нет
```

## Правила предобработки

- температура ниже 0 °C: `warm_clothes: true`;
- курс выше 100: `expensive: true`;
- пустое описание погоды заменяется на `no description`.

## Коды выхода

| Код | Значение |
| --- | --- |
| 0 | успех |
| 2 | ошибка аргументов |
| 3 | город или код валюты не найден |
| 4 | внешний сервис недоступен после повторов |

## Структура проекта

- `main.py` — CLI: аргументы, вывод, коды выхода;
- `exceptions.py` — исключения приложения;
- `clients/` — общение с внешними API (timeout, retry, проверка ответов);
- `processing/` — правила предобработки и сборка сводки;
- `tests/` — автотесты (`python -m unittest`).