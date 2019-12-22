# Тестовое задание REST-сервис на Python

Описание: [документ 1](https://yadi.sk/i/bE-gmumaIDcPGg), [документ 2](https://yadi.sk/i/dA9umaGbQdMNLw)

# Запуск сервера для разработки

(Автоматически запускает линтер и тесты)

```shell script
docker-compose up --build --abort-on-container-exit
```

Для очистки текущей базы данных используйте
```shell script
docker exec restapi_dev_1 python3 -m flask drop-db
```
, где restapi_dev_1 - имя контейнера с приложением
 