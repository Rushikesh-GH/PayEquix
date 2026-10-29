.PHONY: install generate seed validate evaluate test backend frontend run all

install:
	cd backend && python -m pip install -r requirements.txt
	cd frontend && npm install

generate:
	python scripts/generate_data.py --profile full --seed 20261022

seed:
	python scripts/seed_database.py

validate:
	python scripts/validate_data.py

evaluate:
	python scripts/calculate_metrics.py

repro:
	python scripts/check_reproducibility.py --profile starter

test:
	python -m pytest backend/tests -v

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

all: generate seed validate evaluate test
