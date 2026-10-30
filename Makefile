.PHONY: help dev test eval build run

help:
	@echo "Emend development commands:"
	@echo "  make dev      - Run backend and frontend concurrently"
	@echo "  make test     - Run unit test suite"
	@echo "  make eval     - Run automated evaluation harness"
	@echo "  make build    - Build production Docker image"
	@echo "  make run      - Run Docker container on port 7860"

dev:
	python -m uvicorn emend.api.main:app --reload --port 8000

test:
	pytest backend/tests/

eval:
	python eval/run_eval.py

build:
	docker build -t emend .

run:
	docker run --rm -p 7860:7860 --env-file .env emend
