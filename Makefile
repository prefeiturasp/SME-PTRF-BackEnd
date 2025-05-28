# Modo: local (venv) ou docker
MODE ?= local
COMMANDDOCKER := docker-compose 

# Como chamar o manage.py conforme o modo
ifeq ($(MODE), docker)
    SCRIPT = $(COMMANDDOCKER) exec $(SERVICE)
else
    SCRIPT ?= 
endif

build: ## Realiza o build dos containers
	$(COMMANDDOCKER) build

collect: ## Realiza o build dos containers
	$(SCRIPT) python manage.py collectstatic --noinput

coverage: SERVICE = api_ptrf
coverage: ## Executa a cobertura de testes unitários e gera relatório na pasta htmlcov/index.html
	$(SCRIPT) coverage run -m pytest

coverage-html: SERVICE = api_ptrf
coverage-html: ## Executa a cobertura de testes unitários e gera relatório na pasta htmlcov/index.html
	$(SCRIPT) coverage html

coverage-report: SERVICE = api_ptrf
coverage-report: ## Executa a cobertura de testes unitários e gera relatório no próprio terminal
	$(SCRIPT) coverage report

down: ## Para todos os containers do docker-compose
	$(COMMANDDOCKER) down

downv: ## Para todos os containers do docker-compose e remove os volumes
	$(COMMANDDOCKER) down -v

logs: ## Lista os logs dos serviços
	$(COMMANDDOCKER) logs

logs-celery: SERVICE = celery_ptrf
logs-celery: ## Lista os logs do celery
	$(COMMANDDOCKER) logs $(SERVICE)

logs-db: SERVICE = db
logs-db: ## Lista os logs do banco de dados
	$(COMMANDDOCKER) logs $(SERVICE)

logs-django: SERVICE = api_ptrf
logs-django: ## Lista os logs do django
	$(COMMANDDOCKER) logs $(SERVICE)

logs-redis: SERVICE = redis_ptrf
logs-redis: ## Lista os logs do redis
	$(COMMANDDOCKER) logs $(SERVICE)

makemigrations: SERVICE = api_ptrf
makemigrations: ## Cria as migrações
	$(SCRIPT) python manage.py makemigrations

migrate: SERVICE = api_ptrf
migrate: ## Aplica as migrações
	$(SCRIPT) python manage.py migrate

ps: ## Lista os serviços ativos
	$(COMMANDDOCKER) ps

pytest: SERVICE = api_ptrf
pytest: ## Executa os testes unitários
	$(SCRIPT) pytest

run: ## Inicia o servidor da aplicação local
	python manage.py runserver

superuser: SERVICE = api_ptrf
superuser: ## Cria o superusuário do sistema
	$(SCRIPT) python manage.py createsuperuser

shell: SERVICE = api_ptrf
shell: ## Acessa o shell do python no Django
	$(SCRIPT) python manage.py shell

up: ## Sobe os containers e lista os serviços ativos
	$(COMMANDDOCKER) up -d && $(COMMANDDOCKER) ps

up-db: ## Sobe apenas o banco de dados
	$(COMMANDDOCKER) up -d db

upgrade-local: ## Atualiza os pacotes pip do requirements/local.txt
	$(SCRIPT) pip install -r requirements/local.txt

help:
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
