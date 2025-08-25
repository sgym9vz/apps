# Variables
PROJECT_NAME ?= django_intmd
APP_NAME ?= matching_app
USER_NAME ?= admin
SRC = .
TEST_PASS ?= matching_app.tests

# Phony targets
.PHONY: build up down restart reset reset-all migrations migrate test create-superuser django-shell run-mysql-cli prettier help

# Commands
build: ## Build the Docker images
	docker compose build

up: ## Run the development server with docker-compose
	docker compose up -d

down: ## Clear the containers
	docker compose down

restart: ## Restart django container
	docker compose restart django
	docker compose restart channels
	docker compose restart nginx

reset: ## Clear containers and build the images and run the development server
	docker compose down
	docker compose build
	docker compose up -d

reset-all: ## Clear and rebuild all containers, database and run the development server
	docker compose down -v
	docker compose build
	docker compose up -d
	docker compose exec django python manage.py migrate
	make loaddata

migrations: ## Create the migrations for new models
	docker compose exec django python manage.py makemigrations

migrate: ## Migrate the database
	docker compose exec django python manage.py migrate

loaddata: ## Load Fixtures
	docker compose exec django python manage.py loaddata user_fixtures.json recruitment_fixtures.json

test: ## Run all tests in the Django project
	docker compose exec django python manage.py test --settings=django_intmd.settings.test

target-test: ## Run specific test like `make target-test TARGET=test_views.TestViews.test_login_view`
	docker compose exec django python manage.py test $(TEST_PASS).$(TARGET) --settings=django_intmd.settings.test

createsuperuser: ## Create a superuser
	docker compose exec django python manage.py createsuperuser

django-shell: ## Run django shell
	docker compose exec django python manage.py shell

run-mysql-cli: ## Run mysql cli
	docker compose run mysql-cli

run-redis-cli: ## Run redis cli
	docker compose run redis-cli

# Style
prettier: ## Prettier
	docker compose exec django isort $(SRC)
	docker compose exec django black --line-length 120 $(SRC)
	docker compose exec django flake8 $(SRC)

# Help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
