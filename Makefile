# Development and deployment commands for Dev Digest

.PHONY: help install test clean run docker-build docker-run backup deploy

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies and setup project"
	@echo "  test         - Run test suite"
	@echo "  clean        - Clean temporary files"
	@echo "  run          - Run development server"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  backup       - Create database backup"
	@echo "  deploy       - Deploy to production"
	@echo "  sample-data  - Generate sample data for testing"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	python setup.py

test:
	@echo "Running tests..."
	python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage

run:
	@echo "Starting development server..."
	python -m app.main

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-run:
	@echo "Running with Docker Compose..."
	docker-compose up -d

backup:
	@echo "Creating database backup..."
	python scripts/backup.py

deploy:
	@echo "Deploying to production..."
	python scripts/deploy.py deploy

sample-data:
	@echo "Generating sample data..."
	python scripts/generate_sample_data.py