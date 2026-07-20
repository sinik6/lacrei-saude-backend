.PHONY: help test lint

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Desenvolvimento ──────────────────────────────────────────────

install: ## Instala dependências
	poetry install

run: ## Inicia servidor de desenvolvimento
	poetry run python manage.py runserver

test: ## Roda testes via Django (APITestCase nativo)
	poetry run python manage.py test --settings=config.settings_test -v2

test-cov: ## Roda testes com cobertura
	poetry run pytest --cov=. --cov-report=term --cov-report=html

lint: ## Roda linter
	poetry run ruff check .

format: ## Formata código
	poetry run ruff format .

fix: ## Auto-corrige problemas de lint
	poetry run ruff check --fix .

# ── Django ───────────────────────────────────────────────────────

migrate: ## Executa migrações
	poetry run python manage.py migrate

makemigrations: ## Gera novas migrações
	poetry run python manage.py makemigrations

seed: ## Popula banco com dados de exemplo
	poetry run python manage.py seed

api-key: ## Cria nova API Key (use NAME="meu-nome")
	poetry run python manage.py create_api_key --nome $(NAME)

shell: ## Abre Django shell
	poetry run python manage.py shell

# ── Docker ───────────────────────────────────────────────────────

docker-build: ## Build da imagem Docker
	docker build -t lacrei-saude-api .

docker-up: ## Sobe ambiente com Docker
	docker compose -f docker-compose.dev.yml up --build -d

docker-down: ## Derruba ambiente Docker
	docker compose -f docker-compose.dev.yml down

docker-logs: ## Logs do container web
	docker compose -f docker-compose.dev.yml logs -f web
