.PHONY: help test lint build docker-up docker-down deploy-staging deploy-prod

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Desenvolvimento ──────────────────────────────────────────────

install: ## Instala dependências
	poetry install

run: ## Inicia servidor de desenvolvimento
	poetry run python manage.py runserver

test: ## Roda todos os testes
	poetry run pytest -v

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

docker-up: ## Sobe ambiente Docker (produção)
	docker compose up --build -d

docker-down: ## Derruba ambiente Docker
	docker compose down

docker-dev: ## Sobe ambiente dev com hot reload
	docker compose -f docker-compose.dev.yml up --build -d

docker-logs: ## Logs do container web
	docker compose logs -f web

# ── AWS / Deploy ─────────────────────────────────────────────────

aws-auth: ## Autentica no ECR
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR)

deploy-staging: docker-build ## Build e push para staging
	$(eval ECR := $(shell aws ecr describe-repositories --repository-names lacrei-saude-api-staging --query 'repositories[0].repositoryUri' --output text))
	docker tag lacrei-saude-api:latest $(ECR):$$(git rev-parse --short HEAD)
	docker push $(ECR):$$(git rev-parse --short HEAD)
	aws ecs update-service --cluster lacrei-saude-api-staging --service lacrei-saude-api-staging --force-new-deployment

deploy-prod: docker-build ## Build e push para produção
	$(eval ECR := $(shell aws ecr describe-repositories --repository-names lacrei-saude-api-production --query 'repositories[0].repositoryUri' --output text))
	docker tag lacrei-saude-api:latest $(ECR):$$(git rev-parse --short HEAD)
	docker push $(ECR):$$(git rev-parse --short HEAD)
	aws ecs update-service --cluster lacrei-saude-api-production --service lacrei-saude-api-production --force-new-deployment

# ── Terraform ────────────────────────────────────────────────────

tf-init: ## Inicializa Terraform
	cd infra/terraform && terraform init

tf-plan-staging: ## Planeja deploy staging
	cd infra/terraform && terraform plan -var="environment=staging"

tf-apply-staging: ## Aplica deploy staging
	cd infra/terraform && terraform apply -var="environment=staging"

tf-plan-prod: ## Planeja deploy produção
	cd infra/terraform && terraform plan -var="environment=production"

tf-apply-prod: ## Aplica deploy produção
	cd infra/terraform && terraform apply -var="environment=production"
