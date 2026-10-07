# Проверки те же, что запускает Factory в песочнице (docs/factory.md):
# без сети, без кэшей на диске, без тестов, которым нужен Mac или настоящая модель.
PY ?= python
export PYTHONDONTWRITEBYTECODE=1

.PHONY: check lint types test

check: lint types test

lint:
	$(PY) -m ruff check --no-cache .

types:
	$(PY) -m mypy --cache-dir=/tmp/mypy core cli

test:
	$(PY) -m pytest -p no:cacheprovider -q -m "not mac and not model"
