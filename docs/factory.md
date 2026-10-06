# Подключение к Dark Factory

Решения журнала: decisions/026 и 027. Состояние на 2026-10-06.

Код ядра от Factory не зависит (decisions/027): это заметка для
разработки самой Factory, а не требование к проекту.

## Что мешает сейчас

Factory проверяет только проекты на Node.js: песочница собирается из
`node:22-alpine` по `package.json` и `package-lock.json`
(`prototype/factory_core/sandbox_images.py`), а подключение проекта без
`package.json` спрашивает, как запускать проверки
(`prototype/factory_core/onboard.py`). Этот проект на Python.

## Что добавить в Factory (задача для разработки самой Factory)

1. **Образ для Python-проекта.** Если в ревизии есть `pyproject.toml` и
   `uv.lock` (и нет `package.json`): образ на `python:3.12-slim` + `git`,
   `bash`; зависимости ставятся в системный Python из `uv.lock`
   (`uv export --frozen --no-hashes` → `uv pip install --system`). Тег —
   хеш Dockerfile, `pyproject.toml` и `uv.lock`, как у npm-образа. Сеть
   нужна только при сборке.
2. **Проверки без `uv run`.** Песочница без сети и с файловой системой
   только для чтения, а `uv run` пытается синхронизировать `.venv`. Поэтому
   проверки — прямые вызовы `python -m …` (см. профиль ниже).
3. **Подключение проекта.** `onboard.py`: распознать `pyproject.toml` +
   `uv.lock`, предложить проверки из профиля ниже, защищённые пути
   `pyproject.toml`, `uv.lock`, `.github/`.
4. **Тяжёлые зависимости.** Docling, torch и sentence-transformers делают
   образ большим (несколько ГБ, предположение). В песочнице нужны только
   тесты с меткой «не mac и не model»; при необходимости вынести тяжёлые
   пакеты в отдельную группу зависимостей и не ставить их в образ проверок.
5. **Скрытые сценарии.** Эталоны `eval/gold/` (адреса единиц, нужные
   единицы по вопросам, «искать / не искать») хранить в
   `holdout/talkresearchcore/`, а не в репозитории, чтобы агент не
   подгонял код под ответы.

## Черновик профиля `projects/talkresearchcore.json`

Поля — по образцу `projects/expirationtracker.json`. Путь — локальная копия
этого репозитория у Алекса (клонировать заранее).

| Поле | Значение |
|---|---|
| id | `talkresearchcore` |
| repo_path | `C:/Users/Alex/Documents/Codex/talk-to-research-core` |
| base_ref | `origin/main` |
| context_docs | `AGENTS.md`, `docs/PLAN.md` |
| plannable_paths | `core/`, `cli/`, `web/`, `tests/` |
| protected_paths | `.github/`, `pyproject.toml`, `uv.lock`, `eval/testset-by/`, `docs/PLAN.md`, `docs/journal.md` |
| checks | `lint`: `python -m ruff check .`; `types`: `python -m mypy core cli`; `tests`: `python -m pytest -q -m "not mac and not model"` (по 600 с) |
| test_paths | `tests/` |
| github | `octoalx/talk-to-research-core`, ветка `main` |
| review.only_paths | `core/answer/`, `core/search/` (проверка цитат и поиск — главное в продукте) |
| holdout | `holdout/talkresearchcore` |
| остальное | как у ExpirationTracker (лимиты, модель ревью) |

## Как резать вехи плана на цели

Одна цель Factory — одна-две функции с тестами. Пример для M3:
1. «Найти нумерацию пунктов и статей в тексте» (адреса 1., 2.3., «Статья 15»).
2. «Собрать дерево единиц с родителями и адресами».
3. «Шапка контекста для каждой единицы».
4. «Автопроверка разбора и пометка „разобран с ошибками“».

Замеры на Mac (M1, скорость индексации M5, прогоны M6–M9 с настоящей
моделью) Factory готовит как скрипты; запускает Алекс на MacBook, отчёт —
в `docs/results/`.
