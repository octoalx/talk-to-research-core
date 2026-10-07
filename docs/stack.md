# Стек и версии

Проверено 2026-10-07 (веха M0), версии — из `uv.lock`.

| Что | Версия | Группа | Зачем |
|---|---|---|---|
| Python | 3.12 | — | язык ядра |
| fastapi / uvicorn | 0.142.2 / 0.54.0 | основная | API ядра и интерфейс (M9) |
| openai | 3.26.0 | основная | клиент OpenAI-совместимого сервера модели: Ollama, MLX (M1, M7, M8) |
| httpx | 0.28.1 | основная | HTTP: pravo.by (M4), тесты API |
| sqlite-vec | 0.1.9 | основная | векторы в SQLite (M5) |
| pymorphy3 + словари ru | 2.0.6 | основная | лемматизация русского для FTS5 (M5) |
| beautifulsoup4 / lxml | 4.15.0 / 6.1.3 | основная | разбор страниц актов (M4) |
| pyyaml | 6.0.3 | основная | эталоны `eval/gold/` |
| ruff / mypy / pytest | 0.16.10 / 2.4.0 / 9.1.1 | dev | проверки |
| docling | 2.135.0 | heavy | разбор PDF/DOCX (M2) |
| sentence-transformers (torch 2.14.1) | 6.1.0 | heavy | bge-m3 и reranker на машине разработчика (M5, M6) |

## Установка

- Разработка на Mac: `uv sync --group heavy` (всё), проверки — `make check`.
- Песочница Factory и CI: только основная группа и dev (`uv export --frozen --no-hashes`),
  тяжёлая группа не ставится (decisions/028 журнала). Окружение без heavy — около 150 МБ.

## Проверено

- `make check` (ruff, mypy strict, pytest) — 9 тестов, Linux, Python 3.12.3.
- Те же проверки в чистом окружении из `uv.lock` без сети (`unshare -n`): проходят.
- SQLite из Python 3.12 загружает sqlite-vec (`enable_load_extension`), FTS5 работает.

## НЕ проверено

- macOS: загрузка sqlite-vec в Python от `uv` на Mac (системный Python на macOS расширения не грузит).
  Проверить командой `python -m cli.main check`; если упадёт — взять Python из Homebrew и записать здесь.
- Установка группы `heavy` (docling, torch) на Mac M4 и её размер.
- Сборка образа Factory (`factory-py-sandbox`) из этого `uv.lock`.
