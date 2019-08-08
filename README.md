# Тестовое задание REST-сервис на Python

Описание: [документ 1](https://yadi.sk/i/bE-gmumaIDcPGg), [документ 2](https://yadi.sk/i/dA9umaGbQdMNLw)

# Установка для Ubuntu 18.04

Перед установкой нужно создать deploy key

```shell
cd ~
git clone git@github.com:egorchistov/restapi.git
sh ~/restapi/scripts/install.sh
```

# Запуск тестов

```shell
cd ~/restapi
. venv/bin/activate
coverage run -m pytest
coverage report
```

# Запуск сервера для разработки

```shell
cd ~/restapi
. venv/bin/activate
export FLASK_APP=api
export FLASK_ENV=development
python3.7 -m flask run
```
