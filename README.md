## PTRF - Sistema de Gestão de Recursos Educacionais

Este projeto é uma aplicação web desenvolvida com **Django**, baseada em **Cookiecutter Django**, com suporte a execução via **Docker** ou ambiente local.


## SME-PTRF-BackEnd

Esse é o repositório de código da API da aplicação Sig-Escola, um sistema integrado de gestão que visa:

- Apoiar os processos de gestão e prestação de contas de recursos financeiros das unidades educacionais da Rede Municipal de Educação de São Paulo,
- Apoiar o acompanhamento e fiscalização dos referidos recursos pelas Diretorias Regionais de Educação,
- Auxiliar na gestão e avaliação dos programas de transferência de recursos por parte da Secretaria Municipal de Educação.

## Mais informações sobre o projeto

Você pode encontrar mais informações sobre o projeto e instruções detalhadas sobre como colaborar com a documentação na própria [documentação do SigEscola](https://sig-escola.sme.prefeitura.sp.gov.br/docs/). 

---

### 🚀 Tecnologias

- Django
- PostgreSQL
- Redis
- Celery
- Docker e Docker Compose

---

### ⚙️ Requisitos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)
- Python 3.12+
- PostgreSQL 11+
- Redis 5+

---

### 🔧 Configuração do Ambiente

#### 1. Criar arquivo `ENV`
Antes de configurar o ambiente da aplicação, copie o arquivo `env-sample` para `.env` e edite as variáveis de ambiente conforme os parâmetros locais.

Após isso, criar variável de ambiente para permitir o carregamento das variáveis do arquivo `.env` pelo projeto Django.

    $ export DJANGO_READ_DOT_ENV_FILE=1


#### 2. Criação de ambiente virtual

##### 2.1 Criação da venv

###### *Opção 1*. Utilizando `venv` (Requer instalação do `python3-venv`)

Criando a `venv`

    $ python -m venv venv

Ativando a `venv`:

    $ source venv/bin/activate


###### *Opção 2* . Utilizando `Pyenv` (Requer instalação do Pyenv)
Instalar a versão do Python (versão que consta no arquivo `Dockerfile`):

    $ pyenv install 3.12.9

Criando a `venv` ( _ptrf_ = nome da venv):

    $ pyenv virtualenv 3.12.9 ptrf

Ativando a `venv`:

    $ pyenv local ptrf


##### 2.2 Instalação de dependências:
Instalação dos pacotes Python via `pip`:

    $ pip install -r requirements/local.txt


##### 2.3 Subir o banco de dados:
Devido a disponibilidade de um arquivo `docker-compose.yml` é possível subir
um banco de dados em container, sem a necessidade de instalação de uma instância local.
- Requer procedimento da `Etapa 1` para as variáveis de ambiente:
```markdown
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_DB=
# utilize esta porta, é a mesma definida no arquivo docker-compose.yml para o container "db"
POSTGRES_PORT=5434
PGADMIN_DEFAULT_PASSWORD=
```

- Subir o driver de rede do arquivo `docker-compose.yml`:

    $ docker network create ptrf-network

- Subir o container de Banco de Dados:

    $ docker-compose up -d db

- Para confirmar se o banco de dados subiu corretamente, o container será listado no console:

    $ docker-compose ps

##### 2.4 Execução de migrations:
Aplicar as migrações no banco de dados:

    $ python manage.py migrate

##### 2.5 Coleção de arquivos estáticos:

    $ python manage.py collectstatic

##### 2.6 Criação de superusuário:
Após o comando abaixo, será exigida a senha e a confirmação de senha para o usuário admin

    $ python manage.py createsuperuser --username=admin --email=admin@admin.com

##### 2.7 Execução de Celery
Execução local do Celery Worker
- Requer instância do Redis executando. Basta informar nas variáveis do arquivo `.env`, como o exemplo abaixo:
```
REDIS_LOCATION=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
```

Executar o Celery:
```shell
    celery -A config.celery_app worker -l info
```
Importante: Certifique-se de que esteja no mesmo diretório do arquivo *manage.py*.


##### 2.8 Executa o servidor:
    $ python manage.py runserver

O Django Admin ficará acessível em [localhost](`http://localhost:8000/admin/`)


#### 3 Subir o Projeto utilizando Docker:
##### 3.1 Definir as variáveis de ambiente
Considere no arquivo `.env` as portas internas dos container de cada service do arquivo `docker-compose.yml`.
Para as variáveis do banco de dados, o Host deve referenciar o mesmo nome do *service* de banco de dados(`db`). Semelhantemente, o Redis(`redis_ptrf`).
```
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_LOCATION=redis://redis_ptrf:6379/0
REDIS_URL=redis://redis_ptrf:6379/0
```

##### 3.2 Criação de Superusuário
Se necessário, para criar superusuário com o backend executando em container:
```shell
docker-compose exec api_ptrf python manage.py createsuperuser --username=admin --email=admin@admin.com
```
De forma similar ao tópico `2.6`, será exigido a senha e a confirmação de senha para o superusuário.

##### 3.3 Subir os container`s
```shell
docker-compose build
docker-compose up
```

Também é possível verificar se todos os container`s subiram corretamente.
```shell
docker-compose ps
```
Deverá listar os services `api-ptrf`, `db`, `redis_ptrf` e `celery_ptrf`.

##### 3.4 Disponibilidade da aplicação
Observe que, conforme a porta definida no `docker-compose.yml`, a aplicação estará disponível na porta `8001` em [Localhost]('http://localhost:8001/')




#### 4. Execução de testes unitários

##### 4.1 Cobertura de testes com relatório.
    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

##### 4.2 Execução de testes sem cobertura.
    $ pytest

