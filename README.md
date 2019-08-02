# Тестовое задание REST-сервис на Python

Описание: [документ 1](https://yadi.sk/i/bE-gmumaIDcPGg), [документ 2](https://yadi.sk/i/dA9umaGbQdMNLw)

# Установка

## Установка pip

```shell
sudo apt install python3-pip
```

## Установка MongoDB

```shell
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

## mongodb.service

```shell
sudo nano /etc/systemd/system/mongodb.service
```

```
[Unit]
Description=High-performance, schema-free document-oriented database
After=network.target

[Service]
User=mongodb
ExecStart=/usr/bin/mongod --quiet --config /etc/mongod.conf

[Install]
WantedBy=multi-user.target
```

```shell
sudo systemctl start mongodb
sudo systemctl enable mongodb
sudo systemctl status mongodb
```

## Установка restapi

```shell
git clone https://github.com/egorchistov/restapi
cd restapi
python3 -m venv venv
. venv/bin/activate
pip install -e .
deactivate
```

## restapi.service

```shell
sudo nano /etc/systemd/system/restapi.service
```

```
[Unit]
Description=Gunicorn instance to serve restapi
After=network.target
Requires=mongodb.service

[Service]
User=entrant
WorkingDirectory=/home/entrant/restapi
Environment="PATH=/home/entrant/restapi/venv/bin"
Environment="MONGO_DB_NAME=prod"
ExecStart=/home/entrant/restapi/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 "api:create_app()"

[Install]
WantedBy=multi-user.target
```

```shell
sudo systemctl start restapi
sudo systemctl enable restapi
sudo systemctl status restapi
```

# Переменные окружения:

+ MONGO_URI
+ MONGO_DB_NAME

# Windows: Тесты и сервер для разработки

```shell
venv/Scripts/activate
set FLASK_APP=api
set FLASK_ENV=development
coverage run -m pytest
coverage html
start htmlcov/index.html
python -m flask run
```
