# Тестовое задание REST-сервис на Python

Описание: [документ 1](https://yadi.sk/i/bE-gmumaIDcPGg), [документ 2](https://yadi.sk/i/dA9umaGbQdMNLw)

# Установка

```shell
> git clone https://github.com/egorchistov/restapi
> cd restapi
> python3 -m venv venv
> . venv/bin/activate
> pip install -e .
> cd ..
> gunicorn -w 1 -b 0.0.0.0:8080 --worker-class gevent api:app
```

# Переменные окружения:

+ MONGO_URI
+ MONGO_DB_NAME
+ FLASK_ENV

# Запуск для разработки на Windows:

```shell
> venv/bin/activate
> set FLASK_APP=api
> set FLASK_ENV=development
> pytest -vv --durations=0
> python -m flask run
```
