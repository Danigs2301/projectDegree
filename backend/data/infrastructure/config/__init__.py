from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str

    @property
    def MONGO_URI(self) -> str:
        return (
            f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}"
            f":{self.MONGO_INITDB_ROOT_PASSWORD}"
            f"@{self.MONGO_HOST}:{self.MONGO_PORT}"
        )

    class Config:
        env_file = ".env"

settings = Settings()