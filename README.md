# Тестовое задание REST-сервис на Python

# Попробовать

Сервис равзвернут на https://egorchistov-restapi.herokuapp.com

## Методы

 * POST /imports

 * PATCH /imports/$import_id/citizens/$citizen_id

 * GET /imports/$import_id/citizens

 * GET /imports/$import_id/citizens/birthdays

 * GET /imports/$import_id/towns/stat/percentile/age

## Описание api

 * [версия 1](https://yadi.sk/i/bE-gmumaIDcPGg)
 * [версия 2](https://yadi.sk/i/dA9umaGbQdMNLw)

# Запуск сервера для разработки

Развернуть базу данных mongodb (например с помощью docker)

```shell script
docker run                                \
--env MONGO_INITDB_ROOT_USERNAME="me"     \
--env MONGO_INITDB_ROOT_PASSWORD="hackme" \
--name "restapi_dev"                      \
-d                                        \
-p 27017:27017                            \
mongo:4.4.0-bionic
```

Склонировать репозиторий

```shell script
git clone git@github.com:egorchistov/restapi.git

cd restapi
```

Установить зависимости

```shell script
poetry install
poetry shell
```

Запустить сервер для разработки

```shell script
env MONGO_URI="mongodb://me:hackme@localhost:27017/" \
env MONGO_DBNAME="dev"                               \
gunicorn "api:create_app()"
```

Тесты и инструменты для анализа кода

```shell script
flake8

mypy --ignore-missing-imports .

env MONGO_URI="mongodb://me:hackme@localhost:27017/" \
env MONGO_TESTDBNAME="test"                          \
coverage run --source api -m pytest

coverage report -m
```

При необходимости можно очистить базу данных от записей

```shell script
env MONGO_URI="mongodb://me:hackme@localhost:27017/" \
env MONGO_DBNAME="dev"                               \
env FLASK_APP="api"                                  \
python -m flask drop-db
```

# Деплой на Heroku

Необходимые для деплоя файлы могут быть получены с помощью следующих комманд

```shell script
echo 'python-3.8.5' > runtime.txt
poetry export -f requirements.txt -o requirements.txt
echo 'web gunicorn "api:create_app()"' > Procfile
```
