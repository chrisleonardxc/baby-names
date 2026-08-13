from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:////data/baby_names.db"
    cors_origins: str = "http://localhost:8060"

    person_a_key: str = "person_a"
    person_a_name: str = "Person A"
    person_b_key: str = "person_b"
    person_b_name: str = "Person B"

    site_password: str = "bingo"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
