# Тестовое задание REST-сервис на Python

# Попробовать

 * [Интерактивная документация](https://egorchistov-restapi.herokuapp.com/docs)
 * [ТЗ версия 1](https://yadi.sk/i/bE-gmumaIDcPGg)
 * [ТЗ версия 2](https://yadi.sk/i/dA9umaGbQdMNLw)

# Запуск сервера для разработки

Развернуть базу данных mongodb (например с помощью docker)

```shell script
docker run                                \
--env MONGO_INITDB_ROOT_USERNAME="me"     \
--env MONGO_INITDB_ROOT_PASSWORD="hackme" \
--name "restapi_dev"                      \
-d                                        \
-p 27017:27017                            \
mongo:latest
```

Склонировать репозиторий

```shell script
git clone git@github.com:egorchistov/restapi.git

cd restapi
```

Настроить локальную среду

```shell script
python -m venv venv
. ./venv/bin/activate
```

Установить зависимости

```shell script
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

Запустить сервер для разработки

```shell script
env MONGO_URI="mongodb://me:hackme@localhost:27017/" \
env MONGO_DBNAME="dev"                               \
uvicorn "api:app" --reload
```

Тесты и инструменты для анализа кода

```shell script
isort .

flake8

mypy --ignore-missing-imports .

env MONGO_URI="mongodb://me:hackme@localhost:27017/" \
env MONGO_DBNAME="test"                              \
coverage run --source api -m pytest

coverage report -m
```

# Деплой на Heroku

Необходимые для деплоя файлы могут быть получены с помощью следующих комманд

```shell script
echo 'python-3.9.5' > runtime.txt
echo 'web: uvicorn "api:app" --host=0.0.0.0 --port $PORT' > Procfile
```
