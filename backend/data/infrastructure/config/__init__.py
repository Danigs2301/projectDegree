from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: Optional[str] = None

    MONGO_INITDB_ROOT_USERNAME: Optional[str] = None
    MONGO_INITDB_ROOT_PASSWORD: Optional[str] = None
    MONGO_HOST: Optional[str] = None
    MONGO_PORT: Optional[int] = None
    MONGO_DB: str

    @model_validator(mode="after")
    def build_mongo_uri(self):
        if not self.MONGO_URI:
            faltantes = [
                campo for campo in ("MONGO_INITDB_ROOT_USERNAME", "MONGO_INITDB_ROOT_PASSWORD", "MONGO_HOST", "MONGO_PORT")
                if getattr(self, campo) is None
            ]
            if faltantes:
                raise ValueError(
                    f"Define MONGO_URI directamente, o todas estas variables: {', '.join(faltantes)}"
                )
            self.MONGO_URI = (
                f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}"
                f":{self.MONGO_INITDB_ROOT_PASSWORD}"
                f"@{self.MONGO_HOST}:{self.MONGO_PORT}"
            )
        return self

    class Config:
        env_file = ".env"


settings = Settings()