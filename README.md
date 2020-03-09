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

(Автоматически запускает линтер и тесты)

## Docker-compose

```shell script
docker-compose up --build --abort-on-container-exit
```

## Docker

```shell script
docker build . --target dev -t restapi
docker run -p 8080:8080 \
--env MONGO_URI="Uri of your mongodb base" \
--env MONGO_DBNAME="Name of database" \
--env MONGO_TESTDBNAME="Name of database for tests. It will be dropped after the tests" \
-v $(pwd)/api:/opt/restapi/api:ro \
restapi
```

## Вручную

```shell script
export FLASK_APP=api
export FLASK_ENV=development
export MONGO_URI="Uri of your mongodb base"
export MONGO_DBNAME="Name of database"
export MONGO_TESTDBNAME="Name of database for tests. It will be dropped after the tests"

python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt -r requirements.tests.txt

pylama
mypy --ignore-missing-imports api tests
coverage run --source api -m pytest && coverage report -m
python -m flask run --host=0.0.0.0 -p 8080
```

# Cброс базы данных

## Docker

```shell script
docker exec restapi_dev_1 python -m flask drop-db
```
`restapi_dev_1` - имя контейнера с приложением

## Локально

```shell script
python -m flask drop-db
```

# Деплой

## Docker

```shell script
docker build . --target prod -t restapi
docker run -p 8080:8080 \
--env MONGO_URI="Uri of your mongodb base" \
--env MONGO_DBNAME="Name of database" \
restapi
```

## Вручную

```shell script
export MONGO_URI="Uri of your mongodb base"
export MONGO_DBNAME="Name of database"

python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

gunicorn "api:create_app()"
```
