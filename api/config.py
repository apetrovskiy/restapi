from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Конфигурирование доступно через переменные окружения
    """
    mongo_uri: str  # uri для подключения к mongodb
    mongo_dbname: str  # имя базы данных


settings = Settings()
